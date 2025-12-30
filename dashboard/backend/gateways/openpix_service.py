# dashboard/backend/gateways/openpix_service.py

import requests
import json
from dashboard.backend.models.models import GatewayConfig

class OpenPixService:
    def __init__(self, config: GatewayConfig):
        self.config = config
        self.creds = config.credentials
        self.app_id = self.creds.get("app_id")
        
        # --- CORREÇÃO DA URL BASE ---
        # Se for Sandbox (app.woovi-sandbox.com), usa a API da Woovi Sandbox
        # Se for Produção (app.openpix.com.br), usa a API da OpenPix
        if config.is_sandbox:
            self.base_url = "https://api.woovi-sandbox.com/api/v1"
        else:
            self.base_url = "https://api.openpix.com.br/api/v1"

    def get_headers(self):
        # O Header é apenas o AppID, sem "Bearer"
        return {
            "Authorization": self.app_id,
            "Content-Type": "application/json"
        }

    def create_charge(self, txid: str, nome: str, cpf: str, valor: float):
        """
        Cria uma cobrança Pix imediata na OpenPix/Woovi.
        """
        # OpenPix trabalha com valor em centavos (Integer)
        valor_centavos = int(valor * 100)
        
        url = f"{self.base_url}/charge"
        
        payload = {
            "correlationID": txid,
            "value": valor_centavos,
            "comment": f"Pgto {nome}",
            "customer": {
                "name": nome,
                "taxID": cpf
            }
        }

        try:
            print(f"🚀 Enviando para OpenPix ({'SANDBOX' if self.config.is_sandbox else 'PROD'}): {url}")
            response = requests.post(url, headers=self.get_headers(), json=payload)
            response.raise_for_status() 
            
            data = response.json()
            charge = data.get("charge", {})
            
            # Recupera dados para exibição
            br_code = charge.get("brCode") # Pix Copia e Cola
            qr_code_image = charge.get("qrCodeImage") 
            
            return {
                "pix_copia_cola": br_code,
                "qrcode_base64": qr_code_image,
                "txid": charge.get("correlationID")
            }

        except Exception as e:
            print(f"❌ Erro OpenPix Create: {e}")
            if 'response' in locals():
                print(f"Detalhe: {response.text}")
            raise Exception(f"Falha na API OpenPix ({response.status_code}): {response.text}")