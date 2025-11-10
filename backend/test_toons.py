"""
Script de teste para validar a integração do TOONS e otimização de tokens.
Execute com: python test_toons.py
"""

import sys
from pathlib import Path

# Adicionar o diretório backend ao path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.toons_service import toons_optimizer
import logging

# Configurar logging para teste
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_compression():
    """Testa a compressão de contexto."""
    print("\n" + "="*60)
    print("TESTE 1: Compressão de Contexto")
    print("="*60)
    
    # Contexto de exemplo
    context = """
    Dados encontrados:
    
    1. Tabela usuarios contém informações de usuários do sistema
       (5000 registros)
    
    2. Tabela usuarios contém informações de usuários do sistema
       (5000 registros)
    
    3. Tabela produtos com lista de produtos disponíveis
       (12000 registros)
    
    4. Tabela pedidos com histórico de pedidos
       (25000 registros)
    """
    
    logger.info(f"Contexto original: {len(context)} caracteres")
    result = toons_optimizer.compress_context(context)
    
    print(f"\n✓ Tamanho original: {result['original_length']} caracteres")
    print(f"✓ Tamanho comprimido: {result['compressed_length']} caracteres")
    print(f"✓ Redução: {result['reduction_percentage']}%")
    print(f"✓ Tokens economizados estimado: {result['tokens_saved_estimate']}")
    print(f"✓ Do cache: {result['from_cache']}")
    print(f"✓ Tempo de processamento: {result['processing_time_ms']}ms")
    
    return result


def test_cache():
    """Testa o cache do otimizador."""
    print("\n" + "="*60)
    print("TESTE 2: Cache de Contexto")
    print("="*60)
    
    context = "Dados: tabela usuarios com 5000 registros. Tabela produtos com 12000 registros."
    
    # Primeira compressão (cache miss)
    logger.info("Primeira compressão - esperado CACHE MISS")
    result1 = toons_optimizer.compress_context(context)
    print(f"\n✓ Primeira execução - Do cache: {result1['from_cache']}")
    
    # Segunda compressão (cache hit)
    logger.info("Segunda compressão - esperado CACHE HIT")
    result2 = toons_optimizer.compress_context(context)
    print(f"✓ Segunda execução - Do cache: {result2['from_cache']}")
    
    # Verificar que resultados são idênticos
    assert result1['compressed'] == result2['compressed'], "Conteúdo comprimido deve ser idêntico"
    print("✓ Conteúdo comprimido é idêntico em ambas as execuções")
    
    return result2


def test_full_optimization():
    """Testa a otimização completa do prompt."""
    print("\n" + "="*60)
    print("TESTE 3: Otimização Completa do Prompt")
    print("="*60)
    
    system_prompt = "Você é um assistente de banco de dados SQL."
    context = "Tabelas encontradas: usuarios (5000), produtos (12000), pedidos (25000)"
    user_message = "Quantos usuários temos no banco?"
    
    result = toons_optimizer.optimize_prompt(system_prompt, context, user_message)
    
    print(f"\n✓ Tamanho original do prompt: {result['original_size']} caracteres")
    print(f"✓ Tamanho otimizado do prompt: {result['optimized_size']} caracteres")
    print(f"✓ Tokens economizados: {result['tokens_saved_estimate']}")
    print(f"✓ Vem do cache: {result['cache_hit']}")
    
    return result


def test_statistics():
    """Testa as estatísticas do otimizador."""
    print("\n" + "="*60)
    print("TESTE 4: Estatísticas do Otimizador")
    print("="*60)
    
    stats = toons_optimizer.get_statistics()
    
    print(f"\n✓ Cache hits: {stats['cache_hits']}")
    print(f"✓ Cache misses: {stats['cache_misses']}")
    print(f"✓ Total de requisições: {stats['total_requests']}")
    print(f"✓ Taxa de acerto do cache: {stats['hit_rate_percentage']}%")
    print(f"✓ Tamanho atual do cache: {stats['cache_size']}")
    print(f"✓ Total de tokens economizados: {stats['total_tokens_saved']}")
    print(f"✓ Custo economizado estimado: {stats['estimated_cost_saved']}")
    
    return stats


def main():
    """Executa todos os testes."""
    print("\n" + "🚀 " * 20)
    print("TOONS - Otimizador de Tokens para IA")
    print("🚀 " * 20)
    
    try:
        # Executar testes
        test_compression()
        test_cache()
        test_full_optimization()
        stats = test_statistics()
        
        print("\n" + "="*60)
        print("✅ TODOS OS TESTES PASSARAM COM SUCESSO!")
        print("="*60)
        
        print(f"\n📊 Resumo Final:")
        print(f"   - Cache hit rate: {stats['hit_rate_percentage']}%")
        print(f"   - Tokens economizados: {stats['total_tokens_saved']}")
        print(f"   - Economia estimada: {stats['estimated_cost_saved']}")
        
    except Exception as e:
        print(f"\n❌ ERRO DURANTE OS TESTES: {str(e)}")
        logger.exception("Erro durante execução dos testes")
        sys.exit(1)


if __name__ == "__main__":
    main()
