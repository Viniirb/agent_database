import json
from typing import List
from .sql_analyzer import TableInfo
import numpy as np

class DatabaseReport:
    def __init__(self, tables: List[TableInfo]):
        self.tables = tables

    @staticmethod
    def convert_to_native(obj):
        if isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj

    def generate_summary(self) -> dict:
        total_rows = sum(t.row_count for t in self.tables)
        total_columns = sum(len(t.columns) for t in self.tables)

        return {
            "total_tables": len(self.tables),
            "total_rows": int(total_rows),
            "total_columns": int(total_columns),
            "tables": [
                {
                    "name": f"{t.schema}.{t.name}",
                    "columns": len(t.columns),
                    "rows": int(t.row_count),
                    "has_relationships": len(t.relationships) > 0
                }
                for t in self.tables
            ]
        }

    def generate_text_report(self) -> str:
        summary = self.generate_summary()
        report = []

        report.append("="*60)
        report.append("RELATÓRIO DE ANÁLISE DO BANCO DE DADOS")
        report.append("="*60)
        report.append(f"\nTotal de Tabelas: {summary['total_tables']}")
        report.append(f"Total de Linhas: {summary['total_rows']:,}")
        report.append(f"Total de Colunas: {summary['total_columns']}")
        report.append("\n" + "-"*60)
        report.append("DETALHES DAS TABELAS")
        report.append("-"*60)

        for table in self.tables:
            report.append(f"\n📊 {table.schema}.{table.name}")
            report.append(f"   Linhas: {table.row_count:,}")
            report.append(f"   Colunas: {len(table.columns)}")

            if table.relationships:
                report.append(f"   Relacionamentos: {len(table.relationships)}")
                for rel in table.relationships:
                    report.append(f"      └─ {rel['column_name']} → {rel['referenced_table']}.{rel['referenced_column']}")

            report.append("\n   Estrutura:")
            for col in table.columns:
                nullable = "NULL" if col['IS_NULLABLE'] == 'YES' else "NOT NULL"
                max_len = f"({col['CHARACTER_MAXIMUM_LENGTH']})" if col['CHARACTER_MAXIMUM_LENGTH'] else ""
                report.append(f"      • {col['COLUMN_NAME']}: {col['DATA_TYPE']}{max_len} {nullable}")

        return "\n".join(report)

    def save_json(self, filepath: str):
        summary = self.generate_summary()

        def convert_values(obj):
            if isinstance(obj, dict):
                return {k: convert_values(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_values(item) for item in obj]
            else:
                return self.convert_to_native(obj)

        clean_summary = convert_values(summary)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(clean_summary, f, indent=2, ensure_ascii=False)
        print(f"   📄 JSON: {filepath}")

    def save_text(self, filepath: str):
        report = self.generate_text_report()
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"   📝 TXT: {filepath}")
