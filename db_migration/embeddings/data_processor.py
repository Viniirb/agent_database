from typing import List, Dict, Any
from ..analyzer.sql_analyzer import TableInfo
import pandas as pd

class DataProcessor:
    @staticmethod
    def table_to_documents(table_info: TableInfo, sample_data: pd.DataFrame = None) -> List[Dict[str, Any]]:
        documents = []

        schema_doc = DataProcessor._create_schema_document(table_info)
        documents.append(schema_doc)

        if sample_data is not None and not sample_data.empty:
            row_docs = DataProcessor._create_row_documents(table_info, sample_data)
            documents.extend(row_docs)

        return documents

    @staticmethod
    def _create_schema_document(table_info: TableInfo) -> Dict[str, Any]:
        columns_desc = []
        for col in table_info.columns:
            col_type = col['DATA_TYPE']
            col_name = col['COLUMN_NAME']
            nullable = "nullable" if col['IS_NULLABLE'] == 'YES' else "not null"
            columns_desc.append(f"{col_name} ({col_type}, {nullable})")

        relationships_desc = []
        for rel in table_info.relationships:
            relationships_desc.append(
                f"{rel['column_name']} references {rel['referenced_table']}.{rel['referenced_column']}"
            )

        document_text = f"""
        Table: {table_info.schema}.{table_info.name}
        Total Rows: {table_info.row_count}
        Columns: {', '.join([col['COLUMN_NAME'] for col in table_info.columns])}

        Column Details:
        {chr(10).join(columns_desc)}

        Relationships:
        {chr(10).join(relationships_desc) if relationships_desc else 'None'}
        """.strip()

        return {
            "text": document_text,
            "metadata": {
                "type": "schema",
                "table": f"{table_info.schema}.{table_info.name}",
                "row_count": table_info.row_count,
                "column_count": len(table_info.columns)
            }
        }

    @staticmethod
    def _create_row_documents(table_info: TableInfo, sample_data: pd.DataFrame) -> List[Dict[str, Any]]:
        documents = []

        for idx, row in sample_data.iterrows():
            row_text = f"Table: {table_info.schema}.{table_info.name}\n"
            row_text += "Data: "

            row_parts = []
            for col_name, value in row.items():
                if pd.notna(value):
                    row_parts.append(f"{col_name}={value}")

            row_text += ", ".join(row_parts)

            documents.append({
                "text": row_text,
                "metadata": {
                    "type": "data",
                    "table": f"{table_info.schema}.{table_info.name}",
                    "row_index": int(idx)
                }
            })

        return documents

    @staticmethod
    def prepare_for_embedding(documents: List[Dict[str, Any]]) -> tuple:
        texts = [doc["text"] for doc in documents]
        metadatas = [doc["metadata"] for doc in documents]
        return texts, metadatas
