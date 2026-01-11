import httpx
import base64
import asyncio

# --- CONFIGURAÇÃO MANUAL ---
CERT_PATH = "/code/dashboard/backend/api/gateways/efi/credencial/certificado.pem"
CLIENT_ID = "Client_Id_497c00249fd13a6b4058e67cfc751d9ec6100775"
CLIENT_SECRET = "Client_Secret_cbd25e7acd2c42a6ef6745736a649e1b8743909e"
IS_SANDBOX = False
PIX_KEY = "5726ec81-0287-4657-b68d-90f6d9629b2e"
WEBHOOK_URL = "https://api.u9ttyt.easypanel.host/api/webhook/pix"
# ---------------------------

ENV_URL = "https://pix-h.api.efipay.com.br" if IS_SANDBOX else "https://pix.api.efipay.com.br"

async def ativar():
    print("🔌 Registrando Webhook na Efí (via httpx)...")
    
    # 1. Autenticação
    auth = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/json"
    }

    try:
        # Se for PEM, passamos direto. Se for P12, precisaria converter. 
        # Assumindo que o usuário tem o PEM aqui conforme o script original indicava.
        cert = CERT_PATH 
        
        async with httpx.AsyncClient(cert=cert, verify=False) as client: # verify=False se cert autoassinado
            print("🔑 Autenticando...")
            resp_auth = await client.post(
                f"{ENV_URL}/oauth/token",
                json={"grant_type": "client_credentials"},
                headers=headers,
                timeout=10.0
            )
            
            if resp_auth.status_code != 200:
                print(f"❌ Erro Auth: {resp_auth.text}")
                return

            token = resp_auth.json()["access_token"]
            print("✅ Token obtido!")

            # 2. Registrar Webhook
            # Endpoint: PUT /v2/webhook/:chave
            headers_wh = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "x-skip-mtls-checking": "true" # Importante
            }
            
            body = {
                "webhookUrl": WEBHOOK_URL
            }

            print(f"📡 Configurando webhook para chave: {PIX_KEY}")
            resp_wh = await client.put(
                f"{ENV_URL}/v2/webhook/{PIX_KEY}",
                json=body,
                headers=headers_wh,
                timeout=10.0
            )

            if resp_wh.status_code in [200, 201]:
                print("✅ Sucesso ao registrar!")
                print(resp_wh.json())
            else:
                print(f"❌ Erro ao registrar: {resp_wh.status_code} - {resp_wh.text}")

    except Exception as e:
        print(f"❌ Erro de conexão/certificado: {e}")
        print(f"Verifique se o arquivo existe: {CERT_PATH}")

if __name__ == "__main__":
    asyncio.run(ativar())
