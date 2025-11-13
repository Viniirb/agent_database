import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import uuid
import os
from app.config.settings import settings


class ChromaService:

    def __init__(self):
        self.persist_directory = settings.chroma_persist_directory
        self.model_name = settings.embedding_model
        self._client = None
        self._embedding_model = None

    def reset_client(self):
        self._client = None
        self.persist_directory = settings.chroma_persist_directory
        self._initialize_client()

    def _initialize_client(self):
        if self._client is None:
            os.makedirs(self.persist_directory, exist_ok=True)

            self._client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=ChromaSettings(
                    anonymized_telemetry=False
                )
            )

    def _initialize_embedding_model(self):
        if self._embedding_model is None:
            self._embedding_model = SentenceTransformer(self.model_name)

    @property
    def client(self):
        self._initialize_client()
        return self._client

    @property
    def embedding_model(self):
        self._initialize_embedding_model()
        return self._embedding_model

    def generate_embeddings(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    def list_collections(self) -> List[Dict[str, Any]]:
        """
        Lista todas as collections disponíveis no ChromaDB.

        Returns:
            Lista com informações das collections (nome e metadados)
        """
        collections = self.client.list_collections()
        return [{'name': col.name, 'metadata': col.metadata} for col in collections]

    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """
        Obtém informações sobre uma collection específica.

        Args:
            collection_name: Nome da collection

        Returns:
            Dicionário com informações da collection
        """
        try:
            collection = self.client.get_collection(collection_name)
            count = collection.count()
            return {
                "name": collection_name,
                "count": count,
                "metadata": collection.metadata
            }
        except Exception as e:
            return {"error": str(e), "name": collection_name}

    def search_across_all_collections(
        self,
        query_text: str,
        n_results: int = 5
    ) -> Dict[str, Any]:
        """
        Busca em todas as collections e retorna os resultados mais relevantes.

        Args:
            query_text: Texto da consulta
            n_results: Número de resultados por collection

        Returns:
            Dicionário com resultados agregados de todas as collections
        """
        all_results = []
        collections = self.list_collections()
        collection_names = [col['name'] for col in collections]

        query_embedding = self.generate_embeddings([query_text])[0]

        for collection_name in collection_names:
            try:
                results = self.query_collection(
                    collection_name=collection_name,
                    query_text=query_text,
                    n_results=n_results
                )

                # Adiciona o nome da collection aos resultados
                for i, doc in enumerate(results.get('documents', [[]])[0]):
                    all_results.append({
                        'collection': collection_name,
                        'document': doc,
                        'metadata': results.get('metadatas', [[]])[0][i] if results.get('metadatas') else {},
                        'distance': results.get('distances', [[]])[0][i] if results.get('distances') else None
                    })
            except Exception as e:
                # Log do erro mas continua buscando em outras collections
                print(f"Erro ao buscar na collection {collection_name}: {e}")
                continue

        # Ordena por distância (menor distância = mais similar)
        all_results.sort(key=lambda x: x.get('distance', float('inf')))

        return {
            'query': query_text,
            'total_collections_searched': len(collection_names),
            'total_results': len(all_results),
            'results': all_results[:n_results * 2]  # Retorna mais resultados agregados
        }

    def query_collection(
        self,
        collection_name: str,
        query_text: str,
        n_results: int = 5
    ) -> Dict[str, Any]:
        """
        Consulta uma collection específica.

        Args:
            collection_name: Nome da collection
            query_text: Texto da consulta
            n_results: Número de resultados a retornar

        Returns:
            Resultados da busca
        """
        collection = self.client.get_collection(collection_name)
        query_embedding = self.generate_embeddings([query_text])[0]

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )

        return results

    def get_database_schema_summary(self) -> Dict[str, Any]:
        """
        Retorna um resumo OTIMIZADO das collections disponíveis.
        Não conta documentos individuais para evitar lentidão.

        Returns:
            Resumo do schema do banco de dados
        """
        collections = self.list_collections()
        summary = {
            'total_collections': len(collections),
            'collections': []
        }

        # OTIMIZAÇÃO: Mostra apenas as primeiras 50 collections com info básica
        # Para 5000+ collections, é impraticável contar documentos de todas
        max_detailed = 50
        
        for i, col_info in enumerate(collections):
            col_name = col_info['name']
            if i < max_detailed:
                # Informações detalhadas apenas para as primeiras
                info = self.get_collection_info(col_name)
                summary['collections'].append(info)
            else:
                # Para o resto, apenas nome (sem contar documentos)
                summary['collections'].append({
                    "name": col_name,
                    "count": "não calculado (otimização)",
                    "metadata": {}
                })

        return summary

    def get_quick_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas rápidas sem acessar collections individuais.
        Ideal para grandes volumes de collections.
        """
        collections = self.list_collections()
        collection_names = [col['name'] for col in collections]
        
        # Amostra aleatória para estimativa
        sample_size = min(10, len(collection_names))
        sample_collections = collection_names[:sample_size] if collection_names else []
        
        total_docs_sample = 0
        for col_name in sample_collections:
            try:
                info = self.get_collection_info(col_name)
                if isinstance(info, dict) and 'count' in info:
                    total_docs_sample += info['count']
            except:
                continue
        
        # Estimativa baseada na amostra
        avg_docs = total_docs_sample / sample_size if sample_size > 0 else 0
        estimated_total_docs = int(avg_docs * len(collection_names))
        
        return {
            'total_collections': len(collection_names),
            'estimated_total_documents': estimated_total_docs,
            'sample_size': sample_size,
            'sample_collections': sample_collections[:5],  # Primeiras 5 para exemplo
            'note': 'Estatísticas estimadas para performance otimizada'
        }

    def search_across_collections_optimized(
        self,
        query_text: str,
        n_results: int = 3,
        max_collections: Optional[int] = 50
    ) -> Dict[str, Any]:
        """
        Busca OTIMIZADA em collections.
        Usa busca inteligente: filtra collections por palavras-chave antes de buscar.
        """
        all_results = []
        all_collections_list = self.list_collections()
        
        # OTIMIZAÇÃO INTELIGENTE: Se max_collections é None, busca por relevância
        if max_collections is None:
            # Extrai palavras-chave da query (remove stopwords básicas)
            stopwords = {'o', 'a', 'os', 'as', 'de', 'da', 'do', 'em', 'para', 'com', 'por', 'qual', 'quais', 'me', 'mostre', 'liste', 'buscar', 'encontrar'}
            keywords = [word.lower() for word in query_text.split() if word.lower() not in stopwords and len(word) > 2]
            
            # Filtra collections que contêm palavras-chave no nome
            relevant_collections = []
            for col in all_collections_list:
                col_name_lower = col['name'].lower()
                # Verifica se alguma keyword aparece no nome da collection
                if any(keyword in col_name_lower for keyword in keywords):
                    relevant_collections.append(col)
            
            # Se encontrou collections relevantes, usa elas. Senão, usa as primeiras 100
            if relevant_collections:
                collections = relevant_collections[:100]  # Limita a 100 para segurança
            else:
                collections = all_collections_list[:100]  # Fallback: primeiras 100
        else:
            collections = all_collections_list[:max_collections]
        
        collection_names = [col['name'] for col in collections]
        
        query_embedding = self.generate_embeddings([query_text])[0]

        for collection_name in collection_names:
            try:
                results = self.query_collection(
                    collection_name=collection_name,
                    query_text=query_text,
                    n_results=1  # Apenas 1 resultado por collection
                )

                # Adiciona resultado se relevante
                for i, doc in enumerate(results.get('documents', [[]])[0]):
                    all_results.append({
                        'collection': collection_name,
                        'document': doc,
                        'metadata': results.get('metadatas', [[]])[0][i] if results.get('metadatas') else {},
                        'distance': results.get('distances', [[]])[0][i] if results.get('distances') else None
                    })
            except Exception:
                continue  # Ignora erros silenciosamente para performance

        # Ordena por relevância e retorna os melhores resultados
        all_results.sort(key=lambda x: x.get('distance', float('inf')))
        
        # Retorna mais resultados se a busca for em todas as collections
        results_limit = n_results * 3 if max_collections is None else n_results

        return {
            'query': query_text,
            'collections_searched': len(collection_names),
            'total_collections_available': len(all_collections_list),
            'total_results': len(all_results),
            'results': all_results[:results_limit],
            'optimization': 'Busca em TODAS as collections' if max_collections is None else f'Busca limitada a {max_collections} collections'
        }


# Instância global do serviço
chroma_service = ChromaService()
