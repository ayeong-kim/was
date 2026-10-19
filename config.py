import os

# .env 파일이 있으면 읽어서 환경변수로 등록 (클라우드에서 직접 넣은 환경변수가 우선)
_env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(_env_file):
    with open(_env_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())

WAS_HOST = os.environ.get("WAS_HOST", "127.0.0.1")                          # 클라우드: 0.0.0.0
WAS_PORT = int(os.environ.get("WAS_PORT", "8000"))
DB_PATH = os.environ.get("DB_PATH", "petclinic.db")                         # sqlite 파일 경로
COOKIE_SECURE = os.environ.get("COOKIE_SECURE", "false").lower() == "true"  # HTTPS면 true
