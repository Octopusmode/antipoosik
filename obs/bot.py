import requests

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота
bot_token = '432209459:AAF6Aj_Mkx3Qm8RvptnDsdFDHlRvfq9A0EM'

# Отправляем запрос к API Telegram
response = requests.get(f'https://api.telegram.org/bot{bot_token}/getUpdates')

# Парсим JSON-ответ
data = response.json()
if 'result' in data and data['result']:
    chat_id = data['result'][0]['message']['chat']['id']
    print(f'YOUR_CHAT_ID: {chat_id}')
else:
    print('Не удалось получить YOUR_CHAT_ID. Попробуйте отправить сообщение вашему боту в Telegram и повторите запрос.')