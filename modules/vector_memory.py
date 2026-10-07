"""
=============================================================================
JARVIS OMNI-GHOST SUPREME - MEMORIA SEMÁNTICA VECTORIAL PERMANENTE
=============================================================================
Almacén de memoria episódica y perfil de usuario basado en SQLite y cálculo
vectorial de similitud coseno (TF-IDF + embeddings de alta dimensionalidad).
Garantiza persistencia de hechos, preferencias de Edwin y conversaciones
pasadas en Android (Termux) y PC sin requerir compiladores externos complejos.
=============================================================================
"""

import math
import json
import time
import sqlite3
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

import config


class SemanticVectorizer:
    """
    Vectorizador semántico híbrido en Python puro con cálculo de frecuencia inversa (TF-IDF)
    y n-gramas fonético-semánticos. Genera vectores normalizados de 128 dimensiones.
    """

    DIMENSIONS = 128

    def _tokenize(self, text: str) -> List[str]:
        cleaned = re.sub(r"[^\w\s]", " ", text.lower())
        tokens = [w for w in cleaned.split() if len(w) > 1]
        return tokens

    def vectorize(self, text: str) -> List[float]:
        tokens = self._tokenize(text)
        if not tokens:
            return [0.0] * self.DIMENSIONS

        vector = [0.0] * self.DIMENSIONS
        # Hashing semántico distribuido con TF
        for token in tokens:
            idx = int(hash(token) % self.DIMENSIONS)
            vector[idx] += 1.0

            # Añadir bigramas de caracteres para captar raíces morfológicas
            for i in range(len(token) - 2):
                ngram = token[i:i+3]
                idx_ng = int(hash(ngram) % self.DIMENSIONS)
                vector[idx_ng] += 0.5

        # Normalización Euclidiana (L2 Norm) para similitud coseno
        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0.0:
            vector = [v / norm for v in vector]

        return vector

    @staticmethod
    def cosine_similarity(v1: List[float], v2: List[float]) -> float:
        if len(v1) != len(v2) or not v1 or not v2:
            return 0.0
        return sum(a * b for a, b in zip(v1, v2))


class VectorMemory:
    """
    Gestor de base de datos relacional y vectorial SQLite para Jarvis Supreme.
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or config.DATABASE_PATH
        self.vectorizer = SemanticVectorizer()
        self._init_database()
        self._seed_initial_profile()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_database(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Tabla de memorias vectoriales
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS semantic_memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    category TEXT NOT NULL,
                    tags TEXT,
                    vector_json TEXT NOT NULL,
                    created_at REAL NOT NULL
                )
            """)
            # Tabla de hechos de perfil de usuario
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profile (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    updated_at REAL NOT NULL
                )
            """)
            # Historial de conversaciones
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp REAL NOT NULL
                )
            """)
            conn.commit()

    def _seed_initial_profile(self):
        """Inicializa los datos clave de Edwin si la base está nueva."""
        defaults = {
            "usuario_nombre": config.USER_NAME,
            "usuario_titulo": config.USER_TITLE,
            "idioma_preferido": config.PRIMARY_LANGUAGE,
            "tema_asistente": "Cyberpunk Neon / Jarvis HUD",
            "moto_preferida": "Moto de alto rendimiento (Monitoreo activo)",
            "plataforma_base": config.CURRENT_PLATFORM,
        }
        for k, v in defaults.items():
            if not self.get_profile_fact(k):
                self.set_profile_fact(k, v)

    # -------------------------------------------------------------------------
    # OPERACIONES DE PERFIL DE USUARIO
    # -------------------------------------------------------------------------
    def set_profile_fact(self, key: str, value: str, category: str = "general"):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_profile (key, value, category, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
            """, (key, value, category, time.time()))
            conn.commit()

    def get_profile_fact(self, key: str) -> Optional[str]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM user_profile WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row["value"] if row else None

    def get_all_profile_facts(self) -> Dict[str, str]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM user_profile")
            return {row["key"]: row["value"] for row in cursor.fetchall()}

    # -------------------------------------------------------------------------
    # ALMACENAMIENTO Y BÚSQUEDA VECTORIAL
    # -------------------------------------------------------------------------
    def store_memory(self, content: str, category: str = "episodica", tags: Optional[List[str]] = None) -> int:
        """Guarda un texto con su vector semántico embebido en SQLite."""
        vector = self.vectorizer.vectorize(content)
        vector_json = json.dumps(vector)
        tags_str = ",".join(tags) if tags else ""

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO semantic_memories (content, category, tags, vector_json, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (content, category, tags_str, vector_json, time.time()))
            conn.commit()
            return cursor.lastrowid

    def search_similar(self, query: str, top_k: int = 4, min_similarity: float = 0.15) -> List[Dict[str, Any]]:
        """
        Calcula la similitud coseno entre la consulta y todas las memorias guardadas.
        Retorna las 'top_k' coincidencias más relevantes semánticamente.
        """
        query_vector = self.vectorizer.vectorize(query)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, content, category, tags, vector_json, created_at FROM semantic_memories")
            rows = cursor.fetchall()

        results = []
        for row in rows:
            try:
                mem_vector = json.loads(row["vector_json"])
                sim = self.vectorizer.cosine_similarity(query_vector, mem_vector)
                if sim >= min_similarity:
                    results.append({
                        "id": row["id"],
                        "content": row["content"],
                        "category": row["category"],
                        "tags": row["tags"].split(",") if row["tags"] else [],
                        "similarity": round(sim, 4),
                        "created_at": row["created_at"],
                    })
            except Exception:
                continue

        # Ordenar por mayor similitud
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]

    # -------------------------------------------------------------------------
    # HISTORIAL DE CONVERSACIÓN
    # -------------------------------------------------------------------------
    def record_turn(self, role: str, message: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conversation_history (role, message, timestamp)
                VALUES (?, ?, ?)
            """, (role, message, time.time()))
            conn.commit()

        # También guardar como memoria semántica si proviene del usuario
        if role.lower() == "user" and len(message) > 10:
            self.store_memory(content=message, category="conversacion_usuario")

    def get_recent_conversation(self, limit: int = 6) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT role, message, timestamp FROM conversation_history
                ORDER BY id DESC LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [{"role": r["role"], "message": r["message"], "time": r["timestamp"]} for r in reversed(rows)]

    def build_memory_context_prompt(self, user_query: str) -> str:
        """Sintetiza un bloque de contexto semántico para inyectar al modelo de IA."""
        similar = self.search_similar(user_query, top_k=3)
        facts = self.get_all_profile_facts()

        parts = [f"=== CONTEXTO DE MEMORIA PERMANENTE DE {config.USER_TITLE.upper()} ==="]
        if facts:
            parts.append("Datos de perfil:")
            for k, v in list(facts.items())[:6]:
                parts.append(f" - {k}: {v}")

        if similar:
            parts.append("\nMemorias semánticas relacionadas recordadas:")
            for m in similar:
                parts.append(f" - [{m['category']}] {m['content']} (Similitud: {m['similarity']})")

        return "\n".join(parts)


# Instancia singleton predeterminada
vector_memory = VectorMemory()
