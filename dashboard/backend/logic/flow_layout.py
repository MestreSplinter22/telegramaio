"""Módulo responsável por gerenciar o layout do ReactFlow para o editor de fluxos."""
import json
from typing import Dict, List, Any, Tuple, Set
import networkx as nx


def calculate_interactive_layout(
    full_flow: Dict[str, Any], 
    selected_screen_key: str = ""
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Calcula nós e arestas compatíveis com a estrutura do React Flow.
    Implementa layout bifurcado: nó raiz central, filhos divididos em esquerda/direita.
    """
    screens_raw = full_flow.get("screens", {})
    if not screens_raw: 
        return [], []

    screens = {str(k).strip(): v for k, v in screens_raw.items()}

    # 1. Construir Grafo e identificar conexões
    G = nx.DiGraph()
    temp_edges = []
    all_nodes_set = set(screens.keys())
    
    # Adicionar nós ao grafo
    for node_id in screens.keys():
        G.add_node(node_id)
    
    # Identificar arestas (edges) a partir dos callbacks
    for screen_id, content in screens.items():
        found_buttons = []
        stack = [content]
        
        # Buscar callbacks goto_*
        while stack:
            curr = stack.pop()
            if isinstance(curr, dict):
                if "callback" in curr and isinstance(curr["callback"], str) and curr["callback"].startswith("goto_"):
                    found_buttons.append(curr)
                for v in curr.values():
                    if isinstance(v, (dict, list)): 
                        stack.append(v)
            elif isinstance(curr, list):
                for item in curr: 
                    stack.append(item)
        
        # Criar arestas para botões
        for i, btn in enumerate(found_buttons):
            raw_target = btn["callback"].replace("goto_", "").strip()
            target = raw_target.split()[0] if raw_target else raw_target
            label = btn.get("text", "Próximo").strip()
            
            edge_id = f"e-{screen_id}-{target}-{i}"
            is_broken = target not in screens
            
            temp_edges.append({
                "id": edge_id,
                "source": screen_id,
                "target": target,
                "label": label,
                "animated": True,
                "style": {"stroke": "#ef4444", "strokeWidth": 2} if is_broken else {"stroke": "#94a3b8"},
                "labelStyle": {"fill": "#ef4444", "fontWeight": 700} if is_broken else {"fill": "#64748b"},
            })
            
            # Adicionar aresta ao grafo
            if not is_broken:
                G.add_edge(screen_id, target)
            if target not in all_nodes_set:
                all_nodes_set.add(target)
                G.add_node(target)
        
        # Buscar webhooks
        stack_for_webhook = [content]
        found_webhooks = []
        
        while stack_for_webhook:
            curr = stack_for_webhook.pop()
            if isinstance(curr, dict):
                if "webhook" in curr and isinstance(curr["webhook"], str):
                    found_webhooks.append(curr["webhook"])
                for v in curr.values():
                    if isinstance(v, (dict, list)): 
                        stack_for_webhook.append(v)
            elif isinstance(curr, list):
                for item in curr: 
                    stack_for_webhook.append(item)
        
        # Criar arestas para webhooks
        for i, webhook_target in enumerate(found_webhooks):
            if webhook_target and webhook_target in screens:
                edge_id = f"e-webhook-{screen_id}-{webhook_target}-{i}"
                
                temp_edges.append({
                    "id": edge_id,
                    "source": screen_id,
                    "target": webhook_target,
                    "label": "webhook",
                    "animated": True,
                    "style": {"stroke": "#10b981", "strokeWidth": 2},
                    "labelStyle": {"fill": "#059669", "fontWeight": 700},
                })
                
                G.add_edge(screen_id, webhook_target)
                if webhook_target not in all_nodes_set:
                    all_nodes_set.add(webhook_target)
                    G.add_node(webhook_target)

    # 2. Calcular layout bifurcado
    positions = calculate_bifurcated_layout(
        G, 
        node_width=250, 
        node_height=150, 
        x_gap=50, 
        y_gap=100,
        start_x=0,
        start_y=0
    )

    # 3. Converter posições para formato React Flow
    final_rf_nodes = []
    
    for node_id, pos in positions.items():
        is_selected = node_id == selected_screen_key
        is_missing = node_id not in screens
        
        # Estilização
        bg_color = "#1e293b" if is_selected else ("#fef2f2" if is_missing else "#ffffff")
        text_color = "white" if is_selected else ("#b91c1c" if is_missing else "black")
        border_color = "#3b82f6" if is_selected else ("#ef4444" if is_missing else "#cbd5e1")
        label_text = f"🚫 {node_id}" if is_missing else node_id
        
        final_rf_nodes.append({
            "id": node_id,
            "data": {"label": label_text},
            "position": {"x": pos["x"], "y": pos["y"]},
            "draggable": True,
            "style": {
                "background": bg_color,
                "color": text_color,
                "border": f"2px solid {border_color}",
                "borderRadius": "8px",
                "width": "200px",
                "padding": "10px",
                "fontSize": "12px",
                "fontWeight": "bold",
                "boxShadow": "0 4px 6px -1px rgb(0 0 0 / 0.1)"
            }
        })

    return final_rf_nodes, temp_edges


def calculate_bifurcated_layout(
    G: nx.DiGraph,
    node_width: int = 250,
    node_height: int = 150,
    x_gap: int = 50,
    y_gap: int = 100,
    start_x: int = 0,
    start_y: int = 0
) -> Dict[str, Dict[str, float]]:
    """
    Calcula um layout onde o nó raiz fica no centro e seus filhos se 
    espalham para a esquerda e para a direita.
    """
    if G.number_of_nodes() == 0:
        return {}

    # 1. Encontrar nó raiz (sem predecessores ou primeiro da lista)
    roots = [n for n, d in G.in_degree() if d == 0]
    root_id = roots[0] if roots else list(G.nodes())[0]

    # 2. Identificar os ramos principais (filhos imediatos da raiz)
    root_children = list(G.successors(root_id))
    
    # Dividir filhos: Metade para esquerda, metade para direita
    mid_point = (len(root_children) + 1) // 2
    left_branch_roots = root_children[:mid_point]
    right_branch_roots = root_children[mid_point:]

    # Dicionário final de posições
    positions = {root_id: {"x": start_x, "y": start_y}}

    # 3. Processar ramo da esquerda (direção = -1)
    if left_branch_roots:
        layout_branch(
            G, 
            left_branch_roots, 
            positions, 
            direction=-1,
            node_width=node_width,
            node_height=node_height,
            x_gap=x_gap,
            y_gap=y_gap
        )

    # 4. Processar ramo da direita (direção = 1)
    if right_branch_roots:
        layout_branch(
            G, 
            right_branch_roots, 
            positions, 
            direction=1,
            node_width=node_width,
            node_height=node_height,
            x_gap=x_gap,
            y_gap=y_gap
        )

    return positions


def layout_branch(
    G: nx.DiGraph,
    branch_roots: List[str],
    positions: Dict[str, Dict[str, float]],
    direction: int,
    node_width: int,
    node_height: int,
    x_gap: int,
    y_gap: int
):
    """
    Layout recursivo para um ramo específico.
    direction: 1 para direita, -1 para esquerda
    """
    # Para cada raiz neste ramo, calcular sua subárvore
    current_y_offset = -len(branch_roots) * (node_height + y_gap) / 2  # Centralizar verticalmente
    
    for root_node in branch_roots:
        # Calcular posição inicial
        depth = 0
        y_start = current_y_offset
        
        # Processar subárvore recursivamente
        _assign_positions_recursive(
            G, 
            root_node, 
            depth, 
            y_start,
            positions,
            direction,
            node_width,
            node_height,
            x_gap,
            y_gap
        )
        
        # Atualizar offset Y para próximo nó raiz
        subtree_height = _calculate_subtree_height(G, root_node, node_height, y_gap, set())
        current_y_offset += subtree_height + y_gap


def _assign_positions_recursive(
    G: nx.DiGraph,
    node_id: str,
    depth: int,
    y_pos: float,
    positions: Dict[str, Dict[str, float]],
    direction: int,
    node_width: int,
    node_height: int,
    x_gap: int,
    y_gap: int
):
    """Atribui posições recursivamente para todos os descendentes."""
    if node_id in positions:
        return
    
    # Calcular posição X (distância da raiz * direção)
    x_pos = (depth + 1) * (node_width + x_gap) * direction
    
    positions[node_id] = {"x": x_pos, "y": y_pos}
    
    # Processar filhos
    children = list(G.successors(node_id))
    if not children:
        return
    
    # Distribuir filhos verticalmente
    total_height = len(children) * (node_height + y_gap)
    start_y = y_pos - total_height / 2 + node_height / 2
    
    for i, child in enumerate(children):
        child_y = start_y + i * (node_height + y_gap)
        _assign_positions_recursive(
            G, 
            child, 
            depth + 1, 
            child_y,
            positions,
            direction,
            node_width,
            node_height,
            x_gap,
            y_gap
        )


def _calculate_subtree_height(
    G: nx.DiGraph,
    node_id: str,
    node_height: int,
    y_gap: int,
    visited: Set[str] = None
) -> float:
    """Calcula a altura total da subárvore enraizada em node_id.
    Protegido contra ciclos usando conjunto visited."""
    if visited is None:
        visited = set()
    
    # Proteção contra ciclos - se já visitamos este nó, retornar altura mínima
    if node_id in visited:
        return node_height
    
    visited.add(node_id)
    children = list(G.successors(node_id))
    
    if not children:
        visited.remove(node_id)  # Limpar para permitir reuso
        return node_height
    
    total_child_height = 0
    for child in children:
        # Passar o mesmo conjunto visited para manter rastreamento
        child_height = _calculate_subtree_height(G, child, node_height, y_gap, visited)
        total_child_height += child_height
    
    visited.remove(node_id)  # Limpar antes de retornar
    return max(node_height, total_child_height + (len(children) - 1) * y_gap)