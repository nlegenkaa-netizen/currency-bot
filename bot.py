# Мой первый бот - конвертер валют
print("Привет! Я бот-конвертер валют") 

# Курсы валют к норвежской кроне (NOK)
RATES = {
    "USD": 10.5,   # 1 доллар = 10.5 крон
    "EUR": 11.4,   # 1 евро = 11.4 крон
    "RUB": 0.11,   # 1 рубль = 0.11 крон
} 

def convert(amount, currency):
    """Конвертирует валюту в NOK"""
    rate = RATES.get(currency)
    if rate:
        return amount * rate
    return None 

    # Тестируем
result = convert(100, "USD")
print(f"100 USD = {result} NOK") 



