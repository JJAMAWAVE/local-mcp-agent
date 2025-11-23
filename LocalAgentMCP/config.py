# ============================================================
# config.py
# Local MCP Agent – Global Configuration File
# ============================================================

import os

# ------------------------------------------------------------
# GPT HISTORY SAVE DIRECTORY
# ------------------------------------------------------------
GPT_HISTORY_DIR = r"C:\AshenWard\Documents\gpt_history"

# 폴더가 없으면 자동 생성
if not os.path.exists(GPT_HISTORY_DIR):
    os.makedirs(GPT_HISTORY_DIR, exist_ok=True)

# ------------------------------------------------------------
# UNITY PIPE NAME
# ------------------------------------------------------------
UNITY_PIPE_NAME = r"\\.\pipe\UnityAIAgentPipe"

# ------------------------------------------------------------
# RENDER RELAY SERVER (PROD)
# ------------------------------------------------------------
RENDER_WS_URL = "wss://mcp-relay-server.onrender.com/ws"

# ------------------------------------------------------------
# GOOGLE API
# (OAuth Tokens, Credentials 저장경로 등)
# ------------------------------------------------------------
GOOGLE_TOKEN_PATH = r"C:\AshenWard\Documents\gpt_history\google_token.json"
GOOGLE_CREDENTIALS_PATH = r"C:\AshenWard\Documents\gpt_history\google_credentials.json"

# ------------------------------------------------------------
# GENERAL SETTINGS
# ------------------------------------------------------------
REQUEST_TIMEOUT = 30
MAX_LOG_LENGTH = 20000
