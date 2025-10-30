import os
from dotenv import load_dotenv
from analyzer.sql_analyzer import SQLServerAnalyzer
from embeddings.chroma_manager import ChromaManager
from embeddings.data_processor import DataProcessor
from tqdm import tqdm

def build_connection_string():
    host = os.getenv('SQL_SERVER_HOST')
    database = os.getenv('SQL_SERVER_DATABASE')
    use_windows_auth = os.getenv('SQL_SERVER_USE_WINDOWS_AUTH', 'False').lower() == 'true'
    trust_cert = os.getenv('SQL_SERVER_TRUST_CERTIFICATE', 'False').lower() == 'true'
    user = os.getenv('SQL_SERVER_USER')
    password = os.getenv('SQL_SERVER_PASSWORD')

    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={host};DATABASE={database};"

    if use_windows_auth:
        conn_str += "Trusted_Connection=yes;"
    else:
        conn_str += f"UID={user};PWD={password};"

    if trust_cert:
        conn_str += "TrustServerCertificate=yes;"

    return conn_str, host, database

def main():
    load_dotenv()

    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "🚀 SQL SERVER → CHROMADB MIGRATION" + " " * 14 + "║")
    print("╚" + "═" * 58 + "╝\n")

    connection_string, host, database = build_connection_string()
    chroma_dir = os.getenv('CHROMA_PERSIST_DIRECTORY', './chroma_db')
    embedding_model = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')

    print(f"📦 Banco de Dados: {database}")
    print(f"🌐 Servidor: {host}")
    print(f"🎯 ChromaDB: {chroma_dir}")
    print(f"🧠 Modelo Embeddings: {embedding_model}\n")

    analyzer = SQLServerAnalyzer(connection_string)
    if not analyzer.connect():
        print("\n❌ Migração abortada devido a erro de conexão")
        return

    print()
    chroma = ChromaManager(persist_directory=chroma_dir, model_name=embedding_model)

    try:
        tables = analyzer.get_all_tables()
        print(f"\n📊 Encontradas {len(tables)} tabelas para migrar")
        print("─" * 60)

        total_docs = 0
        for schema, table in tqdm(tables, desc="🔄 Migrando", ncols=60,
                                   bar_format="{desc} {percentage:3.0f}% |{bar}| {n_fmt}/{total_fmt}"):
            collection_name = f"{database}_{schema}_{table}".lower().replace(" ", "_")

            table_info = analyzer.analyze_table(schema, table)

            sample_data = None
            if table_info.row_count > 0:
                try:
                    sample_data = analyzer.get_sample_data(schema, table, limit=10)
                except:
                    pass

            documents = DataProcessor.table_to_documents(table_info, sample_data)
            texts, metadatas = DataProcessor.prepare_for_embedding(documents)

            chroma.add_documents(
                collection_name=collection_name,
                documents=texts,
                metadatas=metadatas
            )
            total_docs += len(documents)

        print("─" * 60)
        print(f"\n📊 Resumo da Migração:")
        collections = chroma.list_collections()
        for col_name in collections:
            info = chroma.get_collection_info(col_name)
            print(f"   ✓ {col_name}: {info['count']} documentos")

        print(f"\n📈 Total: {len(collections)} collections | {total_docs} documentos")

        print("\n" + "╔" + "═" * 58 + "╗")
        print("║" + " " * 16 + "✅ MIGRAÇÃO CONCLUÍDA!" + " " * 19 + "║")
        print("╚" + "═" * 58 + "╝")

    except Exception as e:
        print(f"\n❌ Erro durante migração: {e}")
    finally:
        print()
        analyzer.close()

if __name__ == "__main__":
    main()
