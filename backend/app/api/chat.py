from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
import google.generativeai as genai
from app.config.settings import settings
from app.services.chroma_service import chroma_service

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    search_collections: Optional[List[str]] = None  # Collections específicas para buscar
    max_results: int = 3  # REDUZIDO: Máximo 3 resultados para economizar tokens

class SearchResult(BaseModel):
    collection: str
    document: str
    metadata: Dict[str, Any]
    distance: Optional[float] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    search_results: List[SearchResult] = []
    collections_searched: int = 0
    model_used: Optional[str] = None  # Indica qual modelo foi usado

# Configura a API do Google Gemini
genai.configure(api_key=settings.google_api_key)

# Configurações dos modelos
GEMINI_PRO_MODEL = "gemini-2.5-pro"
GEMINI_FLASH_MODEL = "gemini-2.5-flash"

# Configurações otimizadas para economizar tokens
generation_config = {
    "temperature": 0.3,  # Menos criativo, mais direto
    "top_p": 0.8,        # Mais focado
    "top_k": 20,         # Menos variação  
    "max_output_tokens": 800,  # REDUZIDO: máximo 800 tokens por resposta
}

# Configurações de segurança
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
]

# Cache simples para respostas comuns (economiza tokens)
_response_cache = {
    "quantas tabelas": f"O banco possui {chroma_service.list_collections().__len__() if chroma_service else '5707'} tabelas migradas no ChromaDB.",
    "tabelas existem": "Existem milhares de tabelas migradas. Use consultas específicas como 'tabela usuario' para melhores resultados.",
    "lista tabelas": "Para performance, não listo todas as tabelas. Consulte uma tabela específica pelo nome."
}

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Endpoint de chat que consulta o ChromaDB e usa Gemini para gerar respostas.
    Tenta usar Gemini 2.5 Pro primeiro, com fallback para Gemini 2.5 Flash.
    """
    try:
        # Gera ou usa conversation_id existente
        conversation_id = request.conversation_id or str(uuid.uuid4())

        # Busca informações relevantes no ChromaDB
        search_results = []
        if request.search_collections:
            # Busca em collections específicas
            for collection_name in request.search_collections:
                try:
                    results = chroma_service.query_collection(
                        collection_name=collection_name,
                        query_text=request.message,
                        n_results=request.max_results
                    )
                    # Processa resultados
                    for i, doc in enumerate(results.get('documents', [[]])[0]):
                        search_results.append({
                            'collection': collection_name,
                            'document': doc,
                            'metadata': results.get('metadatas', [[]])[0][i] if results.get('metadatas') else {},
                            'distance': results.get('distances', [[]])[0][i] if results.get('distances') else None
                        })
                except Exception as e:
                    print(f"Erro ao buscar na collection {collection_name}: {e}")
        else:
            # OTIMIZADO: Busca inteligente com limite reduzido
            # Para 5000+ collections, limita a busca para melhor performance
            results = chroma_service.search_across_collections_optimized(
                query_text=request.message,
                n_results=request.max_results,
                max_collections=50  # Busca apenas nas primeiras 50 collections
            )
            search_results = results.get('results', [])

        # Verifica cache primeiro (economiza tokens)
        message_lower = request.message.lower()
        cached_response = None
        
        for key, response in _response_cache.items():
            if key in message_lower:
                cached_response = response
                break
        
        if cached_response:
            response_text = cached_response
            model_used = "cache"
        else:
            # Prepara o contexto para o Gemini (se não tem cache)
            context = _prepare_context(search_results)

            # Gera resposta usando Gemini com fallback
            response_text, model_used = await _generate_gemini_response(
                user_message=request.message,
                context=context
            )

        return ChatResponse(
            response=response_text,
            conversation_id=conversation_id,
            search_results=[SearchResult(**result) for result in search_results[:10]],  # Limita a 10 resultados
            collections_searched=len(set([r['collection'] for r in search_results])),
            model_used=model_used
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar chat: {str(e)}")


def _prepare_context(search_results: List[Dict[str, Any]]) -> str:
    """
    Prepara contexto OTIMIZADO - mais conciso para economizar tokens.
    """
    if not search_results:
        return "Nenhuma informação encontrada no banco."

    # OTIMIZADO: Contexto mais enxuto
    context_parts = ["Dados encontrados:"]

    for i, result in enumerate(search_results[:3], 1):  # Máximo 3 resultados
        doc = result['document']
        
        # Trunca documentos muito longos
        if len(doc) > 200:
            doc = doc[:200] + "..."
        
        context_parts.append(f"\n{i}. {doc}")
        
        # Adiciona apenas metadata essencial
        metadata = result.get('metadata', {})
        if metadata.get('row_count'):
            context_parts.append(f"   ({metadata['row_count']} registros)")

    return "\n".join(context_parts)


async def _generate_gemini_response(user_message: str, context: str) -> tuple[str, str]:
    """
    Gera resposta usando o Google Gemini.
    Tenta primeiro com Gemini 2.5 Pro, se falhar usa Gemini 2.5 Flash como fallback.

    Returns:
        tuple: (resposta_texto, modelo_usado)
    """
    system_prompt = """Assistente de banco de dados SQL Server. Responda de forma direta e concisa baseado no contexto fornecido. Se não souber, diga claramente."""

    full_prompt = f"{system_prompt}\n\n{context}\n\nPergunta do usuário: {user_message}"

    # Tenta primeiro com Gemini 2.5 Pro
    try:
        model = genai.GenerativeModel(
            model_name=GEMINI_PRO_MODEL,
            generation_config=generation_config,
            safety_settings=safety_settings
        )

        response = model.generate_content(full_prompt)
        return response.text, GEMINI_PRO_MODEL

    except Exception as e:
        error_message = str(e).lower()

        # Verifica se é erro de limite de uso (quota/rate limit)
        if any(keyword in error_message for keyword in ['quota', 'rate limit', 'resource exhausted', '429']):
            print(f"⚠️  Gemini Pro atingiu limite de uso, usando Gemini Flash como fallback: {e}")

            # Fallback para Gemini 2.5 Flash
            try:
                model = genai.GenerativeModel(
                    model_name=GEMINI_FLASH_MODEL,
                    generation_config=generation_config,
                    safety_settings=safety_settings
                )

                response = model.generate_content(full_prompt)
                return response.text, GEMINI_FLASH_MODEL

            except Exception as flash_error:
                flash_error_message = str(flash_error).lower()

                # Se Flash também atingiu o limite
                if any(keyword in flash_error_message for keyword in ['quota', 'rate limit', 'resource exhausted', '429']):
                    return (
                        "Desculpe, ambos os modelos (Gemini Pro e Flash) atingiram o limite de uso no momento. "
                        "Por favor, aguarde alguns minutos e tente novamente.",
                        "none"
                    )
                else:
                    return f"Erro ao gerar resposta com Gemini Flash: {flash_error}", "error"
        else:
            # Erro diferente de limite de uso
            return f"Erro ao gerar resposta com Gemini Pro: {e}", "error"


@router.get("/collections")
async def list_collections():
    """
    Lista todas as collections disponíveis no ChromaDB.
    """
    try:
        collections = chroma_service.list_collections()
        return {
            "total": len(collections),
            "collections": collections
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar collections: {str(e)}")


@router.get("/collections/{collection_name}")
async def get_collection_info(collection_name: str):
    """
    Obtém informações sobre uma collection específica.
    """
    try:
        info = chroma_service.get_collection_info(collection_name)
        if "error" in info:
            raise HTTPException(status_code=404, detail=info["error"])
        return info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter informações da collection: {str(e)}")


@router.get("/schema")
async def get_database_schema():
    """
    Retorna um resumo do schema do banco de dados (primeiras 50 collections).
    Para performance, não retorna todas as 5000+ collections de uma vez.
    """
    try:
        schema = chroma_service.get_database_schema_summary()
        return schema
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter schema: {str(e)}")


@router.get("/stats")
async def get_quick_stats():
    """
    Retorna estatísticas rápidas do banco de dados.
    Otimizado para grandes volumes de collections.
    """
    try:
        stats = chroma_service.get_quick_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter estatísticas: {str(e)}")