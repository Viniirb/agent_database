"""
Script para limpar ChromaDB e reiniciar a migração
"""
import os
import shutil
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    print("╔" + "═" * 50 + "╗")
    print("║" + " " * 10 + "🧹 LIMPEZA DO CHROMADB" + " " * 15 + "║")
    print("╚" + "═" * 50 + "╝\n")

    chroma_dir = os.getenv('CHROMA_PERSIST_DIRECTORY', './chroma_db')
    
    print(f"📁 Diretório ChromaDB: {chroma_dir}")
    
    if os.path.exists(chroma_dir):
        print(f"🗑️  Removendo diretório existente...")
        try:
            shutil.rmtree(chroma_dir)
            print("✅ ChromaDB limpo com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao limpar: {e}")
            return False
    else:
        print("📂 Diretório não existe - nada para limpar")
    
    print("\n" + "╔" + "═" * 50 + "╗")
    print("║" + " " * 12 + "✅ LIMPEZA CONCLUÍDA" + " " * 14 + "║")
    print("╚" + "═" * 50 + "╝")
    
    print("\n💡 Agora você pode executar:")
    print("   python migrate_to_chroma.py")
    
    return True

if __name__ == "__main__":
    main()