"""
Fábrica de gateways para permitir escalabilidade e manutenção fácil
"""
from typing import Dict, Type, Any
from dashboard.backend.gateways.efi_service import EfiPixService
from dashboard.backend.gateways.suitpay_service import SuitPayService
from dashboard.backend.gateways.openpix_service import OpenPixService
from dashboard.backend.models import GatewayConfig
from .constants import (
    GATEWAY_NAME_EFI, GATEWAY_NAME_SUITPAY, GATEWAY_NAME_OPENPIX, DEFAULT_CPF, DEFAULT_TEST_CPF
)


class GatewayServiceFactory:
    """
    Fábrica para criar instâncias de serviços de gateway
    """
    _services: Dict[str, Type] = {
        GATEWAY_NAME_EFI: EfiPixService,
        GATEWAY_NAME_SUITPAY: SuitPayService,
        GATEWAY_NAME_OPENPIX: OpenPixService,
    }

    @classmethod
    def register_service(cls, name: str, service_class: Type):
        """Registra um novo serviço de gateway"""
        cls._services[name] = service_class

    @classmethod
    def create_service(cls, gateway_config: GatewayConfig) -> Any:
        """Cria uma instância de serviço com base na configuração do gateway"""
        if gateway_config.name not in cls._services:
            raise ValueError(f"Gateway não suportada: {gateway_config.name}")
        
        service_class = cls._services[gateway_config.name]
        return service_class(gateway_config)

    @classmethod
    def get_available_gateways(cls) -> list:
        """Retorna a lista de gateways disponíveis"""
        return list(cls._services.keys())


class GatewayProcessor:
    """
    Processador de pagamentos que abstrai a lógica de diferentes gateways
    """
    def __init__(self, gateway_config: GatewayConfig):
        self.gateway_config = gateway_config
        self.service = GatewayServiceFactory.create_service(gateway_config)

    def create_payment(self, txid: str, cpf: str, nome: str, email: str, valor: float) -> dict:
        """
        Cria um pagamento no gateway apropriado
        """
        if self.gateway_config.name == GATEWAY_NAME_EFI:
            # A Efí exige CPF válido em Produção, cuidado com dados fake
            efi_data = self.service.create_immediate_charge(
                txid=txid,
                cpf=cpf or DEFAULT_TEST_CPF,  # Usar CPF de teste para Homologação
                nome=nome,
                valor=f"{valor:.2f}"
            )
            # Normaliza retorno da Efí
            return {
                "pix_copia_cola": efi_data.get("qrcode") or efi_data.get("pixCopiaECola"),
                "qrcode_base64": efi_data.get("imagemQrcode"),
                "external_id": txid
            }

        elif self.gateway_config.name == GATEWAY_NAME_SUITPAY:
            suit_data = self.service.create_pix_payment(
                txid=txid, 
                cpf=cpf, 
                nome=nome, 
                email=email, 
                valor=valor
            )
            # Normaliza retorno da SuitPay
            return {
                "pix_copia_cola": suit_data.get("pix_copia_cola"),
                "qrcode_base64": suit_data.get("qrcode_base64"),
                "external_id": suit_data.get("txid")
            }

        elif self.gateway_config.name == GATEWAY_NAME_OPENPIX:
            # OpenPix aceita CPF formatado ou limpo, vamos limpar por garantia
            cpf_limpo = "".join(filter(str.isdigit, cpf or DEFAULT_CPF))
            
            op_data = self.service.create_charge(
                txid=txid,
                nome=nome,
                cpf=cpf_limpo,
                valor=valor
            )
            
            return {
                "pix_copia_cola": op_data["pix_copia_cola"],
                "qrcode_base64": op_data["qrcode_base64"],
                "external_id": op_data["txid"]
            }

        else:
            raise ValueError(f"Gateway não suportada: {self.gateway_config.name}")