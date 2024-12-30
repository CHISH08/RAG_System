import requests
import json
import aiohttp

class LLM:
    def __init__(self, host="localhost", port=8000):
        """
        Инициализация клиента.
        :param host: Хост Llama-сервера.
        :param port: Порт Llama-сервера.
        :param initial_prompt: Начальный промпт для модели.
        """
        self.url = f"http://{host}:{port}/v1/chat/completions"
        self.initial_prompt = self.build_initial_prompt()
        self.model = "bartowski/Meta-Llama-3.1-8B-Instruct-GGUF"

    def build_initial_prompt(self):
        """
        Создаёт начальный промпт для модели с учётом задач Retrieval-Augmented Generation (RAG).
        """
        return (
            "Ты бот-ассистент, способный отвечать на вопросы пользователя, "
            "используя предоставленный контекст. Если контекст недостаточен, уточни это. "
            "Всегда давай ответы, основанные на контексте, и избегай домыслов."
            "Текст пиши в формате markdown для удобного отображения пользователю ответа."
        )

    async def ask(self, user_message, context=[], history=[]):
        messages = [{"role": "system", "content": ctx} for ctx in context]
        for entry in history:
            messages.append({"role": "user", "content": entry["question"]})
            messages.append({"role": "assistant", "content": entry["answer"]})
        messages.append({"role": "user", "content": user_message})

        payload = {"model": self.model, "messages": messages, "stream": True, "max_tokens": 1000}
        headers = {"Content-Type": "application/json"}

        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, json=payload, headers=headers) as response:
                if response.status != 200:
                    raise RuntimeError(f"Ошибка сервера: {response.status} - {await response.text()}")
                async for line in response.content:
                    yield line.decode('utf-8')
