"""Embedding storage using SQLite with JSON serialization.
Concurrency-safe: uses WAL mode, connection timeout, and a threading.Lock
for serializing write operations to avoid 'database is locked' errors.
"""

import sqlite3
import threading
import json
import numpy as np
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime
import hashlib


class EmbeddingDB:
    """SQLite database for storing and retrieving face embeddings."""

    def __init__(self, db_path: str = "embeddings.db"):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Return a sqlite3 connection with reasonable timeout and thread settings."""
        conn = sqlite3.connect(self.db_path, timeout=30, check_same_thread=False)
        return conn

    def _init_db(self):
        """Create schema and set PRAGMAs for better concurrency."""
        conn = self._get_connection()
        cur = conn.cursor()
        try:
            # Enable WAL to reduce write/read locking contention
            try:
                cur.execute("PRAGMA journal_mode=WAL;")
                cur.execute("PRAGMA synchronous=NORMAL;")
            except Exception:
                # Some SQLite builds may ignore PRAGMA statements; ignore failures
                pass

            cur.execute(
                '''
                CREATE TABLE IF NOT EXISTS embeddings (
                    id TEXT PRIMARY KEY,
                    application_id TEXT NOT NULL,
                    evidence_type TEXT NOT NULL,
                    evidence_id TEXT NOT NULL,
                    embedding TEXT NOT NULL,
                    embedding_dim INTEGER NOT NULL,
                    file_sha256 TEXT,
                    file_uri TEXT,
                    detection_confidence REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(evidence_id)
                )
                '''
            )

            cur.execute(
                '''
                CREATE INDEX IF NOT EXISTS idx_application_id
                ON embeddings(application_id)
                '''
            )

            cur.execute(
                '''
                CREATE INDEX IF NOT EXISTS idx_evidence_type
                ON embeddings(evidence_type)
                '''
            )

            cur.execute(
                '''
                CREATE INDEX IF NOT EXISTS idx_evidence_id
                ON embeddings(evidence_id)
                '''
            )

            cur.execute(
                '''
                CREATE TABLE IF NOT EXISTS verification_results (
                    id TEXT PRIMARY KEY,
                    application_id TEXT NOT NULL,
                    embedding_id_selfie TEXT NOT NULL,
                    embedding_id_idcrop TEXT NOT NULL,
                    similarity REAL NOT NULL,
                    similarity_metric TEXT DEFAULT 'cosine',
                    liveness_score REAL,
                    match_confidence REAL,
                    agent_version TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (embedding_id_selfie) REFERENCES embeddings(id),
                    FOREIGN KEY (embedding_id_idcrop) REFERENCES embeddings(id)
                )
                '''
            )

            cur.execute(
                '''
                CREATE INDEX IF NOT EXISTS idx_app_verification
                ON verification_results(application_id)
                '''
            )

            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def _generate_embedding_id(application_id: str, evidence_id: str) -> str:
        combined = f"{application_id}:{evidence_id}"
        hash_value = hashlib.sha256(combined.encode()).hexdigest()[:8]
        return f"emb-{hash_value}"

    def store_embedding(
        self,
        application_id: str,
        evidence_type: str,
        evidence_id: str,
        embedding: np.ndarray,
        file_sha256: Optional[str] = None,
        file_uri: Optional[str] = None,
        detection_confidence: Optional[float] = None,
    ) -> str:
        """Serialize and store an embedding. Returns embedding id."""
        emb_id = self._generate_embedding_id(application_id, evidence_id)
        embedding_json = json.dumps(np.asarray(embedding).tolist())

        with self._lock:
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute(
                '''
                INSERT OR REPLACE INTO embeddings
                (id, application_id, evidence_type, evidence_id, embedding,
                 embedding_dim, file_sha256, file_uri, detection_confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    emb_id,
                    application_id,
                    evidence_type,
                    evidence_id,
                    embedding_json,
                    int(np.asarray(embedding).size),
                    file_sha256,
                    file_uri,
                    detection_confidence,
                ),
            )
            conn.commit()
            conn.close()

        return emb_id

    def get_embedding(self, embedding_id: str) -> Optional[np.ndarray]:
        conn = self._get_connection()
        cur = conn.cursor()
        try:
            cur.execute('SELECT embedding FROM embeddings WHERE id = ?', (embedding_id,))
            row = cur.fetchone()
            if row is None:
                return None
            lst = json.loads(row[0])
            return np.array(lst)
        finally:
            conn.close()

    def get_embeddings_by_application(self, application_id: str) -> Dict[str, dict]:
        conn = self._get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                '''SELECT id, evidence_type, evidence_id, embedding, detection_confidence
                   FROM embeddings WHERE application_id = ?''',
                (application_id,),
            )
            results = cur.fetchall()
            out = {}
            for row in results:
                emb_id, evidence_type, evidence_id, embedding_json, confidence = row
                out[evidence_type] = {
                    'id': emb_id,
                    'evidence_id': evidence_id,
                    'embedding': np.array(json.loads(embedding_json)),
                    'confidence': confidence,
                }
            return out
        finally:
            conn.close()

    def store_verification_result(
        self,
        application_id: str,
        embedding_id_selfie: str,
        embedding_id_idcrop: str,
        similarity: float,
        similarity_metric: str = "cosine",
        liveness_score: Optional[float] = None,
        match_confidence: Optional[float] = None,
        agent_version: str = "face-v1",
    ) -> str:
        result_id = self._generate_embedding_id(application_id, "verification")
        with self._lock:
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute(
                '''
                INSERT OR REPLACE INTO verification_results
                (id, application_id, embedding_id_selfie, embedding_id_idcrop,
                 similarity, similarity_metric, liveness_score, match_confidence, agent_version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    result_id,
                    application_id,
                    embedding_id_selfie,
                    embedding_id_idcrop,
                    similarity,
                    similarity_metric,
                    liveness_score,
                    match_confidence,
                    agent_version,
                ),
            )
            conn.commit()
            conn.close()
        return result_id

    def get_verification_result(self, result_id: str) -> Optional[Dict]:
        conn = self._get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                '''SELECT application_id, embedding_id_selfie, embedding_id_idcrop,
                          similarity, similarity_metric, liveness_score, match_confidence,
                          agent_version, created_at
                   FROM verification_results WHERE id = ?''',
                (result_id,),
            )
            row = cur.fetchone()
            if row is None:
                return None
            return {
                'id': result_id,
                'application_id': row[0],
                'embedding_id_selfie': row[1],
                'embedding_id_idcrop': row[2],
                'similarity': row[3],
                'similarity_metric': row[4],
                'liveness_score': row[5],
                'match_confidence': row[6],
                'agent_version': row[7],
                'created_at': row[8],
            }
        finally:
            conn.close()

    def delete_old_embeddings(self, days: int = 90):
        with self._lock:
            conn = self._get_connection()
            cur = conn.cursor()
            try:
                cur.execute(
                    '''
                    DELETE FROM embeddings
                    WHERE created_at < datetime('now', '-' || ? || ' days')
                    ''',
                    (days,),
                )
                conn.commit()
            finally:
                conn.close()
        # file cleanup: nothing more below
