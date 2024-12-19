FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04 AS base

# Устанавливаем зависимости
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем requirements.txt для кеширования зависимостей
COPY requirements.txt /app/

# Устанавливаем зависимости только при изменении requirements.txt
RUN pip3 install -r requirements.txt

# Копируем весь код
COPY . /app

# Загружаем и кешируем SentenceTransformer
# RUN python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('deepvk/USER-bge-m3', device='cuda', cache_folder='model_cache_folder')"

CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]