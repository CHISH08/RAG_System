import torch
import torch.nn.functional as F

class Summarizer:
    def __init__(self, model, batch_size=8):
        self.model = model
        self.batch_size = batch_size

    def vectorize_batch(self, texts):
        embeddings = self.model.encode(texts, show_progress_bar=True, convert_to_tensor=True, normalize_embeddings=True)
        return embeddings

    def compute_cosine_similarity(self, question_embedding, paragraph_embeddings):
        question_embedding = F.normalize(question_embedding, p=2, dim=1)
        paragraph_embeddings = F.normalize(paragraph_embeddings, p=2, dim=1)
        cosine_sim = torch.mm(question_embedding, paragraph_embeddings.t())
        return cosine_sim

    def summary(self, texts, question, limit=5):
        paragraphs = "\n".join(texts).split("\n")
        paragraphs = [paragraph.strip() for paragraph in paragraphs]
        paragraphs = [paragraph for paragraph in paragraphs if len(paragraph) > 5]

        question_embedding = self.vectorize_batch([question])

        batch_embeddings = []
        for i in range(0, len(paragraphs), self.batch_size):
            batch = paragraphs[i:i + self.batch_size]
            embeddings = self.vectorize_batch(batch)
            batch_embeddings.append(embeddings)

        all_embeddings = torch.cat(batch_embeddings, dim=0)

        similarity_scores = self.compute_cosine_similarity(question_embedding, all_embeddings)

        ranked_idxs = torch.argsort(similarity_scores, descending=True).cpu().numpy().flatten()[:limit]

        ranked_paragraphs = [paragraphs[i] for i in ranked_idxs]

        return ranked_paragraphs
