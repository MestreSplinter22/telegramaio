"""Módulo de serviço para gerenciamento de fluxos de telas."""
import json
import os
import uuid
from typing import Dict, List, Any


FLOW_FILE_PATH = "dashboard/backend/telegram/flows/start_flow.json"


class FlowService:
    """Classe de serviço para operações relacionadas ao fluxo de telas."""
    
    @staticmethod
    def load_flow() -> Dict[str, Any]:
        """Carrega o fluxo do arquivo JSON."""
        if os.path.exists(FLOW_FILE_PATH):
            try:
                with open(FLOW_FILE_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erro ao carregar o fluxo: {e}")
                return {}
        return {}
    
    @staticmethod
    def save_flow(full_flow: Dict[str, Any]) -> bool:
        """Salva o fluxo no arquivo JSON."""
        try:
            with open(FLOW_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(full_flow, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erro ao salvar o fluxo: {e}")
            return False
    
    @staticmethod
    def add_payment_sequence(full_flow: Dict[str, Any]) -> tuple:
        """
        Cria um par de telas de pagamento conectadas: Pagamento -> Sucesso
        Retorna (novo_full_flow, payment_id, success_id, mensagem_status)
        """
        # 1. Gerar IDs únicos curtos
        payment_id = f"pay_{uuid.uuid4().hex[:4]}"
        success_id = f"success_{uuid.uuid4().hex[:4]}"

        # 2. Definir os dados das telas seguindo o seu padrão JSON
        payment_data = {
            "type": "payment",
            "text": "💳 *Pagamento Pendente*\n\nPor favor, realize o pagamento de **R$ {amount}** usando o botão abaixo.\n\n {pix_copia_cola}",
            "amount": 10.00,
            "gateway": "openpix",
            "buttons": [[{
                "text": "✅ Já realizei o pagamento",
                "callback": f"goto_{success_id}"
            }]]
        }

        success_data = {
            "text": "🎉 *Pagamento de **R$ {amount}** Confirmado!*\n\nO Canal Vip foi liberado com sucesso.",
            "buttons": []
        }

        # 3. Inserir no dicionário global
        if "screens" not in full_flow:
            full_flow["screens"] = {}
        
        full_flow["screens"][payment_id] = payment_data
        full_flow["screens"][success_id] = success_data

        # 4. Persistir no arquivo JSON
        success = FlowService.save_flow(full_flow)
        
        if success:
            return full_flow, payment_id, success_id, "✅ Sequência de pagamento criada!"
        else:
            return full_flow, payment_id, success_id, f"❌ Erro ao criar sequência: Falha ao salvar o arquivo"
    
    @staticmethod
    def save_screen(full_flow: Dict[str, Any], screen_key: str, screen_content: str) -> tuple:
        """
        Salva uma tela específica no fluxo.
        Retorna (novo_full_flow, mensagem_status)
        """
        try:
            # Converte o conteúdo JSON em objeto Python
            new_data = json.loads(screen_content)
            
            if "screens" not in full_flow: 
                full_flow["screens"] = {}
            full_flow["screens"][screen_key] = new_data
            
            success = FlowService.save_flow(full_flow)
            
            if success:
                return full_flow, "✅ Salvo com sucesso!"
            else:
                return full_flow, "❌ Erro ao salvar no arquivo"
                
        except json.JSONDecodeError:
            return full_flow, "❌ JSON Inválido. Corrija o texto antes de salvar."
        except Exception as e:
            return full_flow, f"❌ Erro ao salvar: {e}"
    
    @staticmethod
    def get_screen_keys(full_flow: Dict[str, Any]) -> List[str]:
        """Obtém as chaves das telas ordenadas."""
        if "screens" in full_flow:
            return sorted(list(full_flow["screens"].keys()))
        return []
    
    @staticmethod
    def get_initial_screen(full_flow: Dict[str, Any]) -> str:
        """Obtém a tela inicial do fluxo."""
        return full_flow.get("initial_screen", "")