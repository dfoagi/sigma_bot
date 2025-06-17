import csv
from datetime import datetime
import os

CSV_FILE = os.path.join("logs", "logs.csv")


def log_to_csv(username, user_id, question, answer, tokens_used, chapter_ids, chapter_names, model):
    file_exists = os.path.exists(CSV_FILE)

    with open(CSV_FILE, mode="a", encoding="windows-1251", newline='') as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "Время", "Логин", "Telegram ID", "Вопрос", "Ответ",
                "Модель", "Токены", "ID документов", "Названия глав"
            ])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            username or "—",
            user_id,
            question,
            answer,
            model,
            tokens_used,
            ", ".join(map(str, chapter_ids)) if isinstance(chapter_ids, list) else chapter_ids,
            ", ".join(map(str, chapter_names)) if isinstance(chapter_names, list) else chapter_names,
        ])
