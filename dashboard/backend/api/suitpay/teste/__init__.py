"""
SuitPay Integration Endpoint.
Este módulo registra a rota para gerar um PIX de teste hardcoded.
"""

from fastapi import FastAPI, HTTPException
import httpx
import uuid
from datetime import datetime, timedelta

# Configurações Hardcoded (Rascunho)
SUITPAY_HOST = "https://ws.suitpay.app" # URL de Produção baseada nas credenciais
# SUITPAY_HOST = "https://sandbox.ws.suitpay.app" # URL Sandbox (caso as credenciais sejam de teste)

CREDENTIALS = {
    "ci": "dege22_1754575850408",
    "cs": "e6ccf0bbf506ac0bd1f0941b7ceef96d376e5679d906a916ea1f18080160227d85c41fc49dc642ab86b82341c3e67702"
}

def register_suitpay_routes(app: FastAPI):
    """Registra as rotas da SuitPay no app principal do Reflex."""

    @app.get("/api/suitpay/teste-pix")
    async def gerar_pix_teste():
        """
        Gera um QR Code PIX de teste com dados hardcoded.
        Retorna a resposta bruta da SuitPay.
        """
        
        # 1. Definir o Endpoint de Solicitação de QR Code
        # Baseado na documentação padrão da SuitPay para Gateway
        url = f"{SUITPAY_HOST}/api/v1/gateway/request-qrcode"

        # 2. Dados do Pedido (Hardcoded para teste)
        # Gera um ID único para cada teste para não dar erro de duplicidade
        request_id = str(uuid.uuid4())
        data_vencimento = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        payload = {
            "requestNumber": request_id,
            "dueDate": data_vencimento,
            "amount": 0.50,  # Valor de teste (R$ 0,50)
            "shippingAmount": 0.0,
            "usernameCheckout": "checkout",
            "callbackUrl": "https://seu-site.com/api/webhook/suitpay", # URL Fictícia
            "client": {
                "name": "Cliente Teste Hardcoded",
                "document": "13592187775", # CPF Fictício de teste (pode precisar ser um CPF válido dependendo da validação deles)
                "email": "teste@email.com",
                "phoneNumber": "11999999999"
            }
        }

        # 3. Headers de Autenticação (CI e CS conforme documentação)
        headers = {
            "Content-Type": "application/json",
            "ci": CREDENTIALS["ci"],
            "cs": CREDENTIALS["cs"]
        }

        # 4. Envio da Requisição
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, headers=headers, timeout=30.0)
                
                # Se a resposta for sucesso (200), retorna o JSON do PIX
                if response.status_code == 200:
                    return {
                        "status": "success",
                        "suitpay_response": response.json(),
                        "debug_info": {
                            "request_number": request_id,
                            "amount": 0.50
                        }
                    }
                else:
                    # Retorna erro formatado se falhar
                    return {
                        "status": "error",
                        "status_code": response.status_code,
                        "response_body": response.text
                    }

            except Exception as e:
                return {"status": "exception", "error": str(e)}