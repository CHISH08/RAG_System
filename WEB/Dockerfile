# Базовый образ с CUDA
FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04 AS base

# Установка необходимых зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    python3 \
    python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл requirements.txt и устанавливаем зависимости
COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r requirements.txt

# Копируем все файлы приложения в контейнер
COPY . /app/

# Настраиваем запуск приложения
CMD ["python3", "app.py"]
