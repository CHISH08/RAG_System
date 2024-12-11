import requests
import json

def test_stream():
    url = "http://localhost:8001/stream"
    payload = {"question": "Как программировать?"}

    with requests.post(url, json=payload, stream=True) as response:
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

test_stream()
