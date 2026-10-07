"""
AI-Powered Fitness Coach — Supabase Client & Local Resilient Fallback

Integrates with official Supabase Python client when credentials are provided.
Provides a local SQLite persistence layer with identical API semantics
if running offline or in demo mode for viva defense.
"""

import os
import uuid
import json
import sqlite3
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime, timezone

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

DB_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "fitness_coach_local.db"


class LocalDatabaseProxy:
    """
    Self-contained SQLite engine mirroring Supabase tables:
    profiles, videos, analyses, reps, feedback.
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS profiles (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE,
                    full_name TEXT,
                    fitness_goal TEXT,
                    experience_level TEXT,
                    created_at TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS videos (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    filename TEXT,
                    file_path TEXT,
                    file_size_bytes INTEGER,
                    duration_sec REAL,
                    fps REAL,
                    width INTEGER,
                    height INTEGER,
                    created_at TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    id TEXT PRIMARY KEY,
                    video_id TEXT,
                    user_id TEXT,
                    exercise TEXT,
                    model_used TEXT,
                    status TEXT,
                    overall_score REAL,
                    grade TEXT,
                    total_reps INTEGER,
                    metrics_breakdown TEXT,
                    coaching_feedback TEXT,
                    processing_time_sec REAL,
                    created_at TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reps (
                    id TEXT PRIMARY KEY,
                    analysis_id TEXT,
                    rep_number INTEGER,
                    duration_sec REAL,
                    eccentric_duration_sec REAL,
                    concentric_duration_sec REAL,
                    min_angle REAL,
                    max_angle REAL,
                    rom REAL,
                    form_errors TEXT,
                    score REAL,
                    created_at TEXT
                )
            """)
            conn.commit()

    # Query builder emulator
    def table(self, table_name: str):
        return TableQueryBuilder(self, table_name)


class TableQueryBuilder:
    def __init__(self, db_proxy: LocalDatabaseProxy, table_name: str):
        self.db = db_proxy
        self.table_name = table_name
        self._filters: List[str] = []
        self._params: List[Any] = []
        self._order_by: Optional[str] = None
        self._limit: Optional[int] = None

    def select(self, columns: str = "*"):
        return self

    def eq(self, column: str, value: Any):
        self._filters.append(f"{column} = ?")
        self._params.append(value)
        return self

    def order(self, column: str, desc: bool = False):
        direction = "DESC" if desc else "ASC"
        self._order_by = f"{column} {direction}"
        return self

    def limit(self, count: int):
        self._limit = count
        return self

    def insert(self, data: Dict[str, Any]):
        cols = list(data.keys())
        placeholders = ", ".join(["?"] * len(cols))
        sql = f"INSERT INTO {self.table_name} ({', '.join(cols)}) VALUES ({placeholders})"

        # Convert dict/lists to JSON strings
        vals = []
        for c in cols:
            v = data[c]
            if isinstance(v, (dict, list)):
                vals.append(json.dumps(v))
            else:
                vals.append(v)

        with self.db._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, vals)
            conn.commit()

        class ExecResult:
            def __init__(self, d):
                self.data = [d]
        return ExecResult(data)

    def update(self, data: Dict[str, Any]):
        set_clauses = []
        vals = []
        for k, v in data.items():
            set_clauses.append(f"{k} = ?")
            if isinstance(v, (dict, list)):
                vals.append(json.dumps(v))
            else:
                vals.append(v)

        where_clause = f" WHERE {' AND '.join(self._filters)}" if self._filters else ""
        sql = f"UPDATE {self.table_name} SET {', '.join(set_clauses)}{where_clause}"
        vals.extend(self._params)

        with self.db._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, vals)
            conn.commit()

        class ExecResult:
            def __init__(self, d):
                self.data = [d]
        return ExecResult(data)

    def delete(self):
        """Delete rows matching accumulated filters. Returns deleted-row count."""
        where_clause = f" WHERE {' AND '.join(self._filters)}" if self._filters else ""
        sql = f"DELETE FROM {self.table_name}{where_clause}"

        with self.db._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, self._params)
            conn.commit()
            count = cursor.rowcount

        class DeleteResult:
            def __init__(self, c):
                self.data = []
                self.count = c
        return DeleteResult(count)

    def execute(self):
        where_clause = f" WHERE {' AND '.join(self._filters)}" if self._filters else ""
        order_clause = f" ORDER BY {self._order_by}" if self._order_by else ""
        limit_clause = f" LIMIT {self._limit}" if self._limit else ""

        sql = f"SELECT * FROM {self.table_name}{where_clause}{order_clause}{limit_clause}"

        with self.db._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, self._params)
            rows = cursor.fetchall()
            results = []
            for r in rows:
                row_dict = dict(r)
                # Parse any JSON text fields
                for k, v in row_dict.items():
                    if isinstance(v, str) and (v.startswith("{") or v.startswith("[")):
                        try:
                            row_dict[k] = json.loads(v)
                        except Exception:
                            pass
                results.append(row_dict)

        class ExecResult:
            def __init__(self, res):
                self.data = res
        return ExecResult(results)


# Singleton instances
_local_db = LocalDatabaseProxy(DB_FILE)
_supabase_client = None


def get_db():
    """
    Returns Supabase client if configured, otherwise returns local database proxy.
    """
    global _supabase_client

    if settings.SUPABASE_URL and settings.SUPABASE_KEY and "example" not in settings.SUPABASE_URL:
        try:
            if _supabase_client is None:
                from supabase import create_client
                _supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            return _supabase_client
        except Exception as e:
            logger.warning(f"Failed to connect to Supabase: {e}. Falling back to local SQLite.")
            return _local_db
    else:
        return _local_db
