import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import uuid

class ChromaManager:
    def __init__(self, persist_directory: str = "./chroma_db", model_name: str = "all-MiniLM-L6-v2"):
        self.persist_directory = persist_directory
        self.model_name = model_name

        print(f"🗄️  Inicializando ChromaDB...", end=" ")
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))
        print("✅")

        print(f"🧠 Carregando modelo de embeddings '{model_name}'...", end=" ")
        self.embedding_model = SentenceTransformer(model_name)
        print("✅")

    def create_collection(self, name: str, metadata: Optional[Dict] = None) -> chromadb.Collection:
        try:
            collection = self.client.get_or_create_collection(
                name=name,
                metadata=metadata or {}
            )
            return collection
        except Exception as e:
            print(f"❌ Erro ao criar collection: {e}")
            raise

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ):
        collection = self.create_collection(collection_name)

        if ids is None:
            ids = [str(uuid.uuid4()) for _ in documents]

        embeddings = self.generate_embeddings(documents)

        collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def query_similar(
        self,
        collection_name: str,
        query_text: str,
        n_results: int = 5
    ) -> Dict[str, Any]:
        collection = self.client.get_collection(collection_name)

        query_embedding = self.generate_embeddings([query_text])[0]

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )

        return results

    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        try:
            collection = self.client.get_collection(collection_name)
            count = collection.count()
            return {
                "name": collection_name,
                "count": count,
                "metadata": collection.metadata
            }
        except Exception as e:
            return {"error": str(e)}

    def list_collections(self) -> List[str]:
        collections = self.client.list_collections()
        return [col.name for col in collections]

    def delete_collection(self, collection_name: str):
        try:
            self.client.delete_collection(collection_name)
            print(f"🗑️  Collection '{collection_name}' deletada")
        except Exception as e:
            print(f"❌ Erro ao deletar collection: {e}")
