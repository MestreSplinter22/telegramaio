# init_openpix.py
import reflex as rx
from dashboard.backend.models.models import GatewayConfig

def configurar_openpix():
    print("🔄 Atualizando configuração da OpenPix para SANDBOX...")
    
    with rx.session() as session:
        gw = session.query(GatewayConfig).filter(GatewayConfig.name == "openpix").first()
        
        if not gw:
            gw = GatewayConfig(name="openpix")
        
        gw.is_active = True
        
        # --- ATENÇÃO AQUI ---
        gw.is_sandbox = True  # Define como TRUE para usar a URL da Woovi Sandbox
        # --------------------

        gw.credentials = {
            "app_id": "Q2xpZW50X0lkXzgzNDMwZjRjLTQzY2EtNGZjZC1hMjhiLTZkYjZlODc5ZGI1YzpDbGllbnRfU2VjcmV0Xy9SL3c2MDhlMWd5UnRRUTlIQms0S2dqTDZHQitmQ0JlWWx2c1ZNZG04UnM9" 
        }
        
        session.add(gw)
        session.commit()
        print("✅ OpenPix configurada para modo SANDBOX com sucesso!")

if __name__ == "__main__":
    configurar_openpix()