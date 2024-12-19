import requests
import json

def test_stream():
    url = "http://localhost:8001/stream"
    payload = {"question": "Как программировать?"}

    with requests.post(url, json=payload, stream=True) as response:
        for chunk in response.iter_lines(decode_unicode=False):
            if chunk.strip() == b"[DONE]":
                break
            if chunk.startswith(b"data: "):
                chunk = chunk[6:]
                try:
                    data = json.loads(chunk.decode("utf-8"))
                    content = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                    if content:
                        print(content, end="", flush=True)
                except json.JSONDecodeError:
                    continue

test_stream()
