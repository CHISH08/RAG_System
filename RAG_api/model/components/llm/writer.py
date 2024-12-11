import aiohttp
import asyncio
import json

class LLM:
    def __init__(
        self,
        model_name: str = "hf.co/bartowski/Qwen2.5.1-Coder-7B-Instruct-GGUF:IQ4_XS",
        host: str = "llm-ollama-1",
        port: int = 11434
    ):
        """
        Инициализация клиента модели.

        :param model_name: Название модели для использования.
        :param host: Хост, на котором запущен API сервера.
        :param port: Порт API сервера.
        """
        self.model_name = model_name
        self.api_url = f"http://{host}:{port}/api/chat"
        self.headers = {
            "Content-Type": "application/json",
        }
        self.prompt = self._generate_prompt()

    def _generate_prompt(self) -> str:
        """
        Генерация системного промпта для модели.

        :return: Строка с системным промптом.
        """
        return """
        Ты ассистент, который отвечает на разнообразные вопросы пользователей.
        Твоя задача — отвечать на вопросы пользователя на основе предоставленного тебе контекста.
        Не упоминай сам контекст, просто отвечай на вопрос.
        """

    async def stream_response(self, messages: list, max_tokens: int = 500):
        """
        Асинхронный генератор для получения стримингового ответа от модели.

        :param messages: Список сообщений для отправки модели.
        :param max_tokens: Максимальное количество токенов в ответе.
        :yield: Часть ответа от модели.
        """
        request_data = {
            "messages": messages,
            "max_tokens": max_tokens,
            "model": self.model_name,
            "stream": True  # Включаем стриминг
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, headers=self.headers, json=request_data) as response:
                    if response.status != 200:
                        text = await response.text()
                        raise Exception(f"Ошибка: {response.status} - {text}")

                    content_type = response.headers.get('Content-Type', '')
                    if 'application/x-ndjson' in content_type:
                        # Обработка как NDJSON
                        async for line in response.content:
                            line_str = line.decode('utf-8').strip()
                            if line_str:
                                try:
                                    data_json = json.loads(line_str)
                                    message = data_json.get("message", {})
                                    content = message.get("content", "")
                                    if content:
                                        yield content  # Возвращаем часть ответа
                                    if data_json.get("done", False):
                                        break
                                except json.JSONDecodeError as e:
                                    raise Exception(f"Ошибка декодирования JSON: {e}")
                                except Exception as e:
                                    raise Exception(f"Ошибка при обработке данных: {e}")
                    elif 'text/event-stream' in content_type:
                        # Обработка как SSE (Server-Sent Events), если необходимо
                        async for line in response.content:
                            line_str = line.decode('utf-8').strip()
                            if line_str.startswith("data: "):
                                data = line_str[len("data: "):]
                                if data == "[DONE]":
                                    break
                                try:
                                    data_json = json.loads(data)
                                    content = data_json.get("message", {}).get("content", "")
                                    if content:
                                        yield content
                                except json.JSONDecodeError as e:
                                    raise Exception(f"Ошибка декодирования JSON в SSE: {e}")
                    else:
                        raise Exception(f"Неподдерживаемый Content-Type: {content_type}")

        except aiohttp.ClientError as e:
            raise Exception(f"Ошибка подключения: {e}")

    async def ask(self, context: str, question: str, history: list = []):
        """
        Основной метод для взаимодействия с моделью.

        :param context: Контекст, на основе которого модель должна отвечать.
        :param question: Вопрос пользователя.
        :param history: История взаимодействий (список словарей с ключами 'question' и 'answer').
        :yield: Часть ответа от модели.
        """
        # Формирование списка сообщений
        messages = [
            {"role": "system", "content": self.prompt}
        ]

        if context:
            messages.append({"role": "system", "content": context})

        for entry in history:
            user_q = entry.get("question", "")
            assistant_a = entry.get("answer", "")
            if user_q:
                messages.append({"role": "user", "content": user_q})
            if assistant_a:
                messages.append({"role": "assistant", "content": assistant_a})

        messages.append({"role": "user", "content": question})

        # Получение ответа от модели через stream_response
        async for chunk in self.stream_response(messages, max_tokens=1000):
            yield chunk
