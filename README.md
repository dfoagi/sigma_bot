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

- 🐍 Python 3.11+
- 🤖 Aiogram 3.x
- 🔍 Qdrant (облачная векторная БД)
- 🧠 OpenAI / Gemini / Claude (LLM)
- 🐳 Docker + Docker Compose
- 📊 OpenPyXL (логирование в Excel)

---

## 📦 Установка

### 1. Клонируй проект:

```bash
git clone https://github.com/you/sigma-bot.git
cd sigma-bot
```

### 2. Создай `.env` файл:

```env
BOT_TOKEN=your_telegram_bot_token
ADMIN_ID=123456789
OPENAI_API_KEY=your_openai_key
OPENAI_BASE_URL=https://api.proxyapi.ru/openai
PROXYAPI_KEY=your_proxyapi_key
QDRANT_URL=https://your-cloud-qdrant-host
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_COLLECTION=sigmaRP_large
```

### 3. Запусти через Docker:

```bash
docker compose up --build -d
```

---

## 📂 Структура проекта

```
├── bot/
│   ├── handlers/         # user.py, admin.py, system.py
│   └── main.py
├── core/                 # get_answer, qdrant, LLM вызовы
├── helper/               # модель, блокировки, клиенты
├── logging/              # очередь логов и логгеры
├── logs/                 # Excel-файл с логами
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env
└── README.md
```

---

## 📌 Команды бота

- `/start` — запуск
- `/set_model` — выбор модели (доступно только админу)
- `/model` — текущая модель
- `вопрос` — любой текст, бот отвечает по руководству

---

## 🔐 Безопасность

- `.env` добавлен в `.gitignore`
- Команды администратора ограничены по `ADMIN_ID`
- Лимиты на частые запросы + FSM

---

## 🛠️ TODO (по желанию)

- [ ] Добавить логирование в БД
- [ ] Подключить Telegram WebApp
- [ ] Реализовать `/export_logs`
- [ ] Добавить CI/CD через GitHub Actions

---

## 👨‍💻 Автор

Разработка: [@yourname](https://t.me/yourname)  
Поддержка: support@3ksigma.ru