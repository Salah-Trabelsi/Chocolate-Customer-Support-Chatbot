from typing import List
from chromadb import PersistentClient, EmbeddingFunction, Embeddings
from langchain_openai import OpenAIEmbeddings
import json
from dotenv import load_dotenv

EMBEDDING_MODEL = "text-embedding-3-small"
DB_PATH = "./chroma_db"
FAQ_FILE_PATH = "./FAQ.json"
INVENTORY_FILE_PATH = "./inventory.json"


load_dotenv()


class Product:
    def __init__(self, name:str, id:str, description:str, price:float, type:str, origin_country:str, quantity:int):
        self.name = name
        self.id = id
        self.description = description
        self.price = price
        self.type = type
        self.origin_country = origin_country
        self.quantity = quantity


class QuestionAnswerPairs:
    def __init__(self, question: str, answer: str):
        self.question = question
        self.answer = answer


class CustomEmbeddingClass(EmbeddingFunction):
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        self.embedding_model = OpenAIEmbeddings(model=model_name)


    def __call__(self, input: List[str]) -> Embeddings:
        return self.embedding_model.embed_documents(list(input))
    


    
class ChocolateShopVectorStore:
    def __init__(self):
        db = PersistentClient(path=DB_PATH)

        custom_embedding_function = CustomEmbeddingClass()

        self.faq_collection = db.get_or_create_collection(
            name="FAQ",
            embedding_function=custom_embedding_function,
        )

        self.inventory_collection = db.get_or_create_collection(
            name="Inventory",
            embedding_function=custom_embedding_function,
        )

        if self.faq_collection.count() == 0:
            self._load_faq_collection(FAQ_FILE_PATH)

        if self.inventory_collection.count() == 0:
            self._load_inventory_collection(INVENTORY_FILE_PATH)

    def _load_faq_collection(self, faq_file_path: str):
        with open(faq_file_path, "r", encoding="utf-8") as file:
            faqs = json.load(file)

        documents = []
        ids = []
        metadatas = []

        for index, faq in enumerate(faqs):
            question = faq["question"]
            answer = faq["answer"]

            documents.append(question)
            ids.append(f"faq-question-{index}")
            metadatas.append({
                "question": question,
                "answer": answer,
                "source": "faq_question",
            })

            documents.append(answer)
            ids.append(f"faq-answer-{index}")
            metadatas.append({
                "question": question,
                "answer": answer,
                "source": "faq_answer",
            })

        self.faq_collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas,
        )

    def _load_inventory_collection(self, inventory_file_path: str):
        with open(inventory_file_path, "r", encoding="utf-8") as file:
            inventories = json.load(file)

        documents = []
        ids = []
        metadatas = []

        for inventory in inventories:
            product_id = inventory["id"]

            document = self._build_inventory_document(inventory)

            documents.append(document)
            ids.append(product_id)
            metadatas.append(inventory)

        self.inventory_collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas,
        )

    def _build_inventory_document(self, inventory: dict) -> str:
        return (
            f"Product name: {inventory.get('name', '')}. "
            f"Brand: {inventory.get('brand', '')}. "
            f"Chocolate type: {inventory.get('type', '')}. "
            f"Origin country: {inventory.get('origin_country', '')}. "
            f"Price: {inventory.get('price', '')} {inventory.get('currency', '')}. "
            f"Quantity available: {inventory.get('quantity', '')}. "
            f"Description: {inventory.get('description', '')}"
        )

    def query_faqs(self, query: str, n_results: int = 5):
        return self.faq_collection.query(
            query_texts=[query],
            n_results=n_results,
        )

    def query_inventories(self, query: str, n_results: int = 5):
        return self.inventory_collection.query(
            query_texts=[query],
            n_results=n_results,
        )
    

    def filter_products_by_price(
        self,
        max_price: float,
        currency: str,
        n_results: int = 10,
    ):
        return self.inventory_collection.get(
            where={
                "$and": [
                    {"price": {"$lte": max_price}},
                    {"currency": {"$eq": currency}},
                ]
            },
            limit=n_results,
            include=["documents", "metadatas"],
        )

###########-----##########
if __name__ == "__main__":
    vector_store = ChocolateShopVectorStore()

    print("✅ Vector store initialized successfully")
    print("FAQ count:", vector_store.faq_collection.count())
    print("Inventory count:", vector_store.inventory_collection.count())

    print("\n🔎 Testing FAQ search...")
    faq_results = vector_store.query_faqs("How can I track my order?")
    print(faq_results)

    print("\n🔎 Testing inventory search...")
    inventory_results = vector_store.query_inventories("dark Swiss chocolate")
    print(inventory_results)