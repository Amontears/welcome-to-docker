# Указываем базовый образ с Python 3.12.2
FROM python:3.12.2

# Устанавливаем зависимости
RUN pip install Flask

# Копируем файлы в контейнер
COPY . /app
WORKDIR /app

# Запускаем приложение
CMD ["python", "app.py"]
