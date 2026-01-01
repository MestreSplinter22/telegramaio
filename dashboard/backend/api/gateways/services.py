"""
Módulo de serviços para operações de pagamento
"""
from typing import Optional
import reflex as rx
from dashboard.backend.models import Transaction, User, GatewayConfig
from .gateway_factory import GatewayProcessor
from .constants import (
    TRANSACTION_TYPE_DEPOSIT,
    TRANSACTION_STATUS_PENDING,
    TRANSACTION_STATUS_COMPLETED,
    EXTRA_DATA_TXID,
    EXTRA_DATA_GATEWAY_ID,
    EXTRA_DATA_EXTERNAL_ID,
    EXTRA_DATA_SCREEN_ID,
    ERROR_NO_ACTIVE_GATEWAY,
    ERROR_USER_NOT_FOUND,
    VALUE_TOLERANCE,
    DEFAULT_CPF,
    DEFAULT_EMAIL
)
import json
import uuid


class PaymentService:
    """
    Serviço responsável por criar pagamentos
    """
    @staticmethod
    def create_payment(user_telegram_id: str, amount: float, gateway_name: str = "suitpay", screen_id: Optional[str] = None) -> dict:
        """
        Cria um pagamento e retorna os dados necessários para o QR Code PIX
        """
        with rx.session() as session:
            # 1. Buscar Gateway Ativo
            gateway = session.query(GatewayConfig).filter(
                GatewayConfig.name == gateway_name,
                GatewayConfig.is_active == True
            ).first()
            
            if not gateway:
                # Fallback: Tenta achar a primeira ativa se a solicitada falhar
                gateway = session.query(GatewayConfig).filter(GatewayConfig.is_active == True).first()
                if not gateway:
                    raise ValueError(ERROR_NO_ACTIVE_GATEWAY)

            # 2. Buscar Usuário
            user = session.query(User).filter(User.telegram_id == user_telegram_id).first()
            if not user:
                raise ValueError(ERROR_USER_NOT_FOUND)

            # 3. Gerar ID Único da Transação
            txid = uuid.uuid4().hex
            
            # Dados do Pagador (Padrão ou do User)
            cpf = DEFAULT_CPF  # Em produção, você deve pegar user.cpf reais
            email = DEFAULT_EMAIL  # Em produção, você deve pegar user.email reais
            nome = f"{user.first_name} {user.last_name}"

            try:
                # Criar processador de gateway
                processor = GatewayProcessor(gateway)
                
                # Criar pagamento no gateway
                pix_result = processor.create_payment(
                    txid=txid,
                    cpf=cpf,
                    nome=nome,
                    email=email,
                    valor=amount
                )

                # 4. Salvar Transação no Banco
                extra_data_dict = {
                    EXTRA_DATA_TXID: txid,
                    EXTRA_DATA_GATEWAY_ID: gateway.id,
                    EXTRA_DATA_EXTERNAL_ID: pix_result.get("external_id")
                }
                
                # Adicionar screen_id se fornecido
                if screen_id:
                    extra_data_dict[EXTRA_DATA_SCREEN_ID] = screen_id

                new_txn = Transaction(
                    user_id=user.telegram_id,
                    type=TRANSACTION_TYPE_DEPOSIT,
                    amount=amount,
                    description=f"Recarga via {gateway.name}",
                    status=TRANSACTION_STATUS_PENDING,
                    extra_data=json.dumps(extra_data_dict)
                )
                session.add(new_txn)
                session.commit()

                return {
                    "txid": txid,
                    "pix_copia_cola": pix_result["pix_copia_cola"],
                    "qrcode_base64": pix_result["qrcode_base64"],
                    "status": TRANSACTION_STATUS_PENDING
                }

            except Exception as e:
                session.rollback()
                raise e


class TransactionService:
    """
    Serviço responsável por operações relacionadas a transações
    """
    @staticmethod
    def update_transaction_status(txn_id: int, new_status: str, amount_paid: float = None) -> bool:
        """
        Atualiza o status de uma transação e, opcionalmente, verifica o valor pago
        """
        with rx.session() as session:
            txn = session.query(Transaction).filter(Transaction.id == txn_id).first()
            if not txn:
                return False

            if amount_paid is not None and abs(txn.amount - amount_paid) > VALUE_TOLERANCE:
                print(f"❌ Fraude Detectada: Valor esperado {txn.amount}, pago {amount_paid}")
                return False

            txn.status = new_status
            session.add(txn)
            session.commit()
            return True

    @staticmethod
    def complete_transaction_by_txid(txid: str, amount_paid: float = None) -> Optional[Transaction]:
        """
        Completa uma transação com base no TXID
        """
        with rx.session() as session:
            txn = session.query(Transaction).filter(
                Transaction.status == TRANSACTION_STATUS_PENDING,
                Transaction.extra_data.contains(txid)
            ).first()

            if not txn:
                return None

            if amount_paid is not None and abs(txn.amount - amount_paid) > VALUE_TOLERANCE:
                print(f"❌ Fraude Detectada: Valor esperado {txn.amount}, pago {amount_paid}")
                return None

            # Atualizar status da transação
            txn.status = TRANSACTION_STATUS_COMPLETED
            
            # Atualizar saldo do usuário
            user = session.query(User).filter(User.telegram_id == txn.user_id).first()
            if user:
                user.balance += txn.amount
                user.total_spent += txn.amount
                session.add(user)

            session.add(txn)
            session.commit()
            return txn

    @staticmethod
    def get_transaction_by_txid(txid: str) -> Optional[Transaction]:
        """
        Obtém uma transação pelo TXID
        """
        with rx.session() as session:
            return session.query(Transaction).filter(
                Transaction.extra_data.contains(txid)
            ).first()