# Використання легкого базового образу
FROM python:3.12-slim

# Встановлення змінної середовища
ENV APP_HOME=/app

# Встановлення робочої директорії
WORKDIR $APP_HOME

# Копіюємо тільки requirements.txt для ефективного кешування
COPY requirements.txt .

# Оновлення pip та встановлення залежностей
RUN pip install --no-cache-dir --upgrade pip && pip install -r requirements.txt

# Копіюємо весь код після встановлення залежностей
COPY . .

# Встановлюємо змінну середовища для Python (якщо потрібно)
ENV PYTHONUNBUFFERED=1

# Відкриваємо потрібні порти
EXPOSE 3000 5000

# Вказуємо команду для запуску обох серверів у фоні
CMD ["python", "main.py"]