from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

class WorkWithVBD:
    def __init__(self, host: str, port: int, embedder_name="deepvk/USER-bge-m3", collection_name="qdrant_collection", batch_size=64):
        self.__connect(host, port)
        self.embedder = SentenceTransformer(embedder_name, device="cuda")
        check_collection_existence = self.__check_collection_existence(collection_name)
        if not check_collection_existence:
            self.create_collection(collection_name)

        self.collection_name = collection_name
        self.batch_size = batch_size

    def __connect(self, host, port):
        self.client = QdrantClient(host=host, port=port)
        self.__check_connect()

    def __check_connect(self):
        server_info = self.client.info()
        if server_info:
            print("Подключение к Qdrant установлено!")
            print(server_info)
        else:
            print("Не удалось получить информацию о сервере.")

    def create_collection(self, collection_name: str):
        self.client.recreate_collection(
            collection_name=collection_name,
            vectors_config={
                "size": self.embedder.get_sentence_embedding_dimension(),
                "distance": "Cosine"
            }
        )

    def update_collection(self, collection_name: str = "qdrant_collection"):
        self.client.delete_collection(collection_name=collection_name)
        self.create_collection(collection_name)

    def __check_collection_existence(self, collection_name: str):
        collections = self.client.get_collections()
        collection_names = [collection.name for collection in collections.collections]

        return collection_name in collection_names

    def add_to_collection(self, texts: list[str]):
        collection_info = self.client.count(collection_name=self.collection_name)
        current_count = collection_info.count

        ids = list(range(current_count, current_count + len(texts)))

        for i in tqdm(range(0, len(texts), self.batch_size), desc="Загрузка данных"):
            batch_texts = texts[i:i + self.batch_size]
            batch_ids = ids[i:i + self.batch_size]
            batch_vectors = self.embedder.encode(batch_texts, normalize_embeddings=True)

            points = [
                PointStruct(
                    id=id_,
                    vector=vector,
                    payload={"text": text}
                )
                for id_, vector, text in zip(batch_ids, batch_vectors, batch_texts)
            ]

            self.client.upsert(collection_name=self.collection_name, points=points)

        print("Данные успешно добавлены.")

    def search(self, question: str, limit: int, threshold: float):
        question_text = question
        question_vector = self.embedder.encode(question_text, normalize_embeddings=True)

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=question_vector,
            limit=limit,
            with_payload=True
        )

        filtered_results = [
            res.payload.get("text", "")
            for res in results if res.score >= threshold
        ]

        return filtered_results
