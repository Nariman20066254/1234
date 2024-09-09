import asyncio
from asyncio import WindowsSelectorEventLoopPolicy
from telegram import Update, InputMediaPhoto
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import requests
from bs4 import BeautifulSoup
import urllib.parse
import g4f

# Установка политики Event Loop для Windows
asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())

# Функция для обработки запроса и получения ответа от API
async def get_car_part_info(messages: list) -> str:
    response = g4f.ChatCompletion.create(
        model=g4f.models.gpt_4o_mini,
        messages=messages
    )
    return response

# Функция для поиска изображений
def search_images(query):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    query = urllib.parse.quote(query)
    url = f"https://www.google.com/search?hl=en&tbm=isch&q={query}"
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    image_urls = []
    for img_tag in soup.find_all("img"):
        img_url = img_tag.get("src")
        if img_url and img_url.startswith("http"):
            image_urls.append(img_url)
            if len(image_urls) >= 5:  # Ограничиваем до 5 изображений
                break
    
    return image_urls

# Обработка команд "/start" и "/help"
async def start(update: Update, context):
    await update.message.reply_text("Привет! Напишите модель машины, и я постараюсь найти информацию.")

# Обработка текстовых сообщений
async def handle_message(update: Update, context):
    user_message = update.message.text
    question = f"""
{user_message}
заполни эти данные 

Производитель    
Тип    
Назначение    
Марка    
Модель напиши все на которые подходит
Двигатель напиши все на которые подходит
Объем напиши объемы которые подходят 
Год    
Артикул оставь пустым
Номер OEM оставь пустым 
Напиши вес     
Напиши длину 
Напиши высоту
Напиши ширину 
И в конце напиши на 150 слов мини описание.
"""

    # Отправляем сообщение о сборе информации
    await update.message.reply_text("Идет сбор информации, пожалуйста, подождите...")
    
    # Обработка запроса и получение ответа от API
    messages = [{"role": "user", "content": question}]
    answer = await get_car_part_info(messages=messages)
    messages.append({"role": "assistant", "content": answer})

    # Поиск изображений
    image_urls = search_images(user_message)
    
    # Отправляем результат пользователю
    await update.message.reply_text(answer)
    
    # Отправка изображений
    if image_urls:
        media_group = [InputMediaPhoto(media=url) for url in image_urls]
        await update.message.reply_media_group(media_group)

def main():
    # Введите ваш токен бота здесь
    TOKEN = '7095244087:AAEiRoEGfDp6Nvu_66cVvoh0J_IuNfXWSQ8'
    
    # Создание приложения Telegram
    application = Application.builder().token(TOKEN).build()
    
    # Обработчики команд и сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()
