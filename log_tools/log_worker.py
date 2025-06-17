import asyncio
from log_tools.excel_export import log_to_excel

log_queue = asyncio.Queue()


async def log_worker(queue: asyncio.Queue):
    while True:
        log_data = await queue.get()
        try:
            log_to_excel(**log_data)
        except Exception as e:
            print(f"❌ Ошибка при логировании: {e}")
        queue.task_done()
