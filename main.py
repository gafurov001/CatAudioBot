import asyncio
import logging
import os
import sys

from aiogram import Dispatcher, Bot, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from audio_edit import bolaklarga_ajrat_va_saqlash
from config import bot_token
from models import create_table, Audios

TOKEN = bot_token
dp = Dispatcher()

cache = dict()


@dp.message(CommandStart())
async def command_start_handler(message: Message, bot: Bot, user_id=None) -> None:
    files = os.listdir('audios')
    if files:
        file_name = files[0]
        file = await bolaklarga_ajrat_va_saqlash(f"audios/{file_name}")
        ikb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Audio tushunarsiz", callback_data=f"delete audio")
                ]
            ]
        )
        if user_id:
            await bot.send_audio(user_id, FSInputFile(file), reply_markup=ikb)
            cache[str(user_id)] = file
        else:
            await bot.send_audio(message.from_user.id, FSInputFile(file), reply_markup=ikb)
            cache[str(message.from_user.id)] = file

    else:
        await message.answer(f"Hozircha audiolar yo'q keyinroq urunib koring!")


@dp.callback_query(F.data == 'delete audio')
async def delete_audio(callback: CallbackQuery, bot: Bot):
    file_location = cache.get(str(callback.from_user.id))
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    os.remove(file_location)
    await command_start_handler(callback.message, bot, callback.from_user.id)


@dp.message()
async def audio_save(message: Message, bot: Bot):
    if message.reply_to_message and message.reply_to_message.audio:
        file_name = message.reply_to_message.audio.file_name
        path = f"edited_audios/{file_name}"
        is_exist = os.path.exists(path)
        if is_exist:
            await Audios.create(audio_location=path, text=message.text)
            await command_start_handler(message, bot)



async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    create_table()
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
