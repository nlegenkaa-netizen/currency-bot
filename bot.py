import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Курсы валют к NOK
RATES = {
    "USD": 10.5,
    "EUR": 11.4,
    "RUB": 0.11,
    "UAH": 0.25,    # гривна
    "GBP": 13.2,    # фунт
    "SEK": 0.95,    # шведская крона
}

# Псевдонимы на русском
ALIASES = {
    "доллар": "USD", "долларов": "USD", "бакс": "USD", "баксов": "USD",
    "евро": "EUR",
    "рубль": "RUB", "рублей": "RUB", "руб": "RUB",
    "гривна": "UAH", "гривен": "UAH", "грн": "UAH",
    "фунт": "GBP", "фунтов": "GBP",
    "крона": "SEK", "крон": "SEK",
}

def get_menu():
    return ReplyKeyboardMarkup([
        ["💵 USD → NOK", "💶 EUR → NOK"],
        ["🇺🇦 UAH → NOK", "🇷🇺 RUB → NOK"],
        ["🔄 NOK → другую", "📋 Все курсы"]
    ], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я конвертер валют 💱\n\n"
        "Напиши сумму и валюту:\n"
        "• 100 USD или 100 долларов\n"
        "• 50 EUR или 50 евро\n"
        "• 1000 UAH или 1000 гривен\n\n"
        "Или используй меню 👇",
        reply_markup=get_menu()
    )

async def show_rates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lines = ["📋 Текущие курсы (к NOK):\n"]
    for currency, rate in RATES.items():
        lines.append(f"1 {currency} = {rate} NOK")
    await update.message.reply_text("\n".join(lines), reply_markup=get_menu())

async def convert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    # Проверяем кнопки меню
    if "Все курсы" in text:
        await show_rates(update, context)
        return
    
    if "NOK → другую" in text:
        await update.message.reply_text(
            "Напиши: NOK 100 USD\n(сколько NOK конвертировать и в какую валюту)",
            reply_markup=get_menu()
        )
        return
    
    if "→ NOK" in text:
        # Кнопка меню типа "USD → NOK"
        currency = text.split()[1] if len(text.split()) > 1 else ""
        currency = currency.replace("💵", "").replace("💶", "").replace("🇺🇦", "").replace("🇷🇺", "").strip()
        await update.message.reply_text(f"Введи сумму в {currency}:", reply_markup=get_menu())
        return

    # Парсим ввод
    parts = text.upper().split()
    
    # Обратная конвертация: NOK 100 USD
    if len(parts) == 3 and parts[0] == "NOK":
        try:
            amount = float(parts[1])
            target = parts[2]
            rate = RATES.get(target)
            if rate:
                result = amount / rate
                await update.message.reply_text(
                    f"{amount} NOK = {result:.2f} {target}",
                    reply_markup=get_menu()
                )
                return
        except ValueError:
            pass
    
    # Обычная конвертация: 100 USD
    if len(parts) >= 2:
        try:
            amount = float(parts[0].replace(",", "."))
            currency = parts[1]
            
            # Проверяем русские названия
            currency_lower = text.split()[1].lower() if len(text.split()) > 1 else ""
            if currency_lower in ALIASES:
                currency = ALIASES[currency_lower]
            
            rate = RATES.get(currency)
            if rate:
                result = amount * rate
                await update.message.reply_text(
                    f"{amount} {currency} = {result:.2f} NOK",
                    reply_markup=get_menu()
                )
                return
        except (ValueError, IndexError):
            pass
    
    # Если просто число — спрашиваем валюту
    try:
        amount = float(text.replace(",", "."))
        context.user_data["amount"] = amount
        await update.message.reply_text(
            f"Сумма: {amount}\nТеперь выбери валюту:",
            reply_markup=get_menu()
        )
        return
    except ValueError:
        pass
    
    await update.message.reply_text(
        "Не понял 🤔\nНапиши например: 100 USD или 100 долларов",
        reply_markup=get_menu()
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, convert))
    print("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
