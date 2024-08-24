# Docker-команда FROM вказує базовий образ контейнера
# Наш базовий образ - це Linux з попередньо встановленим python-3.10
FROM python:3.12-slim

# Встановимо робочу директорію всередині контейнера
WORKDIR /app

# Скопіюємо інші файли в робочу директорію контейнера
COPY . /app

# Встановимо залежності всередині контейнера
RUN pip install -r requirements.txt

# Позначимо порт, де працює застосунок всередині контейнера
EXPOSE 5000

# Запустимо наш застосунок всередині контейнера
CMD ["python", "pyweb_hw_02_bot.py"]
