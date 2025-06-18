# 🤖 Sigma Support Bot

Telegram-бот, который помогает пользователям находить ответы на вопросы по руководству продукта **Sigma**. Бот работает через языковую модель (LLM), ищет ответы в векторной базе `Qdrant` и написан на `Python + Aiogram`.

---

## 🚀 Возможности

- Обработка пользовательских вопросов через LLM (GPT, Claude, Gemini)
- Поиск по руководству через Qdrant (векторная БД)
- Логирование вопросов/ответов в Excel
- Поддержка очередей (`asyncio.Queue`)
- Команда `/set_model` с выбором модели
- FSM, блокировка спамеров, ограничения по времени

---

## ⚙️ Используемые технологии

- 🐍 Python 3.10+
- 🤖 Aiogram 3.x
- 🔍 Qdrant (облачная векторная БД)
- 🧠 OpenAI / Gemini / Claude (LLM)
- 🐳 Docker + Docker Compose
- 📊 OpenPyXL (логирование в Excel)

---

## 📦 Установка

### 1. Клонируй проект:

```bash
git clone https://github.com/dfoagi/sigma_bot
cd sigma-bot
```

### 2. Создай `.env` файл:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_GROUP_ID=-123456789012
PROXY_API_KEY=your_proxyapi_key
PROXY_API_BASE_URL_OPENAI=https://api.proxyapi.ru/openai/v1
QDRANT_URL=https://your-cloud-qdrant-host
QDRANT_API_KEY=your_qdrant_api_key
ADMIN_ID=123456789
COLLECTION_NAME=your_qdrant_collection_name
```

### 3. Запусти через Docker:

```bash
docker-compose up --build -d
```

---

## 📂 Структура проекта

```
├── bot/
│   ├── handlers/         # user.py, admin.py, system.py
│   └── moderation.py
├── core/                 # get_answer, qdrant, LLM вызовы
├── helper/               # модель, блокировки, клиенты
├── logging/              # очередь логов и логгеры
├── logs/                 # Excel-файл с логами
├── Dockerfile
├── docker-compose.yml
├── main.py
├── requirements.txt
├── .env
└── README.md
```
