import reflex as rx
import json
import os
from datetime import datetime, timedelta
from collections import Counter

# Caminho para o arquivo de log
LOG_FILE = "user_interactions.json"

class BotState(rx.State):
    """Bot management, control, and analytics state."""
    
    # --- Status do Bot (Controle de API) ---
    bot_running: bool = False
    bot_status_loading: bool = False
    bot_response_time: str = "--"
    
    # --- Estatísticas de Texto (Cards) ---
    active_users_count: int = 0
    messages_today_count: int = 0
    commands_executed_count: int = 0
    
    # --- Listas e Dados para Gráficos ---
    top_commands_list: list[dict] = []
    recent_logs_list: list[str] = []
    
    # NOVOS CAMPOS PARA GRÁFICOS
    interactions_chart_data: list[dict] = [] # Gráfico de Área (Interações/Hora)
    interaction_types_data: list[dict] = []  # Gráfico de Pizza (Tipos)
    
    def load_log_data(self):
        """Lê o JSON e atualiza todas as estatísticas e dados dos gráficos."""
        if not os.path.exists(LOG_FILE):
            return

        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except Exception:
            return 

        if not logs:
            return

        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        
        # Variáveis temporárias para processamento
        active_users_24h = set()
        msgs_today = 0
        cmds_all_time = []
        cmds_today = 0
        raw_logs_formatted = []
        
        # Contadores para Gráficos
        type_counts = {"Mensagem": 0, "Comando": 0, "Botão": 0}
        
        # Inicializar últimas 24h para o gráfico de área (cronológico)
        hourly_counts = {}
        for i in range(23, -1, -1):
            h_str = (now - timedelta(hours=i)).strftime("%H:00")
            hourly_counts[h_str] = 0

        # Processar logs (da interação mais recente para a mais antiga)
        for entry in reversed(logs):
            timestamp_str = entry.get("timestamp", "")
            try:
                dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue

            # 1. Estatísticas de 24h (Usuários e Gráfico de Área)
            if dt > now - timedelta(hours=24):
                active_users_24h.add(entry.get("user_id"))
                h_key = dt.strftime("%H:00")
                if h_key in hourly_counts:
                    hourly_counts[h_key] += 1

            # 2. Estatísticas de Hoje
            if timestamp_str.startswith(today_str):
                msgs_today += 1

            # 3. Classificação de Interação e Formatação de Log
            log_data = entry.get("log", {})
            msg_data = log_data.get("message", {})
            text = msg_data.get("text", "")
            
            action_type = "Mensagem"
            if "callback_query" in log_data:
                action_type = "Botão"
                cb = log_data["callback_query"]
                user_name = cb.get("from_user", {}).get("username", "Unknown")
                action_desc = f"Botão: {cb.get('data')}"
            else:
                user_name = msg_data.get("from_user", {}).get("username", "Unknown")
                if text and text.startswith("/"):
                    action_type = "Comando"
                    cmd_name = text.split()[0]
                    cmds_all_time.append(cmd_name)
                    if timestamp_str.startswith(today_str):
                        cmds_today += 1
                    action_desc = f"Comando: {cmd_name}"
                else:
                    action_desc = f"Mensagem: {text[:20]}..." if text else "Mídia/Outro"
            
            # Incrementa contador de tipos para o gráfico de pizza
            if action_type in type_counts:
                type_counts[action_type] += 1

            # Adiciona ao log de texto da UI (limite de 20)
            if len(raw_logs_formatted) < 20:
                raw_logs_formatted.append(f"{timestamp_str} - @{user_name}: {action_desc}")

        # --- Atualizar Variáveis de Estado ---
        self.active_users_count = len(active_users_24h)
        self.messages_today_count = msgs_today
        self.commands_executed_count = cmds_today
        self.recent_logs_list = raw_logs_formatted

        # Top 5 Comandos
        self.top_commands_list = [
            {"cmd": cmd, "count": count} 
            for cmd, count in Counter(cmds_all_time).most_common(5)
        ]
        
        # Gráfico de Área: Interações por Hora
        self.interactions_chart_data = [
            {"time": k, "count": v} for k, v in hourly_counts.items()
        ]
        
        # Gráfico de Pizza: Distribuição de Tipos
        self.interaction_types_data = [
            {"name": "Mensagens", "value": type_counts["Mensagem"], "fill": "#8884d8"},
            {"name": "Comandos", "value": type_counts["Comando"], "fill": "#82ca9d"},
            {"name": "Botões", "value": type_counts["Botão"], "fill": "#ffc658"},
        ]
        
        # Status presumido (via Log) caso a API falhe
        if logs:
            try:
                last_ts = logs[-1].get("timestamp")
                last_dt = datetime.strptime(last_ts, "%Y-%m-%d %H:%M:%S")
                if last_dt > now - timedelta(minutes=5):
                    self.bot_running = True
                    self.bot_response_time = "Ativo agora"
                else:
                    self.bot_response_time = "Ocioso"
            except: pass

    # --- Funções de Controle (API Backend) ---

    async def get_bot_status(self):
        """Verifica logs locais e consulta API externa."""
        self.bot_status_loading = True
        yield
        
        # Primeiro carrega o que temos no arquivo local
        self.load_log_data()
        
        # Depois tenta confirmar com o servidor do bot
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:8000/api/telegram/status", timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    self.bot_running = data.get("running", False)
                    self.bot_response_time = "2ms" if self.bot_running else "--"
                    yield rx.toast.info(f"Status do bot: {'Online' if self.bot_running else 'Offline'}", position="top-center")
                else:
                    yield rx.toast.error("Erro ao verificar status na API", position="top-center")
        except Exception as e:
            yield rx.toast.error(f"Erro de conexão com API: {str(e)}", position="top-center")
        finally:
            self.bot_status_loading = False
            yield

    async def start_bot(self):
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.post("http://localhost:8000/api/telegram/start")
                if response.status_code == 200:
                    self.bot_running = True
                    yield rx.toast.success("Bot iniciado com sucesso!", position="top-center")
                else:
                    error_msg = response.json().get("detail", "Erro ao iniciar bot")
                    yield rx.toast.error(f"Erro: {error_msg}", position="top-center")
        except Exception as e:
            yield rx.toast.error(f"Erro de conexão: {str(e)}", position="top-center")
    
    async def stop_bot(self):
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.post("http://localhost:8000/api/telegram/stop")
                if response.status_code == 200:
                    self.bot_running = False
                    yield rx.toast.success("Bot parado com sucesso!", position="top-center")
                else:
                    yield rx.toast.error("Erro ao parar bot", position="top-center")
        except Exception as e:
            yield rx.toast.error(f"Erro de conexão: {str(e)}", position="top-center")
    
    async def test_bot(self):
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.post("http://localhost:8000/api/telegram/test")
                if response.status_code == 200:
                    yield rx.toast.success("Bot testado com sucesso!", position="top-center")
                else:
                    yield rx.toast.error("Falha no teste do bot", position="top-center")
        except Exception as e:
            yield rx.toast.error(f"Erro de conexão: {str(e)}", position="top-center")
    
    async def restart_bot(self):
        await self.stop_bot()
        await self.start_bot()
    
    def clear_logs(self):
        """Simulação de limpeza de logs."""
        return rx.toast.success("Comando de limpeza enviado", position="top-center")