"""Módulo responsável por gerenciar o layout do ReactFlow para o editor de fluxos."""
import networkx as nx
from typing import Dict, List, Any, Tuple, Set

def calculate_interactive_layout(
    full_flow: Dict[str, Any], 
    selected_screen_key: str = ""
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Calcula nós e arestas compatíveis com a estrutura do React Flow usando Layout Hierárquico.
    Configuração: Z-Index Dinâmico baseado em geometria para evitar sobreposições de linhas.
    """
    screens_raw = full_flow.get("screens", {})
    if not screens_raw: 
        return [], []

    screens = {str(k).strip(): v for k, v in screens_raw.items()}

    # 1. Construir Grafo
    G = nx.DiGraph()
    temp_edges = []
    all_nodes_set = set(screens.keys())
    
    for node_id in screens.keys():
        G.add_node(node_id)
    
    # Processar botões e webhooks para criar arestas preliminares
    for screen_id, content in screens.items():
        # --- Lógica de extração de botões ---
        found_buttons = []
        stack = [content]
        while stack:
            curr = stack.pop()
            if isinstance(curr, dict):
                if "callback" in curr and isinstance(curr["callback"], str) and curr["callback"].startswith("goto_"):
                    found_buttons.append(curr)
                for v in curr.values():
                    if isinstance(v, (dict, list)): stack.append(v)
            elif isinstance(curr, list):
                for item in curr: stack.append(item)
        
        for i, btn in enumerate(found_buttons):
            raw_target = btn["callback"].replace("goto_", "").strip()
            target = raw_target.split()[0] if raw_target else raw_target
            label = btn.get("text", "Próximo").strip()
            edge_id = f"e-{screen_id}-{target}-{i}"
            is_broken = target not in screens
            
            edge_style = {"stroke": "#ef4444", "strokeWidth": 2} if is_broken else {"stroke": "#94a3b8"}
            
            temp_edges.append({
                "id": edge_id,
                "source": screen_id,
                "target": target,
                "label": label,
                "type": "smoothstep", 
                "pathOptions": {"borderRadius": 20},
                "animated": False,
                # Categoria de base para ordenação (Botões > Linhas > Back-edges)
                "_category": 2, 
                "style": edge_style,
                "labelStyle": {
                    "fill": "#ef4444" if is_broken else "#64748b",
                    "fontWeight": 700,
                    "fontSize": "11px"
                },
                "labelShowBg": True,
                "labelBgStyle": {"fill": "#ffffff", "fillOpacity": 1, "rx": 4, "ry": 4},
                "labelBgPadding": [8, 4], # Padding extra para limpar a área
            })
            if not is_broken: G.add_edge(screen_id, target)
            if target not in all_nodes_set: 
                all_nodes_set.add(target); G.add_node(target)

        # --- Lógica de extração de Webhooks ---
        stack_wh = [content]
        found_wh = []
        while stack_wh:
            curr = stack_wh.pop()
            if isinstance(curr, dict):
                if "webhook" in curr and isinstance(curr["webhook"], str): found_wh.append(curr["webhook"])
                for v in curr.values():
                    if isinstance(v, (dict, list)): stack_wh.append(v)
            elif isinstance(curr, list):
                for item in curr: stack_wh.append(item)

        for i, wh_target in enumerate(found_wh):
            if wh_target and wh_target in screens:
                edge_id = f"e-wh-{screen_id}-{wh_target}-{i}"
                temp_edges.append({
                    "id": edge_id, 
                    "source": screen_id, 
                    "target": wh_target, 
                    "label": "Webhook",
                    "type": "smoothstep",
                    "pathOptions": {"borderRadius": 20},
                    "animated": True,
                    "_category": 1, # Categoria média
                    "zIndex": 0,
                    "style": {"stroke": "#10b981", "strokeDasharray": "5,5"},
                    "labelShowBg": True,
                    "labelBgStyle": {"fill": "#ffffff", "fillOpacity": 0.8},
                })
                G.add_edge(screen_id, wh_target)
                if wh_target not in all_nodes_set: 
                    all_nodes_set.add(wh_target); G.add_node(wh_target)

    # 2. Calcular Layout Hierárquico Vertical
    positions = calculate_hierarchical_layout(
        G, 
        direction='TB', 
        node_width=250, 
        node_height=180,
        x_gap=50,       
        y_gap=130       
    )

    # 3. Pós-Processamento e Atribuição de Z-Index Dinâmico
    for edge in temp_edges:
        # Ignorar webhooks e links quebrados para cálculo geométrico
        if edge.get("label") == "Webhook" or edge["style"].get("stroke") == "#ef4444":
            continue

        src = edge["source"]
        tgt = edge["target"]

        if src in positions and tgt in positions:
            src_pos = positions[src]
            tgt_pos = positions[tgt]

            # Distância horizontal absoluta (quão "larga" é a dobradiça)
            dist_x = abs(src_pos["x"] - tgt_pos["x"])

            # --- CASO 1: RETORNO (Back-Edge) ---
            # Se destino está acima ou na mesma linha
            if tgt_pos["y"] <= src_pos["y"]:
                edge["_category"] = 0 # Prioridade Mínima
                edge["zIndex"] = -10
                
                back_edge_color = "rgba(59, 130, 246, 0.6)"
                edge["style"] = {
                    "stroke": back_edge_color,
                    "strokeWidth": 2,
                    "strokeDasharray": "5, 5",
                }
                edge["animated"] = True 
                edge["markerEnd"] = {
                    "type": "arrowclosed",
                    "color": back_edge_color,
                    "width": 20,
                    "height": 20,
                }
                edge["label"] = "▲" 
                edge["labelStyle"] = {
                    "fill": "rgba(59, 130, 246, 1)", 
                    "fontWeight": "900",
                    "fontSize": "24px",
                    "filter": "drop-shadow(0px 2px 2px rgba(0,0,0,0.1))"
                }
                edge["labelBgStyle"] = {"fill": "rgba(255, 255, 255, 0.85)", "rx": 5, "ry": 5}
                edge["labelBgPadding"] = [4, 4]
                edge["labelShowBg"] = True
            
            # --- CASO 2: BOTÃO NORMAL (Ida) ---
            else:
                # LÓGICA DE OURO: 
                # Quanto menor a distância horizontal, MAIOR o z-index.
                # Isso faz com que linhas retas (dist_x ~ 0) fiquem POR CIMA das linhas curvas.
                # Base zIndex para botões = 100.
                # Subtraímos um fator da distância.
                
                # Normaliza distância para não ficar negativo (ex: max width ~ 2000)
                priority_score = 1000 - int(dist_x)
                
                edge["zIndex"] = priority_score
                edge["_sort_key"] = priority_score # Usado para ordenação da lista
                
                # Categoria alta para garantir que ganhe de webhooks
                edge["_category"] = 3 

    # 4. ORDENAÇÃO DA LISTA DE ARESTAS (Painter's Algorithm)
    # Ordenamos a lista para que o React desenhe na ordem correta:
    # 1. Back-edges (Fundo)
    # 2. Webhooks (Meio)
    # 3. Botões Largos (Meio-Topo - as dobradiças ficam atrás)
    # 4. Botões Retos (Topo Absoluto - os labels ficam visíveis)
    
    temp_edges.sort(key=lambda x: (
        x.get("_category", 0),  # Primeiro por categoria
        x.get("_sort_key", 0)   # Depois por prioridade geométrica (Retos > Largos)
    ))

    # 5. Converter para nós do React Flow
    final_rf_nodes = []
    for node_id, pos in positions.items():
        is_selected = node_id == selected_screen_key
        is_missing = node_id not in screens
        
        bg_color = "#1e293b" if is_selected else ("#fef2f2" if is_missing else "#ffffff")
        text_color = "white" if is_selected else ("#b91c1c" if is_missing else "#1e293b")
        border_color = "#3b82f6" if is_selected else ("#ef4444" if is_missing else "#cbd5e1")
        
        final_rf_nodes.append({
            "id": node_id,
            "data": {"label": f"🚫 {node_id}" if is_missing else node_id},
            "position": {"x": pos["x"], "y": pos["y"]},
            "targetPosition": "top",
            "sourcePosition": "bottom",
            "draggable": True,
            # Z-INDEX 2000: Garante que o CARD cubra qualquer aresta, mesmo as de alta prioridade
            "zIndex": 2000, 
            "style": {
                "background": bg_color,
                "color": text_color,
                "border": f"1px solid {border_color}",
                "borderRadius": "8px",
                "width": "240px",
                "padding": "12px",
                "fontSize": "13px",
                "fontWeight": "600",
                "boxShadow": "0 4px 6px -1px rgb(0 0 0 / 0.05)"
            }
        })

    return final_rf_nodes, temp_edges


def calculate_hierarchical_layout(
    G: nx.DiGraph, 
    direction: str = 'TB', 
    node_width: int = 250, 
    node_height: int = 150,
    x_gap: int = 50,
    y_gap: int = 80
) -> Dict[str, Dict[str, float]]:
    """
    Algoritmo de layout de árvore compacto (Vertical).
    """
    positions = {}
    
    roots = [n for n, d in G.in_degree() if d == 0]
    remaining_nodes = set(G.nodes())
    
    if not roots and remaining_nodes:
        roots = [next(iter(remaining_nodes))]

    visiting = set()

    def layout_subtree(node, depth, current_pos_start):
        if node in positions: return 0 
        if node in visiting: return 0 

        visiting.add(node)

        children = list(G.successors(node))
        
        if not children:
            if direction == 'LR':
                positions[node] = {"x": depth * (node_width + x_gap), "y": current_pos_start}
            else: # TB
                positions[node] = {"x": current_pos_start, "y": depth * (node_height + y_gap)}
            
            visiting.remove(node)
            return (node_width + x_gap) if direction == 'TB' else (node_height + y_gap)

        total_children_span = 0
        child_cursor = current_pos_start
        
        first_child_pos = None
        last_child_pos = None
        
        for i, child in enumerate(children):
            span = layout_subtree(child, depth + 1, child_cursor)
            
            if child in positions:
                c_pos = positions[child]["x"] if direction == 'TB' else positions[child]["y"]
                if first_child_pos is None: first_child_pos = c_pos
                last_child_pos = c_pos
            
            child_cursor += span
            total_children_span += span
        
        if first_child_pos is not None and last_child_pos is not None:
            center_pos = (first_child_pos + last_child_pos) / 2
        else:
            center_pos = current_pos_start

        if direction == 'LR':
            positions[node] = {"x": depth * (node_width + x_gap), "y": center_pos}
        else: # TB
            positions[node] = {"x": center_pos, "y": depth * (node_height + y_gap)}
            
        visiting.remove(node)
        
        dimension_span = (node_width + x_gap) if direction == 'TB' else (node_height + y_gap)
        return max(dimension_span, total_children_span)

    current_tree_pos = 0
    roots.sort(key=lambda x: str(x))
    
    for root in roots:
        tree_span = layout_subtree(root, 0, current_tree_pos)
        current_tree_pos += tree_span + 50 

    remaining = set(G.nodes()) - set(positions.keys())
    if remaining:
        for node in remaining:
             if direction == 'TB':
                positions[node] = {"x": current_tree_pos, "y": 0}
                current_tree_pos += node_width + x_gap
             else:
                positions[node] = {"x": 0, "y": current_tree_pos}
                current_tree_pos += node_height + y_gap

    return positions