from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
import google.generativeai as genai
import logging

from app.config.settings import settings
from app.services.chroma_service import chroma_service
from app.services.toons_service import toons_optimizer
from app.services.cache_service import cache_service
from app.utils.rate_limiter import rate_limiter

logger = logging.getLogger(__name__)
router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    search_collections: Optional[List[str]] = None
    max_results: int = 3


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
    model_used: Optional[str] = None
    token_optimization: Optional[Dict[str, Any]] = None
    from_cache: bool = False


class Message(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ConversationHistory(BaseModel):
    conversation_id: str
    messages: List[Message]
    total_messages: int

genai.configure(api_key=settings.google_api_key)

# Modelos otimizados para tier gratuito (baseado em limites disponíveis)
# gemini-2.0-flash-lite: 15 RPM, 1M TPM, 1K RPD (MELHOR opção gratuita)
# gemini-2.5-flash: 15 RPM, 250K TPM, 200 RPD
# gemini-2.0-flash: 15 RPM, 1M TPM, 200 RPD
GEMINI_PRIMARY_MODEL = "gemini-2.0-flash-lite"  # Limites maiores
GEMINI_SECONDARY_MODEL = "gemini-2.5-flash"     # Fallback 1
GEMINI_TERTIARY_MODEL = "gemini-2.0-flash"      # Fallback 2

generation_config = {
    "temperature": 0.3,
    "top_p": 0.8,
    "top_k": 20,
    "max_output_tokens": 800,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# Cache expandido de respostas simples e óbvias (EVITA chamadas à API)
_simple_responses = {
    # Saudações
    "oi": "Olá! Bem-vindo ao Agent Database. Como posso ajudá-lo?",
    "ola": "Olá! Bem-vindo ao Agent Database. Como posso ajudá-lo?",
    "olá": "Olá! Bem-vindo ao Agent Database. Como posso ajudá-lo?",
    "hello": "Hello! Welcome to Agent Database. How can I help?",
    "hi": "Hi! Welcome to Agent Database. How can I help?",
    "hey": "Hey! Welcome to Agent Database. How can I help?",
    "bom dia": "Bom dia! Como posso ajudá-lo com o banco de dados hoje?",
    "boa tarde": "Boa tarde! Como posso ajudá-lo com o banco de dados?",
    "boa noite": "Boa noite! Como posso ajudá-lo com o banco de dados?",

    # Agradecimentos
    "obrigado": "De nada! Estou aqui para ajudar com consultas no banco de dados.",
    "obrigada": "De nada! Estou aqui para ajudar com consultas no banco de dados.",
    "valeu": "De nada! Precisa de mais alguma coisa?",
    "thanks": "You're welcome! I'm here to help with database queries.",
    "thank you": "You're welcome! I'm here to help with database queries.",
    "thx": "You're welcome!",

    # Informações sobre o assistente
    "qual seu nome": "Sou o Agent Database, seu assistente para consultas em banco de dados.",
    "qual é seu nome": "Sou o Agent Database, seu assistente para consultas em banco de dados.",
    "quem é você": "Sou o Agent Database, seu assistente para consultas em banco de dados.",
    "quem e voce": "Sou o Agent Database, seu assistente para consultas em banco de dados.",
    "who are you": "I'm Agent Database, your assistant for database queries.",
    "what's your name": "I'm Agent Database, your assistant for database queries.",

    # Funcionamento
    "como você funciona": "Sou um assistente que busca informações no seu banco de dados e usa IA para responder suas perguntas.",
    "como voce funciona": "Sou um assistente que busca informações no seu banco de dados e usa IA para responder suas perguntas.",
    "how do you work": "I'm an assistant that searches your database and uses AI to answer your questions.",
    "what can you do": "I can help you query and understand data in your SQL Server database.",
    "o que você faz": "Eu ajudo você a consultar e entender dados no seu banco SQL Server.",

    # Despedidas
    "tchau": "Até logo! Volte sempre que precisar de ajuda com o banco de dados.",
    "ate logo": "Até logo! Fico à disposição.",
    "até logo": "Até logo! Fico à disposição.",
    "bye": "Goodbye! Come back if you need help with the database.",
    "goodbye": "Goodbye! Come back anytime.",

    # Outros
    "ok": "Certo! Há algo mais em que posso ajudar?",
    "teste": "Sistema funcionando! Estou pronto para ajudar com consultas no banco de dados.",
    "test": "System working! I'm ready to help with database queries.",
}

def _check_simple_response(message: str) -> Optional[str]:
    """Verifica se é uma pergunta simples e retorna resposta do cache."""
    message_lower = message.lower().strip()
    
    # Busca exata
    if message_lower in _simple_responses:
        return _simple_responses[message_lower]
    
    # Busca parcial para mensagens com pontuação
    for key, response in _simple_responses.items():
        if message_lower.startswith(key) and len(message_lower) <= len(key) + 1:
            return response
    
    return None

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        conversation_id = request.conversation_id or str(uuid.uuid4())
        logger.info(f"Iniciando chat: conversation_id={conversation_id}, message_length={len(request.message)}")
        
        # Verifica se é uma pergunta simples primeiro
        simple_response = _check_simple_response(request.message)
        if simple_response:
            logger.info("Resposta simples encontrada no cache")
            return ChatResponse(
                response=simple_response,
                conversation_id=conversation_id,
                search_results=[],
                collections_searched=0,
                model_used="simple_cache",
                token_optimization={"cached": True},
                from_cache=True
            )
        
        # Tenta recuperar do cache Redis primeiro
        cached_response = cache_service.get_cached_response(
            message=request.message,
            conversation_id=conversation_id
        )
        
        if cached_response:
            logger.info(f"Resposta recuperada do cache Redis: {conversation_id}")
            return ChatResponse(
                response=cached_response.get("response", ""),
                conversation_id=conversation_id,
                search_results=[SearchResult(**r) for r in cached_response.get("search_results", [])[:10]],
                collections_searched=cached_response.get("collections_searched", 0),
                model_used="redis_cache",
                token_optimization={"from_cache": True},
                from_cache=True
            )
        
        search_results = []
        if request.search_collections:
            for collection_name in request.search_collections:
                try:
                    results = chroma_service.query_collection(
                        collection_name=collection_name,
                        query_text=request.message,
                        n_results=request.max_results
                    )
                    for i, doc in enumerate(results.get('documents', [[]])[0]):
                        search_results.append({
                            'collection': collection_name,
                            'document': doc,
                            'metadata': results.get('metadatas', [[]])[0][i] if results.get('metadatas') else {},
                            'distance': results.get('distances', [[]])[0][i] if results.get('distances') else None
                        })
                except Exception as e:
                    logger.error(f"Erro ao buscar na collection {collection_name}: {e}")
        else:
            results = chroma_service.search_across_collections_optimized(
                query_text=request.message,
                n_results=request.max_results,
                max_collections=50
            )
            search_results = results.get('results', [])
        
        logger.info(f"Busca em ChromaDB completada: {len(search_results)} resultados encontrados")
        
        # Sempre passa para Gemini, inclusive para perguntas simples
        context = _prepare_context(search_results)
        response_text, model_used, optimization_result = await _generate_gemini_response(
            user_message=request.message,
            context=context
        )

        # Salvar no cache Redis
        cache_service.save_conversation(conversation_id)
        cache_service.add_message_to_conversation(
            conversation_id=conversation_id,
            role="user",
            content=request.message
        )
        cache_service.add_message_to_conversation(
            conversation_id=conversation_id,
            role="assistant",
            content=response_text,
            metadata={"model": model_used}
        )
        cache_service.cache_chat_response(
            message=request.message,
            response=response_text,
            conversation_id=conversation_id,
            metadata={
                "model": model_used,
                "collections_searched": len(set([r['collection'] for r in search_results]))
            },
            ttl=settings.cache_ttl
        )

        return ChatResponse(
            response=response_text,
            conversation_id=conversation_id,
            search_results=[SearchResult(**result) for result in search_results[:10]],
            collections_searched=len(set([r['collection'] for r in search_results])),
            model_used=model_used,
            token_optimization=optimization_result,
            from_cache=False
        )

    except Exception as e:
        logger.error(f"Erro geral no endpoint /chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar chat: {str(e)}")


def _prepare_context(search_results: List[Dict[str, Any]]) -> str:
    if not search_results:
        return "Nenhuma informação encontrada no banco."

    context_parts = ["Dados encontrados:"]

    for i, result in enumerate(search_results[:3], 1):
        doc = result['document']
        
        if len(doc) > 200:
            doc = doc[:200] + "..."
        
        context_parts.append(f"\n{i}. {doc}")
        
        metadata = result.get('metadata', {})
        if metadata.get('row_count'):
            context_parts.append(f"   ({metadata['row_count']} registros)")

    return "\n".join(context_parts)


async def _generate_gemini_response(user_message: str, context: str) -> tuple[str, str, Dict[str, Any]]:
    system_prompt = """Assistente de banco de dados SQL Server. Responda de forma direta e concisa baseado no contexto fornecido. Se não souber, diga claramente."""

    # Otimiza o prompt usando TOONS
    optimization_result = toons_optimizer.optimize_prompt(system_prompt, context, user_message)
    optimized_prompt = optimization_result["optimized_prompt"]

    logger.info(f"Prompt otimizado: original={optimization_result['original_size']} chars, "
               f"otimizado={optimization_result['optimized_size']} chars, "
               f"tokens_economizados_estimado={optimization_result['tokens_saved_estimate']}")

    # Sistema de fallback em cascata: tenta Primary -> Secondary -> Tertiary
    models_to_try = [
        (GEMINI_PRIMARY_MODEL, "primary"),
        (GEMINI_SECONDARY_MODEL, "secondary"),
        (GEMINI_TERTIARY_MODEL, "tertiary")
    ]

    for model_name, model_type in models_to_try:
        try:
            logger.info(f"Tentando modelo {model_type}: {model_name}")

            # Aguarda rate limiter antes de fazer a requisição
            await rate_limiter.acquire(model_name)

            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config,
                safety_settings=safety_settings
            )

            response = model.generate_content(optimized_prompt)

            # Verifica se a resposta é válida
            try:
                response_text = response.text
                if response_text and response_text.strip():
                    logger.info(f"✓ Resposta gerada com sucesso usando {model_name} ({model_type})")
                    return response_text, model_name, optimization_result
            except (AttributeError, ValueError):
                logger.warning(f"⚠️  {model_name} retornou resposta vazia/bloqueada")
                continue

        except Exception as e:
            error_message = str(e).lower()

            # Se for erro de quota/rate limit, tenta próximo modelo
            if any(keyword in error_message for keyword in ['quota', 'rate limit', 'resource exhausted', '429']):
                logger.warning(f"⚠️  {model_name} atingiu limite de rate, tentando próximo modelo...")
                continue

            # Se for erro de segurança, tenta próximo modelo
            elif any(keyword in error_message for keyword in ['safety', 'blocked', 'invalid operation']):
                logger.warning(f"⚠️  {model_name} bloqueou a requisição, tentando próximo modelo...")
                continue

            # Outros erros, também tenta próximo modelo
            else:
                logger.error(f"Erro em {model_name}: {e}")
                continue

    # Se todos os modelos falharam
    logger.error("❌ Todos os modelos falharam ou atingiram limites")
    error_msg = ("Desculpe, todos os modelos estão temporariamente indisponíveis devido a limites de uso. "
                "Por favor, aguarde alguns segundos e tente novamente.")
    return error_msg, "all_failed", optimization_result


@router.get("/collections")
async def list_collections():
    try:
        collections = chroma_service.list_collections()
        return {"total": len(collections), "collections": collections}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collections/{collection_name}")
async def get_collection_info(collection_name: str):
    try:
        info = chroma_service.get_collection_info(collection_name)
        if "error" in info:
            raise HTTPException(status_code=404, detail=info["error"])
        return info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schema")
async def get_database_schema():
    try:
        schema = chroma_service.get_database_schema_summary()
        return schema
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_quick_stats():
    try:
        return chroma_service.get_quick_stats()
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/toons-stats")
async def get_toons_statistics():
    try:
        stats = toons_optimizer.get_statistics()
        return {"optimizer": "TOONS", "statistics": stats}
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas TOONS: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/toons-reset")
async def reset_toons_statistics():
    try:
        toons_optimizer.reset_statistics()
        logger.info("Estatísticas TOONS resetadas")
        return {"message": "Estatísticas resetadas"}
    except Exception as e:
        logger.error(f"Erro ao resetar TOONS: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/toons-cache")
async def clear_toons_cache():
    try:
        toons_optimizer.clear_cache()
        logger.warning("Cache TOONS foi limpo")
        return {"message": "Cache limpo"}
    except Exception as e:
        logger.error(f"Erro ao limpar cache TOONS: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}/history", response_model=ConversationHistory)
async def get_conversation_history(conversation_id: str, limit: int = 50):
    try:
        logger.info(f"Recuperando histórico: {conversation_id}")
        messages = cache_service.get_conversation_history(conversation_id, limit)
        message_models = [Message(**msg) for msg in messages]
        return ConversationHistory(
            conversation_id=conversation_id,
            messages=message_models,
            total_messages=len(message_models)
        )
    except Exception as e:
        logger.error(f"Erro ao recuperar histórico: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    try:
        logger.warning(f"Deletando conversa: {conversation_id}")
        success = cache_service.delete_conversation(conversation_id)
        if success:
            return {"message": f"Conversa deletada"}
        raise HTTPException(status_code=500, detail="Erro ao deletar")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cache-stats")
async def get_cache_statistics():
    try:
        stats = cache_service.get_cache_stats()
        return {"cache_service": "Redis", "statistics": stats}
    except Exception as e:
        logger.error(f"Erro ao obter stats de cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cache-clear")
async def clear_all_cache():
    try:
        logger.warning("ALERTA: Solicitação para limpar cache Redis!")
        success = cache_service.clear_all_cache()
        if success:
            return {"message": "Cache limpo", "warning": "Todas as conversas foram deletadas!"}
        raise HTTPException(status_code=500, detail="Erro ao limpar")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao limpar cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))