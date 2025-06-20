FROM python:3.10-slim

# Устанавливаем зависимости системы и чистим за собой
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Сначала копируем только requirements.txt для лучшего кэширования
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы
COPY . .

# Создаем директории для логов и данных
RUN mkdir -p /app/logs /app/data

CMD ["python", "./main.py"]