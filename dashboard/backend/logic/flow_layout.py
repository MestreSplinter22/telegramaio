"""Módulo responsável por gerenciar o layout do ReactFlow para o editor de fluxos."""
import json
from typing import Dict, List, Any, Tuple, Set


def calculate_interactive_layout(
    full_flow: Dict[str, Any], 
    selected_screen_key: str = ""
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Calcula nós e arestas compatíveis com a estrutura do React Flow.
    Mantém a lógica de BFS para distribuir as posições X e Y.
    """
    screens_raw = full_flow.get("screens", {})
    if not screens_raw: 
        return [], []

    screens = {str(k).strip(): v for k, v in screens_raw.items()}

    # Dimensões para cálculo de posição (Grid)
    NODE_WIDTH = 250
    NODE_HEIGHT = 150 
    GAP_X = 50
    GAP_Y = 100
    START_X = 100
    START_Y = 50

    # Listas temporárias
    temp_edges = []
    adjacency = {} 
    all_nodes_set = set(screens.keys())
    
    # 1. Identificar Conexões (Edges)
    for screen_id, content in screens.items():
        if screen_id not in adjacency: 
            adjacency[screen_id] = []
        
        found_buttons = []
        stack = [content]
        
        # Varredura profunda por botões
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
        
        # Criar Edges
        for i, btn in enumerate(found_buttons):
            raw_target = btn["callback"].replace("goto_", "").strip()
            target = raw_target.split()[0] if raw_target else raw_target
            label = btn.get("text", "Próximo").strip()
            
            # Edge ID único
            edge_id = f"e-{screen_id}-{target}-{i}"
            
            # Verifica se o target existe (Link Quebrado)
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
            
            adjacency[screen_id].append(target)
            if target not in all_nodes_set:
                all_nodes_set.add(target)

    # 2. Algoritmo BFS para Níveis (Layout Hierárquico)
    start_node = full_flow.get("initial_screen", "").strip()
    if start_node not in screens and screens: 
        start_node = next(iter(screens))

    levels = {}
    queue = [(start_node, 0)]
    visited: Set[str] = set()

    while queue:
        current, level = queue.pop(0)
        if current in visited: 
            continue
        visited.add(current)
        levels[current] = level
        for child in adjacency.get(current, []): 
            queue.append((child, level + 1))

    # Adicionar nós órfãos no nível 1
    for node in all_nodes_set:
        if node not in visited: 
            levels[node] = 1

    nodes_by_level = {}
    for node, level in levels.items():
        if level not in nodes_by_level: 
            nodes_by_level[level] = []
        nodes_by_level[level].append(node)

    # 3. Construir Nós do ReactFlow
    final_rf_nodes = []
    
    for level, level_nodes in nodes_by_level.items():
        # Centralizar a linha horizontalmente
        row_width = len(level_nodes) * (NODE_WIDTH + GAP_X)
        start_x_level = START_X # Você pode centralizar dinamicamente se quiser
        
        for i, node_id in enumerate(level_nodes):
            x = start_x_level + (i * (NODE_WIDTH + GAP_X))
            y = START_Y + (level * (NODE_HEIGHT + GAP_Y))
            
            is_selected = node_id == selected_screen_key
            is_missing = node_id not in screens
            
            # Estilização baseada em estado
            bg_color = "#1e293b" if is_selected else ("#fef2f2" if is_missing else "#ffffff")
            text_color = "white" if is_selected else ("#b91c1c" if is_missing else "black")
            border_color = "#3b82f6" if is_selected else ("#ef4444" if is_missing else "#cbd5e1")
            
            # Label com indicador
            label_text = f"🚫 {node_id}" if is_missing else node_id
            
            final_rf_nodes.append({
                "id": node_id,
                "data": {"label": label_text},
                "position": {"x": x, "y": y},
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