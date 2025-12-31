# dashboard/backend/gateways/openpix_service.py

import requests
import json
from typing import Optional
from dashboard.backend.models import GatewayConfig

class OpenPixService:
    def __init__(self, config: GatewayConfig):
        self.config = config
        self.creds = config.credentials
        self.app_id = self.creds.get("app_id")
        
        # URL Base (Sandbox ou Produção)
        if config.is_sandbox:
            self.base_url = "https://api.woovi-sandbox.com/api/v1"
        else:
            self.base_url = "https://api.openpix.com.br/api/v1"

    def get_headers(self):
        return {
            "Authorization": self.app_id,
            "Content-Type": "application/json"
        }

    def create_charge(self, txid: str, nome: str, valor: float, cpf: Optional[str] = None, email: str = "cliente@sememail.com"):
        """
        Cria cobrança. CPF é opcional.
        Se não houver CPF, usamos Nome + Email para validar o customer (regra da OpenPix).
        """
        valor_centavos = int(valor * 100)
        url = f"{self.base_url}/charge"
        
        # Monta o objeto customer dinamicamente
        customer_data = {"name": nome}
        
        # Regra OpenPix: Precisa de (Nome + CPF) OU (Nome + Email) OU (Nome + Telefone)
        if cpf:
            # Apenas limpa se o CPF foi fornecido
            customer_data["taxID"] = "".join(filter(str.isdigit, cpf))
        
        if email:
            customer_data["email"] = email

        payload = {
            "correlationID": txid,
            "value": valor_centavos,
            "comment": f"Pgto {nome}",
            "customer": customer_data
        }

        try:
            print(f"🚀 Enviando para OpenPix: {json.dumps(payload)}")
            response = requests.post(url, headers=self.get_headers(), json=payload)
            response.raise_for_status()
            
            data = response.json()
            charge = data.get("charge", {})
            
            return {
                "pix_copia_cola": charge.get("brCode"),
                "qrcode_base64": charge.get("qrCodeImage"),
                "txid": charge.get("correlationID")
            }

        except Exception as e:
            print(f"❌ Erro OpenPix: {e}")
            if 'response' in locals():
                print(f"Detalhe: {response.text}")
            raise Exception(f"Falha OpenPix: {str(e)}")