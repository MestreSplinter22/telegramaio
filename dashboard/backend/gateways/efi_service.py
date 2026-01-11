# dashboard/backend/gateways/efi_service.py

import os
import base64
import httpx
import json
import tempfile
import unicodedata
import re
from contextlib import contextmanager
from cryptography.hazmat.primitives.serialization import pkcs12, Encoding, PrivateFormat, NoEncryption
from dashboard.backend.models import GatewayConfig

class EfiPixService:
    def __init__(self, config: GatewayConfig):
        self.config = config
        self.creds = config.credentials
        # Define URL base (Produção ou Homologação)
        self.env_url = "https://pix-h.api.efipay.com.br" if config.is_sandbox else "https://pix.api.efipay.com.br"
        
    def sanitize_string(self, text: str) -> str:
        """
        Remove formatações especiais (Negrito, Itálico, Emojis) e caracteres não bancários.
        Converte '𝙈𝙚𝙨𝙩𝙧𝙚' para 'Mestre'.
        """
        if not text:
            return ""
            
        # 1. Normalização NFKC
        normalized = unicodedata.normalize('NFKC', text)
        
        # 2. Remove caracteres que não sejam letras, números ou espaços
        cleaned = re.sub(r'[^\w\s\-\.]', '', normalized, flags=re.UNICODE)
        
        # 3. Limita tamanho
        return cleaned.strip()[:70]

    @contextmanager
    def _get_cert_context(self):
        """
        Lê o arquivo .p12 e prepara contexto SSL seguro.
        """
        p12_path = self.creds.get("certificate_path")
        p12_password = self.creds.get("certificate_password", "").encode()
        
        if not os.path.exists(p12_path):
            raise FileNotFoundError(f"Certificado não encontrado em: {p12_path}")

        with open(p12_path, "rb") as f:
            p12_data = f.read()

        private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(
            p12_data, p12_password
        )

        with tempfile.NamedTemporaryFile(delete=False) as t_cert, tempfile.NamedTemporaryFile(delete=False) as t_key:
            try:
                t_cert.write(certificate.public_bytes(Encoding.PEM))
                t_cert.close()

                t_key.write(private_key.private_bytes(
                    Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()
                ))
                t_key.close()

                yield (t_cert.name, t_key.name)

            finally:
                if os.path.exists(t_cert.name): os.unlink(t_cert.name)
                if os.path.exists(t_key.name): os.unlink(t_key.name)

    async def authenticate_async(self):
        auth = base64.b64encode(
            f"{self.creds['client_id']}:{self.creds['client_secret']}".encode()
        ).decode()

        headers = {
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json"
        }

        with self._get_cert_context() as cert:
            # httpx suporta cert=(cert_file, key_file)
            async with httpx.AsyncClient(cert=cert) as client:
                response = await client.post(
                    f"{self.env_url}/oauth/token",
                    json={"grant_type": "client_credentials"},
                    headers=headers
                )
        
        if response.status_code == 200:
            return response.json()["access_token"]
        raise Exception(f"Erro Auth Efí ({response.status_code}): {response.text}")

    async def create_immediate_charge_async(self, txid: str, cpf: str, nome: str, valor: str):
        token = await self.authenticate_async()
        
        nome_limpo = self.sanitize_string(nome)
        if not nome_limpo:
            nome_limpo = "Cliente Telegram"
            
        print(f"🧹 Nome higienizado: '{nome}' -> '{nome_limpo}'")

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        cpf_limpo = "".join(filter(str.isdigit, cpf))
        
        body = {
            "calendario": {"expiracao": 3600},
            "devedor": {
                "cpf": cpf_limpo,
                "nome": nome_limpo
            },
            "valor": {"original": valor},
            "chave": self.creds.get("pix_key"),
            "solicitacaoPagador": "Recarga via Bot"
        }

        with self._get_cert_context() as cert:
            async with httpx.AsyncClient(cert=cert) as client:
                response = await client.put(
                    f"{self.env_url}/v2/cob/{txid}",
                    json=body,
                    headers=headers
                )

        if response.status_code == 201:
            data = response.json()
            loc_id = data["loc"]["id"]
            return await self._get_qrcode_async(loc_id, token, headers)
        
        raise Exception(f"Erro Criar Cobrança ({response.status_code}): {response.text}")

    async def _get_qrcode_async(self, loc_id, token, headers):
        with self._get_cert_context() as cert:
            async with httpx.AsyncClient(cert=cert) as client:
                response = await client.get(
                    f"{self.env_url}/v2/loc/{loc_id}/qrcode",
                    headers=headers
                )
            
        if response.status_code == 200:
            return response.json()
        
        raise Exception(f"Erro QR Code ({response.status_code}): {response.text}")
