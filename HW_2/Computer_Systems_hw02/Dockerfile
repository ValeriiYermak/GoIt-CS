# Використання легкого базового образу
FROM python:3.12-slim

# Встановлення змінної середовища
ENV APP_HOME=/app

# Встановлення робочої директорії
WORKDIR $APP_HOME

# Встановлення необхідних пакетів для компіляції залежностей
RUN apt-get update && apt-get install -y \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Копіюємо тільки requirements.txt для ефективного кешування
COPY requirements.txt .

# Оновлення pip та встановлення залежностей
RUN pip install --no-cache-dir --upgrade pip && pip install -r requirements.txt

# Копіюємо весь інший код
COPY . .

# Вказуємо порт для документації (це не відкриває порт, а лише позначає)
EXPOSE 8000

# Запускаємо додаток
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

