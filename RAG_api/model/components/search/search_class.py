from config import API_KEY, CSE_ID, MAIN_URL
import requests
from newspaper import Article

class Searcher:
    def __init__(self):
        self.api_key = API_KEY
        self.cse_id = CSE_ID
        self.main_url = MAIN_URL
        self.params = {
            "q": None,
            "key": API_KEY,
            "cx": CSE_ID,
        }

    def get_relevant_links(self, question: str, limit: int):
        relevant_links = []
        self.params["q"] = question
        response = requests.get(self.main_url, params=self.params)
        data = response.json()
        if "items" in data:
            data = data["items"][:limit + 1]
            relevant_links = [item["link"] for item in data]

        return relevant_links

    def get_links_data(self, link: str):
        article = Article(link, fetch_images=False, request_timeout=5)
        try:
            article.download()
            article.parse()
            data = {"link": link, "title": article.title, "text": article.text}
        except:
            data = {}

        return data

    def search_context(self, question: str, limit: int):
        texts = []
        links = self.get_relevant_links(question, limit=limit)
        for link in links:
            text = self.get_links_data(link)
            if text:
                texts.append(text)

        return texts
