# dashboard/backend/gateways/openpix_service.py

import httpx
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
            self.base_url = "https://api.openpix.com.br/api/v1"
        else:
            self.base_url = "https://api.openpix.com.br/api/v1"

    def get_headers(self):
        return {
            "Authorization": self.app_id,
            "Content-Type": "application/json"
        }

    async def create_charge_async(self, txid: str, nome: str, valor: float, cpf: Optional[str] = None, email: str = "cliente@sememail.com"):
        """
        Cria cobrança de forma ASSÍNCRONA usando httpx.
        """
        valor_centavos = int(valor * 100)
        url = f"{self.base_url}/charge"
        
        customer_data = {"name": nome}
        if cpf:
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
            print(f"🚀 Enviando para OpenPix (Async): {json.dumps(payload)}")
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=self.get_headers(), json=payload, timeout=30.0)
                response.raise_for_status()
                data = response.json()
            
            charge = data.get("charge", {})
            return {
                "pix_copia_cola": charge.get("brCode"),
                "qrcode_base64": charge.get("qrCodeImage"),
                "txid": charge.get("correlationID")
            }

        except Exception as e:
            print(f"❌ Erro OpenPix Async: {e}")
            raise Exception(f"Falha OpenPix Async: {str(e)}")
