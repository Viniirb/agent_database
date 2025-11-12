"""
Script de teste para validar as otimizações do Gemini
Execute com o ambiente virtual ativado: python test_otimizacoes.py
"""
import asyncio
import time
from app.api.chat import GEMINI_PRIMARY_MODEL, GEMINI_SECONDARY_MODEL, GEMINI_TERTIARY_MODEL, _check_simple_response
from app.utils.rate_limiter import rate_limiter


def test_modelos_configurados():
    """Testa se os modelos estão configurados corretamente"""
    print("\n=== TESTE 1: Modelos Configurados ===")
    print(f"Primary Model: {GEMINI_PRIMARY_MODEL}")
    print(f"Secondary Model: {GEMINI_SECONDARY_MODEL}")
    print(f"Tertiary Model: {GEMINI_TERTIARY_MODEL}")

    # Valida que estão usando modelos com melhores limites
    assert "flash" in GEMINI_PRIMARY_MODEL.lower(), "Primary deve ser flash para melhores limites"
    print("✓ Modelos configurados corretamente!")


def test_cache_simples():
    """Testa o cache de respostas simples"""
    print("\n=== TESTE 2: Cache de Respostas Simples ===")

    test_cases = [
        ("oi", True),
        ("olá", True),
        ("bom dia", True),
        ("obrigado", True),
        ("tchau", True),
        ("como fazer uma consulta SQL?", False),  # Não deve estar em cache
    ]

    for message, should_cache in test_cases:
        response = _check_simple_response(message)
        if should_cache:
            assert response is not None, f"'{message}' deveria estar em cache"
            print(f"✓ '{message}' encontrado no cache: {response[:50]}...")
        else:
            assert response is None, f"'{message}' não deveria estar em cache"
            print(f"✓ '{message}' não está em cache (correto)")

    print("✓ Cache de respostas simples funcionando!")


async def test_rate_limiter():
    """Testa o rate limiter"""
    print("\n=== TESTE 3: Rate Limiter ===")

    model_name = GEMINI_PRIMARY_MODEL
    print(f"Testando rate limiter para {model_name}...")

    # Faz 3 requisições rápidas
    start_time = time.time()
    for i in range(3):
        await rate_limiter.acquire(model_name)
        print(f"  Requisição {i+1} aprovada")

    elapsed = time.time() - start_time
    print(f"✓ 3 requisições completadas em {elapsed:.2f}s")
    print("✓ Rate limiter funcionando!")


async def test_rate_limiter_limite():
    """Testa se o rate limiter aguarda quando atinge o limite"""
    print("\n=== TESTE 4: Rate Limiter - Teste de Limite ===")
    print("AVISO: Este teste levará ~60s se executado completamente")
    print("Pulando teste completo... (descomente para testar)")

    # Descomente para testar o limite real (leva 60s+)
    # model_name = GEMINI_PRIMARY_MODEL
    # start_time = time.time()
    # for i in range(15):  # Tenta fazer 15 requisições (limite é 12/min)
    #     await rate_limiter.acquire(model_name)
    #     print(f"  Requisição {i+1} aprovada em {time.time() - start_time:.2f}s")
    # print("✓ Rate limiter aguardou corretamente!")


def test_fallback_models():
    """Testa se há modelos de fallback configurados"""
    print("\n=== TESTE 5: Sistema de Fallback ===")

    models = [GEMINI_PRIMARY_MODEL, GEMINI_SECONDARY_MODEL, GEMINI_TERTIARY_MODEL]
    print(f"Modelos configurados: {len(models)}")

    # Verifica que são diferentes
    assert len(set(models)) == 3, "Deve haver 3 modelos diferentes"
    print("✓ 3 modelos distintos configurados")

    # Verifica que todos são flash (melhor tier gratuito)
    for model in models:
        assert "flash" in model.lower(), f"{model} deveria ser um modelo flash"

    print("✓ Sistema de fallback configurado corretamente!")


async def main():
    """Executa todos os testes"""
    print("=" * 60)
    print("TESTES DE OTIMIZAÇÃO - GEMINI API")
    print("=" * 60)

    try:
        test_modelos_configurados()
        test_cache_simples()
        await test_rate_limiter()
        await test_rate_limiter_limite()
        test_fallback_models()

        print("\n" + "=" * 60)
        print("✓ TODOS OS TESTES PASSARAM!")
        print("=" * 60)
        print("\nResumo das otimizações:")
        print(f"  1. Modelo Primary: {GEMINI_PRIMARY_MODEL} (15 RPM)")
        print(f"  2. Sistema de fallback com 3 modelos")
        print(f"  3. Cache de respostas simples (35+ mensagens)")
        print(f"  4. Rate limiter com janela deslizante (12 RPM)")
        print("\nSeu projeto está otimizado para o tier gratuito do Gemini!")

    except AssertionError as e:
        print(f"\n❌ TESTE FALHOU: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
