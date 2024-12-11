import requests
import json

url = "http://localhost:8000/v1/chat/completions"

# Параметры запроса
payload = {
    "model": "bartowski/Meta-Llama-3.1-8B-Instruct-GGUF",
    "messages": [
        {
            "role": "user",
            "content": "Что такое энкодер в трансформере. из чего состоит, как реализовать"
        }
    ],
    "stream": True  # Включаем потоковый режим
}

# Заголовки запроса
headers = {
    "Content-Type": "application/json"
}

# Отправка запроса
response = requests.post(url, json=payload, headers=headers, stream=True)

# Обработка потока данных
try:
    print("Ответ модели:\n")
    for chunk in response.iter_lines(decode_unicode=False):  # Не декодируем сразу
        if chunk.strip() == b"[DONE]":  # Конец потока
            break
        if chunk.startswith(b"data: "):  # Проверяем, начинается ли строка с "data: "
            chunk = chunk[6:]  # Убираем "data: "
            try:
                # Загружаем строку как JSON
                data = json.loads(chunk.decode("utf-8"))  # Декодируем строку
                content = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                if content:  # Если есть текст, выводим его
                    print(content, end="", flush=True)
            except json.JSONDecodeError:
                continue
    print("\n\nПоток завершён.")
except KeyboardInterrupt:
    print("\nПоток прерван пользователем.")
