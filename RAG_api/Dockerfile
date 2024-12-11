# Базовый образ Python
FROM python:3.10-slim

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копируем только requirements для кеширования установки зависимостей
COPY requirements/requirements.txt ./requirements.txt

# Устанавливаем зависимости Python
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в контейнер
COPY . .

# Загружаем и сохраняем модель user-bge-m3 при сборке контейнера
RUN python -c "from sentence_transformers import SentenceTransformer; model = SentenceTransformer('deepvk/USER-bge-m3'); model.save('./saved_models/user_bge_m3')"

# Указываем, что модель будет загружаться из сохраненной директории
ENV MODEL_DIR=/app/saved_models/user_bge_m3

# Открываем порт для API
EXPOSE 8000

# Запуск сервера API
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
