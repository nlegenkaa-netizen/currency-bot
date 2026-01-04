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
    "UAH": 0.25,
    "GBP": 13.2,
    "SEK": 0.95,
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
    context.user_data.clear()
    await update.message.reply_text(
        "Привет! Я конвертер валют 💱\n\n"
        "Напиши сумму и валюту:\n"
        "• 100 USD или 100 долларов\n"
        "• 50 EUR или 50 евро\n"
        "• 1000 UAH или 1000 гривен\n\n"
        "Или выбери валюту в меню 👇",
        reply_markup=get_menu()
    )

async def show_rates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lines = ["📋 Текущие курсы (к NOK):\n"]
    for currency, rate in RATES.items():
        lines.append(f"1 {currency} = {rate} NOK")
    await update.message.reply_text("\n".join(lines), reply_markup=get_menu())

async def convert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    # Кнопка "Все курсы"
    if "Все курсы" in text:
        await show_rates(update, context)
        return
    
    # Кнопка "NOK → другую"
    if "NOK → другую" in text:
        context.user_data["mode"] = "from_nok"
        context.user_data["currency"] = None
        await update.message.reply_text(
            "Введи сумму в NOK и валюту:\nНапример: 100 USD",
            reply_markup=get_menu()
        )
        return
    
    # Кнопки валют → NOK
    if "→ NOK" in text:
        if "USD" in text:
            context.user_data["currency"] = "USD"
        elif "EUR" in text:
            context.user_data["currency"] = "EUR"
        elif "UAH" in text:
            context.user_data["currency"] = "UAH"
        elif "RUB" in text:
            context.user_data["currency"] = "RUB"
        
        currency = context.user_data.get("currency")
        if currency:
            context.user_data["mode"] = "to_nok"
            await update.message.reply_text(
                f"Введи сумму в {currency}:",
                reply_markup=get_menu()
            )
        return
    
    # Проверяем, есть ли сохранённая валюта (после нажатия кнопки)
    saved_currency = context.user_data.get("currency")
    mode = context.user_data.get("mode")
    
    # Пробуем распарсить число
    try:
        amount = float(text.replace(",", ".").replace(" ", ""))
        
        if saved_currency and mode == "to_nok":
            # Конвертация в NOK
            rate = RATES.get(saved_currency)
            result = amount * rate
            await update.message.reply_text(
                f"{amount} {saved_currency} = {result:.2f} NOK",
                reply_markup=get_menu()
            )
            context.user_data.clear()
            return
        
        if mode == "from_nok":
            # Ждём валюту для обратной конвертации
            context.user_data["amount"] = amount
            await update.message.reply_text(
                f"Сумма: {amount} NOK\nТеперь напиши валюту (USD, EUR, UAH...)",
                reply_markup=get_menu()
            )
            return
            
    except ValueError:
        pass
    
    # Парсим "100 USD" или "100 долларов"
    parts = text.split()
    if len(parts) >= 2:
        try:
            amount = float(parts[0].replace(",", "."))
            currency_input = parts[1].upper()
            
            # Проверяем русские названия
            currency_lower = parts[1].lower()
            if currency_lower in ALIASES:
                currency_input = ALIASES[currency_lower]
            
            # Обратная конвертация: из NOK
            if mode == "from_nok" or (len(parts) == 2 and context.user_data.get("amount")):
                saved_amount = context.user_data.get("amount", amount)
                rate = RATES.get(currency_input)
                if rate:
                    result = saved_amount / rate
                    await update.message.reply_text(
                        f"{saved_amount} NOK = {result:.2f} {currency_input}",
                        reply_markup=get_menu()
                    )
                    context.user_data.clear()
                    return
            
            # Обычная конвертация в NOK
            rate = RATES.get(currency_input)
            if rate:
                result = amount * rate
                await update.message.reply_text(
                    f"{amount} {currency_input} = {result:.2f} NOK",
                    reply_markup=get_menu()
                )
                context.user_data.clear()
                return
                
        except (ValueError, IndexError):
            pass
    
    # Проверяем, может это просто валюта для обратной конвертации
    if mode == "from_nok" and context.user_data.get("amount"):
        currency_input = text.upper().strip()
        if currency_input in RATES:
            amount = context.user_data["amount"]
            result = amount / RATES[currency_input]
            await update.message.reply_text(
                f"{amount} NOK = {result:.2f} {currency_input}",
                reply_markup=get_menu()
            )
            context.user_data.clear()
            return
    
    await update.message.reply_text(
        "Не понял 🤔\nВыбери валюту в меню или напиши: 100 USD",
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
