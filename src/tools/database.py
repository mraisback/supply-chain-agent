"""Database tool - query/insert data, access ERP systems."""

from typing import Any, Dict, List, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os


class DatabaseClient:
    """Client for database operations."""

    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv("DATABASE_URL", "sqlite:///./supply_chain.db")
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)

    async def execute(self, function_name: str, **params) -> Dict[str, Any]:
        """
        Execute database operations.

        Args:
            function_name: Operation name (query, insert, update, delete, etc.)
            **params: Operation parameters

        Returns:
            Operation result
        """
        if function_name == "query":
            return await self._query(params.get("sql", ""))
        elif function_name == "insert":
            return await self._insert(params.get("table", ""), params.get("data", {}))
        elif function_name == "update":
            return await self._update(
                params.get("table", ""),
                params.get("data", {}),
                params.get("where", {}),
            )
        elif function_name == "delete":
            return await self._delete(params.get("table", ""), params.get("where", {}))
        else:
            return {"success": False, "error": f"Unknown function: {function_name}"}

    async def _query(self, sql: str) -> Dict[str, Any]:
        """Execute query."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(sql))
                rows = result.fetchall()
                return {
                    "success": True,
                    "rows": [dict(row._mapping) for row in rows],
                    "count": len(rows),
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert row."""
        try:
            columns = ", ".join(data.keys())
            values = ", ".join([f"'{v}'" if isinstance(v, str) else str(v) for v in data.values()])
            sql = f"INSERT INTO {table} ({columns}) VALUES ({values})"
            with self.engine.connect() as conn:
                conn.execute(text(sql))
                conn.commit()
            return {"success": True, "message": "Row inserted"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _update(self, table: str, data: Dict[str, Any], where: Dict[str, Any]) -> Dict[str, Any]:
        """Update rows."""
        try:
            set_clause = ", ".join([f"{k}='{v}'" if isinstance(v, str) else f"{k}={v}" for k, v in data.items()])
            where_clause = " AND ".join([f"{k}='{v}'" if isinstance(v, str) else f"{k}={v}" for k, v in where.items()])
            sql = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
            with self.engine.connect() as conn:
                conn.execute(text(sql))
                conn.commit()
            return {"success": True, "message": "Rows updated"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _delete(self, table: str, where: Dict[str, Any]) -> Dict[str, Any]:
        """Delete rows."""
        try:
            where_clause = " AND ".join([f"{k}='{v}'" if isinstance(v, str) else f"{k}={v}" for k, v in where.items()])
            sql = f"DELETE FROM {table} WHERE {where_clause}"
            with self.engine.connect() as conn:
                conn.execute(text(sql))
                conn.commit()
            return {"success": True, "message": "Rows deleted"}
        except Exception as e:
            return {"success": False, "error": str(e)}
