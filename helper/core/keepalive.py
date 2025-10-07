import asyncio
import random
import json
import logging
import os
from datetime import datetime, time
from typing import List, Dict

from helper.core.qdrant_client import get_qdrant_client
from helper.core.qdrant_client import get_relevant_chunks
from config import QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION, ADMIN_ID

logger = logging.getLogger(__name__)

_current_report_time = 21    # время отправки отчета


def get_current_report_time():
    return _current_report_time


def set_current_report_time(new_time: int):
    global _current_report_time
    _current_report_time = new_time


class KeepAlive:
    def __init__(self):
        self.bot = None
        self.is_running = False
        self.task = None
        self.embeddings_dir = "helper/data/keepalive_questions"
        self.daily_stats = {
            "date": None,
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0
        }
    

    def _load_embedding_files(self) -> List[Dict]:
        """Загружает файлы с эмбеддингами из папки"""
        embeddings = []
        if not os.path.exists(self.embeddings_dir):
            logger.warning(f"Папка {self.embeddings_dir} не найдена")
            return embeddings
        
        for filename in os.listdir(self.embeddings_dir):
            if filename.endswith('.json'):
                try:
                    file_path = os.path.join(self.embeddings_dir, filename)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        data['filename'] = filename
                        embeddings.append(data)
                except Exception as e:
                    logger.error(f"Ошибка загрузки файла {filename}: {e}")
        
        logger.info(f"Загружено {len(embeddings)} файлов с эмбеддингами")
        return embeddings
    

    def _get_random_embedding(self) -> Dict:
        """Возвращает случайный эмбеддинг из загруженных"""
        embeddings = self._load_embedding_files()
        if not embeddings:
            raise ValueError("Нет доступных эмбеддингов")
        return random.choice(embeddings)
    

    async def make_keepalive_query(self, bot):
        """Выполняет один keep-alive запрос"""
        try:
            # Выбираем случайный эмбеддинг
            embedding_data = self._get_random_embedding()
            question_text = embedding_data.get('text', 'Unknown question')
            question_vector = embedding_data['vector']
            
            logger.info(f"Выполняю keep-alive запрос: {question_text}")
            
            # Выполняем запрос к Qdrant
            qdrant_client = get_qdrant_client(QDRANT_URL, QDRANT_API_KEY)
            relevant_chunks = get_relevant_chunks(
                client=qdrant_client,
                collection_name=QDRANT_COLLECTION,
                question_vector=question_vector,
                top_k=3
            )
            
            self.daily_stats["total_queries"] += 1
            self.daily_stats["successful_queries"] += 1
            
            logger.info(f"Keep-alive запрос выполнен.")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка в keep-alive запросе: {e}")
            self.daily_stats["total_queries"] += 1
            self.daily_stats["failed_queries"] += 1
            await self.send_notification(bot)
            return False
    

    def _generate_daily_schedule(self) -> List[time]:
        """Генерирует расписание на день: 2-3 случайных времени"""
        num_queries = random.randint(2, 3)  # 2 или 3 запроса
        times = []
        
        for _ in range(num_queries):
            # Случайное время между 9:00 и 20:00
            hour = random.randint(9, 20)
            minute = random.randint(1, 59)
            times.append(time(hour, minute))
        
        # Сортируем по времени
        return sorted(times)
    

    async def _wait_until(self, target_time: time):
        """Ожидает до указанного времени"""
        now = datetime.now()
        target_datetime = datetime.combine(now.date(), target_time)
        
        # Если время уже прошло сегодня, планируем на завтра
        if target_datetime <= now:
            target_datetime = target_datetime.replace(day=target_datetime.day + 1)
        
        wait_seconds = (target_datetime - now).total_seconds() + random.randint(5, 50)
        logger.info(f"Ожидаю {wait_seconds:.0f} секунд до {target_time}")
        await asyncio.sleep(wait_seconds)
    

    async def send_daily_report(self, bot):
        """Отправляет ежедневный отчет админу"""
        today = datetime.now().strftime("%d.%m.%Y")
        report_text = (
            f"📊 Отчет по keep-alive запросам\n"
            f"Дата: {today}\n"
            f"Всего запросов: {self.daily_stats['total_queries']}\n"
            f"Успешных: {self.daily_stats['successful_queries']}\n"
            f"Ошибок: {self.daily_stats['failed_queries']}\n"
            f"Статус: {'✅ Все запросы успешны' if self.daily_stats['failed_queries'] == 0 else '⚠️ Были ошибки'}"
        )
        
        try:
            await bot.send_message(chat_id=ADMIN_ID, text=report_text)
            logger.info("Ежедневный отчет отправлен")
        except Exception as e:
            logger.error(f"Ошибка отправки отчета: {e}")


    async def send_notification(self, bot):
        """Отправляет отчет об ошибке админу"""
        report_text = (f"⚠️ С БД какая-то проблема ⚠️")
        
        try:
            await bot.send_message(chat_id=ADMIN_ID, text=report_text)
            logger.info("Админу отправлено предупреждени об ошибке")
        except Exception as e:
            logger.error(f"Ошибка отправки отчета: {e}")


    async def run(self, bot):
        """Основной цикл задачи"""
        self.is_running = True
        self.bot = bot
        logger.info("Запуск keep-alive задачи")
        
        while self.is_running:
            try:
                # Сбрасываем статистику
                today = datetime.now().date()
                self.daily_stats = {
                    "date": today,
                    "total_queries": 0,
                    "successful_queries": 0,
                    "failed_queries": 0
                }
                
                # Генерируем расписание на сегодня
                schedule = self._generate_daily_schedule()
                logger.info(f"Расписание на сегодня: {[t.strftime('%H:%M') for t in schedule]}")
                
                # Выполняем запросы по расписанию
                for query_time in schedule:
                    await self._wait_until(query_time)
                    if not self.is_running:
                        break
                    await self.make_keepalive_query(bot)
                
                # Ждем до отправки отчета
                if self.is_running:
                    report_time = time(get_current_report_time)
                    await self._wait_until(report_time)
                    await self.send_daily_report(bot)
                
                # Ждем до 2:00 следующего дня
                if self.is_running:
                    await self._wait_until(time(1, 0))  # 1:00 ночи
                    
            except Exception as e:
                logger.error(f"Ошибка в keep-alive задаче: {e}")
                await asyncio.sleep(300)  # Ждем 5 минут перед повторной попыткой
    

    def start(self, bot):
        """Запускает задачу"""
        if not self.is_running:
            self.task = asyncio.create_task(self.run(bot))
    

    def stop(self):
        """Останавливает задачу"""
        self.is_running = False
        if self.task:
            self.task.cancel()


keepalive = KeepAlive()
