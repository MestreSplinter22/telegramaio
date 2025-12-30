# init_gateway.py
import reflex as rx
from sqlmodel import select
from dashboard.backend.models.models import GatewayConfig

def init_efi_config():
    # Dados fornecidos
    CLIENT_ID = "Client_Id_497c00249fd13a6b4058e67cfc751d9ec6100775"
    CLIENT_SECRET = "Client_Secret_cbd25e7acd2c42a6ef6745736a649e1b8743909e"
    CERT_PATH = "dashboard/backend/api/gateways/efi/credencial/producao.p12"
    
    # --- IMPORTANTE: COLOQUE SUA CHAVE PIX ABAIXO ---
    PIX_KEY = "5726ec81-0287-4657-b68d-90f6d9629b2e" 
    # ------------------------------------------------

    print("🔌 Conectando ao banco de dados...")
    
    with rx.session() as session:
        # Verifica se já existe a configuração
        statement = select(GatewayConfig).where(GatewayConfig.name == "efi_bank")
        gateway = session.exec(statement).first()

        # Estrutura das credenciais (JSON)
        creds_data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "certificate_path": CERT_PATH,
            "certificate_password": "", # Senha vazia conforme padrão Efí
            "pix_key": PIX_KEY
        }

        # Configurações extras (URLs, limites, etc)
        config_data = {
            "webhook_url": "/api/payment/webhook/efi",
            "min_amount": 1.00
        }

        if gateway:
            print("🔄 Atualizando configuração existente da Efí Bank...")
            gateway.credentials = creds_data
            gateway.config = config_data
            gateway.is_active = True
            gateway.is_sandbox = True # True = Homologação
        else:
            print("✨ Criando nova configuração da Efí Bank...")
            gateway = GatewayConfig(
                name="efi_bank",
                is_active=True,
                is_sandbox=True, # True = Homologação
                credentials=creds_data,
                config=config_data
            )
            session.add(gateway)
        
        session.commit()
        session.refresh(gateway)
        print(f"✅ Configuração salva com sucesso! ID: {gateway.id}")
        print(f"📂 Certificado configurado em: {gateway.credentials['certificate_path']}")

if __name__ == "__main__":
    init_efi_config()