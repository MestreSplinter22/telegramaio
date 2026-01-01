"""
Constantes e enums para o sistema de gateways de pagamento
"""

# Status de transação
TRANSACTION_STATUS_PENDING = "pending"
TRANSACTION_STATUS_COMPLETED = "completed"
TRANSACTION_STATUS_FAILED = "failed"

# Tipos de transação
TRANSACTION_TYPE_DEPOSIT = "deposit"

# Nomes de gateways
GATEWAY_NAME_EFI = "efi_bank"
GATEWAY_NAME_SUITPAY = "suitpay"
GATEWAY_NAME_OPENPIX = "openpix"

# Status de webhook
WEBHOOK_STATUS_PAID_OUT = "PAID_OUT"
WEBHOOK_STATUS_COMPLETED = "COMPLETED"

# Chaves de dados extras
EXTRA_DATA_TXID = "txid"
EXTRA_DATA_GATEWAY_ID = "gateway_id"
EXTRA_DATA_EXTERNAL_ID = "external_id"
EXTRA_DATA_SCREEN_ID = "screen_id"

# Mensagens de erro
ERROR_NO_ACTIVE_GATEWAY = "Nenhuma gateway ativa configurada."
ERROR_USER_NOT_FOUND = "Usuário não encontrado"
ERROR_UNSUPPORTED_GATEWAY = "Gateway não suportada"
ERROR_VALUE_MISMATCH = "Value mismatch"
ERROR_INVALID_JSON = "Invalid JSON"
ERROR_NO_CORRELATION_ID = "No correlationID found"

# Valores padrão
DEFAULT_CPF = "00000000000"
DEFAULT_EMAIL = "cliente@email.com"
DEFAULT_TEST_CPF = "12345678909"

# Caminhos de arquivos
FLOW_FILE_PATH = "dashboard/backend/telegram/flows/start_flow.json"

# Margem de erro para valores
VALUE_TOLERANCE = 0.05