import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Курсы валют к NOK
RATES = {
    "USD": 10.5,
    "EUR": 11.4,
    "RUB": 0.11,
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я конвертер валют 💱\n\n"
        "Напиши сумму и валюту, например:\n"
        "100 USD\n"
        "50 EUR\n"
        "1000 RUB"
    )

async def convert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.upper().split()
    
    if len(text) != 2:
        await update.message.reply_text("Формат: 100 USD")
        return
    
    try:
        amount = float(text[0])
        currency = text[1]
    except ValueError:
        await update.message.reply_text("Формат: 100 USD")
        return
    
    rate = RATES.get(currency)
    if not rate:
        await update.message.reply_text(f"Валюта {currency} не поддерживается.\nДоступны: USD, EUR, RUB")
        return
    
    result = amount * rate
    await update.message.reply_text(f"{amount} {currency} = {result:.2f} NOK")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, convert))
    print("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
