# Bot Telegram - TelegramaIO

## Descrição
Bot simples do Telegram integrado com Reflex framework.

## Comandos
- `/start` - Retorna "Hello World! Bot iniciado com sucesso!"

## Configuração

### Token do Bot
O bot requer um token válido do Telegram. Configure através de:

1. **Variável de ambiente (recomendado):**
   ```bash
   export TELEGRAM_BOT_TOKEN="seu_token_aqui"
   ```

2. **Ou diretamente no código:**
   Edite `bot.py` e substitua `BOT_TOKEN` pelo seu token real.

### Obter Token do Telegram
1. Converse com [@BotFather](https://t.me/botfather) no Telegram
2. Use `/newbot` para criar um novo bot
3. Copie o token fornecido

## Estrutura de Arquivos
- `bot.py` - Lógica principal do bot
- `routes.py` - Endpoints de API para status do bot
- `startup.py` - Funções de inicialização do bot
- `__init__.py` - Pacote Python

## Como Testar
1. Configure o token do bot (veja seção Configuração)
2. Execute o Reflex: `reflex run`
3. Abra http://localhost:8000/api/telegram/status para verificar status
4. Envie `/start` para o bot no Telegram
5. Você receberá a mensagem "Hello World! Bot iniciado com sucesso!"