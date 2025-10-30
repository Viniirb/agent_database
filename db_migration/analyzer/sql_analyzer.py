import pandas as pd
from typing import List, Dict, Any
from dataclasses import dataclass
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
import urllib.parse
import warnings

warnings.filterwarnings('ignore', category=UserWarning, module='pandas')

@dataclass
class TableInfo:
    name: str
    schema: str
    columns: List[Dict[str, Any]]
    row_count: int
    relationships: List[Dict[str, Any]]

class SQLServerAnalyzer:
    def __init__(self, connection_string: str):
        self.odbc_connection_string = connection_string
        self.engine: Engine = None

    def connect(self):
        try:
            print("🔌 Conectando ao SQL Server...", end=" ")

            params = urllib.parse.quote_plus(self.odbc_connection_string)
            sqlalchemy_url = f"mssql+pyodbc:///?odbc_connect={params}"

            self.engine = create_engine(
                sqlalchemy_url,
                fast_executemany=True,
                echo=False
            )

            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            print("✅ Sucesso!")
            return True
        except Exception as e:
            print("❌ Falhou!")
            print(f"💥 Erro: {e}")
            return False

    def get_all_tables(self) -> List[str]:
        query = """
        SELECT TABLE_SCHEMA, TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_SCHEMA, TABLE_NAME
        """
        df = pd.read_sql(query, self.engine)
        return [(row['TABLE_SCHEMA'], row['TABLE_NAME']) for _, row in df.iterrows()]

    def get_table_columns(self, schema: str, table: str) -> List[Dict[str, Any]]:
        query = text("""
        SELECT
            COLUMN_NAME,
            DATA_TYPE,
            CHARACTER_MAXIMUM_LENGTH,
            IS_NULLABLE,
            COLUMN_DEFAULT
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = :schema AND TABLE_NAME = :table
        ORDER BY ORDINAL_POSITION
        """)
        df = pd.read_sql(query, self.engine, params={"schema": schema, "table": table})
        return df.to_dict('records')

    def get_table_row_count(self, schema: str, table: str) -> int:
        try:
            query = text(f"SELECT COUNT(*) as cnt FROM [{schema}].[{table}]")
            df = pd.read_sql(query, self.engine)
            return int(df['cnt'].iloc[0])
        except:
            return 0

    def get_foreign_keys(self, schema: str, table: str) -> List[Dict[str, Any]]:
        query = text("""
        SELECT
            fk.name AS constraint_name,
            OBJECT_NAME(fk.parent_object_id) AS table_name,
            COL_NAME(fc.parent_object_id, fc.parent_column_id) AS column_name,
            OBJECT_NAME(fk.referenced_object_id) AS referenced_table,
            COL_NAME(fc.referenced_object_id, fc.referenced_column_id) AS referenced_column
        FROM sys.foreign_keys AS fk
        INNER JOIN sys.foreign_key_columns AS fc
            ON fk.object_id = fc.constraint_object_id
        WHERE OBJECT_SCHEMA_NAME(fk.parent_object_id) = :schema
            AND OBJECT_NAME(fk.parent_object_id) = :table
        """)
        try:
            df = pd.read_sql(query, self.engine, params={"schema": schema, "table": table})
            return df.to_dict('records')
        except:
            return []

    def analyze_table(self, schema: str, table: str) -> TableInfo:
        columns = self.get_table_columns(schema, table)
        row_count = self.get_table_row_count(schema, table)
        relationships = self.get_foreign_keys(schema, table)

        return TableInfo(
            name=table,
            schema=schema,
            columns=columns,
            row_count=row_count,
            relationships=relationships
        )

    def analyze_database(self) -> List[TableInfo]:
        tables = self.get_all_tables()
        results = []

        print(f"\n🔍 Descobrindo estrutura do banco...")
        print(f"📊 Encontradas {len(tables)} tabelas\n")
        print("─" * 60)

        for idx, (schema, table) in enumerate(tables, 1):
            print(f"[{idx}/{len(tables)}] 📋 {schema}.{table}", end=" ")
            info = self.analyze_table(schema, table)

            emoji = "🟢" if info.row_count > 0 else "🔵"
            rel_emoji = f" 🔗{len(info.relationships)}" if info.relationships else ""
            print(f"{emoji} {info.row_count:,} linhas | {len(info.columns)} colunas{rel_emoji}")

            results.append(info)

        print("─" * 60)
        return results

    def get_sample_data(self, schema: str, table: str, limit: int = 5) -> pd.DataFrame:
        query = text(f"SELECT TOP {limit} * FROM [{schema}].[{table}]")
        return pd.read_sql(query, self.engine)

    def close(self):
        if self.engine:
            self.engine.dispose()
            print("🔌 Conexão fechada com sucesso")
