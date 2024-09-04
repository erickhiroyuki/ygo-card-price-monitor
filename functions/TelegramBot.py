import asyncio
from telegram import Bot


async def send_message(message: str, token: str, chat_id: str) -> None:
    bot = Bot(token=token)
    await bot.send_message(chat_id=chat_id, text=message)

if __name__ == "__main__":
    asyncio.run(send_message())
