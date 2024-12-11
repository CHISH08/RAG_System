import asyncio
from .components import Searcher, WorkWithVBD, Summarizer, LLM
class QAModel:
    def __init__(self):
        self.searcher = Searcher()
        # self.vbd = WorkWithVBD(host="rag_api-qdrant-1", port=6333)
        # self.summariz = Summarizer(self.vbd.embedder, self.vbd.batch_size)
        # self.writer = LLM(host="llm-ollama-1", port=11434)
        self.writer = LLM()
        self.vbd = WorkWithVBD("localhost", 6333)

    async def __call__(self, question: str, history: list=[], limit_context=2, limit_summary=40, threshold=0.5):
        context = self.vbd.search(question, limit=limit_context, threshold=threshold)

        if len(context) == 0:
            context = [elem['text'][:1000] for elem in self.searcher.search_context(question, limit=limit_context)]
            self.vbd.add_to_collection(texts=context)
            # ans = self.summariz.summary(ans, question, limit_summary)

        context = [cxt[:1000] for cxt in context]

        response_generator = self.writer.ask(question, context, history=history)

        async for partial_answer in response_generator:
            yield partial_answer
