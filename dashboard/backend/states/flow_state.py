import reflex as rx
import json
from typing import Dict, List, Any

from dashboard.backend.logic.flow_layout import calculate_interactive_layout
from dashboard.backend.services.flow_service import FlowService

class FlowState(rx.State):
    full_flow: Dict[str, Any] = {}
    screen_keys: List[str] = []
    selected_screen_key: str = ""
    
    # Editor Mode
    visual_editor_mode: bool = True
    editor_blocks: List[Dict[str, Any]] = [] 
    original_data_type: str = "dict"
    
    # Input Badge
    temp_badge_url: str = ""
    
    # Modal State
    is_add_modal_open: bool = False
    
    current_screen_content: str = ""
    new_screen_name: str = ""
    status_message: str = ""
    
    # --- REACT FLOW STATES ---
    # Substituímos graph_nodes e svg_content por estas listas
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []

    def set_temp_badge_url(self, value: str):
        self.temp_badge_url = value

    def toggle_add_modal(self):
        self.is_add_modal_open = not self.is_add_modal_open

    def add_payment_sequence(self):
        """
        Cria um par de nós conectados: Pagamento -> Sucesso
        """
        # Chama o serviço para adicionar a sequência de pagamento
        self.full_flow, payment_id, success_id, status_msg = FlowService.add_payment_sequence(self.full_flow)
        
        # Atualizar interface
        self.status_message = status_msg
        self.screen_keys = FlowService.get_screen_keys(self.full_flow)
        
        # Força o recálculo do gráfico para mostrar os novos nós e a aresta (edge)
        self.calculate_interactive_layout()
        
        # Seleciona o nó de pagamento para edição imediata
        self.select_screen(payment_id)
        
        self.is_add_modal_open = False

    # --- CARREGAMENTO ---
    def load_flow(self):
        # Carrega o fluxo usando o serviço
        self.full_flow = FlowService.load_flow()
        
        if "screens" in self.full_flow:
            self.screen_keys = FlowService.get_screen_keys(self.full_flow)
        
        if not self.selected_screen_key:
            initial = FlowService.get_initial_screen(self.full_flow)
            if initial and initial in self.screen_keys:
                self.select_screen(initial)
            elif self.screen_keys:
                self.select_screen(self.screen_keys[0])
        
        self.calculate_interactive_layout()

    def select_screen(self, key: str):
        self.selected_screen_key = key
        
        # Recupera dados ou cria padrão
        data = self.full_flow.get("screens", {}).get(key, {"text": "Nova Tela", "buttons": []})
        
        self.current_screen_content = json.dumps(data, indent=2, ensure_ascii=False)
        
        if isinstance(data, list):
            self.editor_blocks = data
            self.original_data_type = "list"
        else:
            self.editor_blocks = [data]
            self.original_data_type = "dict"
            
        # Recalcula o layout para atualizar o estilo do nó selecionado
        self.calculate_interactive_layout()

    # Evento de clique no Nó do ReactFlow
    def on_node_click(self, node_id: str):
        # Removemos a lógica de extração .get("id"), pois já é a string
        print(f"DEBUG: Clique no nó recebido: {node_id}") # Para você ver no terminal
        if node_id:
            self.select_screen(node_id)

    def add_new_screen(self):
        key = self.new_screen_name.strip()
        if not key: return
        self.select_screen(key)
        self.save_current_screen()
        self.new_screen_name = ""

    # --- EDITOR VISUAL (Mantido igual) ---
    def set_editor_mode(self, mode):
        # Converte a string "visual" ou "json" para booleano
        self.visual_editor_mode = (mode == "visual")
        
        # Se mudou para visual, carrega os blocos a partir do JSON atual
        if self.visual_editor_mode:
            try:
                data = json.loads(self.current_screen_content)
                if isinstance(data, list):
                    self.editor_blocks = data
                    self.original_data_type = "list"
                else:
                    self.editor_blocks = [data]
                    self.original_data_type = "dict"
            except:
                pass

    def add_block(self):
        self.editor_blocks.append({"text": "Nova mensagem...", "buttons": []})
        self.original_data_type = "list"

    def remove_block(self, index: int):
        if 0 <= index < len(self.editor_blocks):
            self.editor_blocks.pop(index)

    def update_block_text(self, index: int, text: str):
        if 0 <= index < len(self.editor_blocks):
            self.editor_blocks[index]["text"] = text

    def set_media_type(self, index: int, type: str):
        if 0 <= index < len(self.editor_blocks):
            block = self.editor_blocks[index]
            if "image_url" in block: del block["image_url"]
            if "video_url" in block: del block["video_url"]
            if type == "image": block["image_url"] = "https://..."
            elif type == "video": block["video_url"] = "https://..."
            self.editor_blocks[index] = block

    def update_media_url(self, index: int, key: str, value: str):
        if 0 <= index < len(self.editor_blocks):
            self.editor_blocks[index][key] = value

    def insert_badge(self, index: int):
        if not self.temp_badge_url: return
        if 0 <= index < len(self.editor_blocks):
            current_text = self.editor_blocks[index].get("text", "")
            badge_html = f"<a href='{self.temp_badge_url}'>&#8205;</a>"
            self.editor_blocks[index]["text"] = badge_html + current_text
            self.temp_badge_url = ""

    def add_button_row(self, block_index: int):
        if 0 <= block_index < len(self.editor_blocks):
            block = self.editor_blocks[block_index]
            if "buttons" not in block: block["buttons"] = []
            block["buttons"].append([{"text": "Novo Botão", "callback": "goto_..."}])
            self.editor_blocks[block_index] = block

    def add_button_to_row(self, block_index: int, row_index: int):
        if 0 <= block_index < len(self.editor_blocks):
            buttons = self.editor_blocks[block_index].get("buttons", [])
            if 0 <= row_index < len(buttons):
                buttons[row_index].append({"text": "Novo Botão", "callback": "goto_..."})

    def remove_button(self, block_index: int, row_index: int, btn_index: int):
        if 0 <= block_index < len(self.editor_blocks):
            buttons = self.editor_blocks[block_index].get("buttons", [])
            if 0 <= row_index < len(buttons):
                if 0 <= btn_index < len(buttons[row_index]):
                    buttons[row_index].pop(btn_index)
                    if not buttons[row_index]:
                        buttons.pop(row_index)

    def update_button(self, block_idx: int, row_idx: int, btn_idx: int, field: str, value: str):
        if 0 <= block_idx < len(self.editor_blocks):
            btn = self.editor_blocks[block_idx]["buttons"][row_idx][btn_idx]
            if field == "type":
                if value == "url":
                    if "callback" in btn: del btn["callback"]
                    btn["url"] = "https://..."
                else:
                    if "url" in btn: del btn["url"]
                    btn["callback"] = "goto_..."
            else:
                btn[field] = value
            self.editor_blocks[block_idx]["buttons"][row_idx][btn_idx] = btn

    def save_visual_changes(self):
        final_data = self.editor_blocks
        if len(self.editor_blocks) == 1 and self.original_data_type == "dict":
            final_data = self.editor_blocks[0]
        self.current_screen_content = json.dumps(final_data, indent=2, ensure_ascii=False)
        self.save_current_screen()

    def update_content(self, new_content: str):
        self.current_screen_content = new_content

    def set_new_screen_name(self, value: str):
        self.new_screen_name = value

    def save_current_screen(self):
        # --- CORREÇÃO: Sincronização do Modo Visual ---
        # Se estiver no modo visual, atualizamos o texto JSON (current_screen_content)
        # com base nos blocos editados (editor_blocks) antes de prosseguir.
        if self.visual_editor_mode:
            final_data = self.editor_blocks
            # Se originalmente era um dicionário único e continua com 1 bloco, salva como dict
            if len(self.editor_blocks) == 1 and self.original_data_type == "dict":
                final_data = self.editor_blocks[0]
            
            self.current_screen_content = json.dumps(final_data, indent=2, ensure_ascii=False)
        # -----------------------------------------------

        # Chama o serviço para salvar a tela
        self.full_flow, status_msg = FlowService.save_screen(self.full_flow, self.selected_screen_key, self.current_screen_content)
        
        self.status_message = status_msg
        
        if "✅" in status_msg:  # Se salvou com sucesso
            self.screen_keys = FlowService.get_screen_keys(self.full_flow)
            self.calculate_interactive_layout()
            
            # Se salvou via modo texto, atualiza os blocos visuais para não quebrar se trocar de aba
            try:
                new_data = json.loads(self.current_screen_content)
                if not self.visual_editor_mode:
                    if isinstance(new_data, list):
                        self.editor_blocks = new_data
                        self.original_data_type = "list"
                    else:
                        self.editor_blocks = [new_data]
                        self.original_data_type = "dict"
            except json.JSONDecodeError:
                pass  # Não faz nada se o JSON for inválido

    # --- NOVO LAYOUT PARA REACT FLOW ---
    def calculate_interactive_layout(self):
        """
        Calcula nós e arestas compatíveis com a estrutura do React Flow.
        """
        self.nodes, self.edges = calculate_interactive_layout(self.full_flow, self.selected_screen_key)