"""
Script para testar os endpoints da API
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_health():
    """Testa o endpoint de health check"""
    print("\n=== TESTANDO HEALTH CHECK ===")
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"[ERRO] {e}")
        return False

def test_list_collections():
    """Testa listagem de collections"""
    print("\n=== TESTANDO LISTAGEM DE COLLECTIONS ===")
    try:
        response = requests.get(f"{BASE_URL}/collections")
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Total de collections: {data.get('total', 0)}")
        print(f"Collections: {data.get('collections', [])[:5]}...")  # Mostra apenas as primeiras 5
        return response.status_code == 200
    except Exception as e:
        print(f"[ERRO] {e}")
        return False

def test_get_schema():
    """Testa obtenção do schema do banco (otimizado)"""
    print("\n=== TESTANDO SCHEMA DO BANCO ===")
    try:
        # Usa o endpoint rápido primeiro
        response = requests.get(f"{BASE_URL}/stats")
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Total de collections: {data.get('total_collections', 0)}")
        print(f"Documentos estimados: {data.get('estimated_total_documents', 0):,}")
        
        if data.get('sample_collections'):
            print(f"\nExemplos de collections:")
            for i, col in enumerate(data['sample_collections'][:3], 1):
                print(f"  {i}. {col}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"[ERRO] {e}")
        return False

def test_chat(message: str):
    """Testa o endpoint de chat"""
    print(f"\n=== TESTANDO CHAT ===")
    print(f"Mensagem: {message}")
    try:
        payload = {
            "message": message,
            "max_results": 2  # OTIMIZADO: Menos resultados para economizar tokens
        }
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"\n[RESPOSTA]")
            print(data['response'])
            print(f"\n[METADADOS]")
            print(f"Collections consultadas: {data['collections_searched']}")
            print(f"Resultados encontrados: {len(data['search_results'])}")

            if data['search_results']:
                print(f"\nPrimeiros resultados:")
                for i, result in enumerate(data['search_results'][:3], 1):
                    print(f"\n{i}. Collection: {result['collection']}")
                    print(f"   Document: {result['document'][:100]}...")
                    print(f"   Distance: {result.get('distance', 'N/A')}")
        else:
            print(f"Erro: {response.text}")

        return response.status_code == 200
    except Exception as e:
        print(f"[ERRO] {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*60)
    print("  TESTE DA API - BACKEND")
    print("="*60)
    print("\nCertifique-se de que o servidor esta rodando:")
    print("  uvicorn main:app --reload")
    print("\nPressione Enter para continuar...")
    input()

    results = []

    # Testes básicos
    results.append(("Health Check", test_health()))
    results.append(("List Collections", test_list_collections()))
    results.append(("Get Stats (Rápido)", test_get_schema()))

    # Testes de chat OTIMIZADOS (perguntas que podem usar cache)
    results.append(("Chat - Pergunta básica", test_chat("Quantas tabelas existem?")))
    results.append(("Chat - Busca específica", test_chat("tabela produto")))

    # Resumo
    print("\n" + "="*60)
    print("  RESUMO DOS TESTES")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[OK]" if result else "[FALHOU]"
        print(f"{status} {test_name}")

    print(f"\n{passed}/{total} testes passaram")

    if passed == total:
        print("\n[SUCESSO] Todos os testes passaram!")
    else:
        print("\n[ATENCAO] Alguns testes falharam. Verifique os erros acima.")

if __name__ == "__main__":
    main()