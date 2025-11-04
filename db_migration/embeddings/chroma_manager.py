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
        
        # Cria o diretório se não existir
        import os
        os.makedirs(persist_directory, exist_ok=True)
        
        # Usa PersistentClient que garante persistência
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False
            )
        )
        print("✅")

        print(f"🧠 Carregando modelo de embeddings '{model_name}'...", end=" ")
        self.embedding_model = SentenceTransformer(model_name)
        print("✅")

    def create_collection(self, name: str, metadata: Optional[Dict] = None) -> chromadb.Collection:
        try:
            # ChromaDB requer pelo menos uma chave de metadata
            default_metadata = {"created_by": "migration_script"}
            if metadata:
                default_metadata.update(metadata)

            collection = self.client.get_or_create_collection(
                name=name,
                metadata=default_metadata
            )
            return collection
        except Exception as e:
            print(f"❌ Erro ao criar collection: {e}")
            raise

    def generate_embeddings(self, texts: List[str], batch_size: int = 1) -> List[List[float]]:
        """
        Gera embeddings UM POR VEZ para evitar problemas de memória
        """
        # CORREÇÃO DRÁSTICA: Sempre processa um texto por vez
        all_embeddings = []
        for text in texts:
            embedding = self.embedding_model.encode([text], convert_to_numpy=True, show_progress_bar=False)
            all_embeddings.extend(embedding.tolist())
        
        return all_embeddings

    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None,
        batch_size: int = 1
    ):
        """
        Adiciona documentos UM POR VEZ para evitar problemas de memória
        """
        collection = self.create_collection(collection_name)

        if ids is None:
            ids = [str(uuid.uuid4()) for _ in documents]

        # CORREÇÃO DRÁSTICA: Sempre processa um documento por vez
        for doc, meta, doc_id in zip(documents, metadatas, ids):
            embeddings = self.generate_embeddings([doc])
            
            collection.add(
                embeddings=embeddings,
                documents=[doc],
                metadatas=[meta],
                ids=[doc_id]
            )
            
            # Pequena pausa entre documentos
            import time
            time.sleep(0.01)

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
