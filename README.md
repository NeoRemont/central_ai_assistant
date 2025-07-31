# Центральный нейросотрудник (ДРСотрудник)

## Возможности:
- Принимает текстовые и голосовые команды через Telegram
- Использует GPT-4 Turbo для ответа
- Распознаёт голос с помощью Whisper API
- Полностью готов к деплою на Render

## Установка вручную:
1. Установите зависимости:
```
pip install -r requirements.txt
```
2. Скопируйте `.env.example` → `.env` и вставьте ключи
3. Запустите:
```
uvicorn main:app --reload
```

## Деплой на Render:
- Подключите GitHub-репозиторий
- Установите переменные окружения:
  - `TELEGRAM_BOT_TOKEN`
  - `OPENAI_API_KEY`
  - `WHISPER_LANGUAGE=ru`
  - `USE_WHISPER_API=True`
  - `GPT_MODEL=gpt-4-turbo`
  - `PORT=10000`
- Стартовая команда: `uvicorn main:app --host=0.0.0.0 --port=10000`
