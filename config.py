import os
from dotenv import load_dotenv

load_dotenv()
ARTIS_TOKEN = os.environ.get("ARTIS_BEARER_TOKEN")
if not ARTIS_TOKEN:
    raise RuntimeError("ARTIS_BEARER_TOKEN not set in .env")

BASE_URL = "http://localhost:8080/artis/api"
COMMON_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {ARTIS_TOKEN}"
}