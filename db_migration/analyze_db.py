import os
from dotenv import load_dotenv
from analyzer.sql_analyzer import SQLServerAnalyzer
from analyzer.report_generator import DatabaseReport

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
    print("║" + " " * 15 + "🔍 SQL SERVER ANALYZER" + " " * 21 + "║")
    print("╚" + "═" * 58 + "╝\n")

    connection_string, host, database = build_connection_string()

    print(f"📦 Banco de Dados: {database}")
    print(f"🌐 Servidor: {host}\n")

    analyzer = SQLServerAnalyzer(connection_string)

    if not analyzer.connect():
        print("\n❌ Análise abortada devido a erro de conexão")
        return

    try:
        tables_info = analyzer.analyze_database()

        report = DatabaseReport(tables_info)

        print("\n" + report.generate_text_report())

        print(f"\n💾 Salvando relatórios...")
        os.makedirs('reports', exist_ok=True)
        report.save_json('reports/database_analysis.json')
        report.save_text('reports/database_analysis.txt')

        print("\n" + "╔" + "═" * 58 + "╗")
        print("║" + " " * 18 + "✅ ANÁLISE CONCLUÍDA!" + " " * 19 + "║")
        print("╚" + "═" * 58 + "╝")

    except Exception as e:
        print(f"\n❌ Erro durante análise: {e}")
    finally:
        print()
        analyzer.close()

if __name__ == "__main__":
    main()
