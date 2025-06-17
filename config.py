import os
from dotenv import load_dotenv

load_dotenv(override=True)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROUP_ID = os.getenv("TELEGRAM_GROUP_ID")
PROXYAPI_KEY = os.getenv("PROXY_API_KEY")
OPENAI_BASE_URL = os.getenv("PROXY_API_BASE_URL_OPENAI")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY=os.getenv("QDRANT_API_KEY")
ADMIN_ID=int(os.getenv("ADMIN_ID"))
QDRANT_COLLECTION=os.getenv("COLLECTION_NAME")
