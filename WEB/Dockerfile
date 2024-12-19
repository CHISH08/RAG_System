FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04 AS base

# Установка минимальных зависимостей, включая Python
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    python3 \
    python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл requirements.txt для установки зависимостей
COPY requirements.txt /app/

# Устанавливаем зависимости
RUN pip3 install --no-cache-dir -r requirements.txt

# Копируем остальные файлы приложения
COPY . /app/

# Настраиваем запуск приложения
CMD ["python3", "app.py"]
