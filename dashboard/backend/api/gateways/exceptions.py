"""
Exceções personalizadas para o sistema de gateways
"""


class GatewayException(Exception):
    """Exceção base para erros de gateway"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class GatewayNotConfiguredException(GatewayException):
    """Lançada quando um gateway não está configurado corretamente"""
    def __init__(self, gateway_name: str):
        super().__init__(f"Gateway '{gateway_name}' não está configurado corretamente", "GATEWAY_NOT_CONFIGURED")


class GatewayNotActiveException(GatewayException):
    """Lançada quando um gateway não está ativo"""
    def __init__(self, gateway_name: str):
        super().__init__(f"Gateway '{gateway_name}' não está ativo", "GATEWAY_NOT_ACTIVE")


class GatewayNotSupportedException(GatewayException):
    """Lançada quando um gateway não é suportado"""
    def __init__(self, gateway_name: str):
        super().__init__(f"Gateway '{gateway_name}' não é suportado", "GATEWAY_NOT_SUPPORTED")


class PaymentCreationException(GatewayException):
    """Lançada quando ocorre um erro ao criar um pagamento"""
    def __init__(self, gateway_name: str, details: str = None):
        message = f"Erro ao criar pagamento no gateway '{gateway_name}'"
        if details:
            message += f": {details}"
        super().__init__(message, "PAYMENT_CREATION_ERROR")


class TransactionNotFoundException(GatewayException):
    """Lançada quando uma transação não é encontrada"""
    def __init__(self, txid: str):
        super().__init__(f"Transação com TXID '{txid}' não encontrada", "TRANSACTION_NOT_FOUND")


class ValueMismatchException(GatewayException):
    """Lançada quando o valor pago não corresponde ao valor da transação"""
    def __init__(self, expected: float, actual: float):
        super().__init__(
            f"Valor pago não corresponde ao valor da transação. Esperado: {expected}, Pago: {actual}",
            "VALUE_MISMATCH"
        )


class UserNotFoundException(GatewayException):
    """Lançada quando um usuário não é encontrado"""
    def __init__(self, user_telegram_id: str):
        super().__init__(f"Usuário com Telegram ID '{user_telegram_id}' não encontrado", "USER_NOT_FOUND")


class InvalidWebhookDataException(GatewayException):
    """Lançada quando os dados do webhook são inválidos"""
    def __init__(self, details: str = None):
        message = "Dados do webhook inválidos"
        if details:
            message += f": {details}"
        super().__init__(message, "INVALID_WEBHOOK_DATA")