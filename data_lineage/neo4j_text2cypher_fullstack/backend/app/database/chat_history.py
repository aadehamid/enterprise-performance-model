"""In-memory chat history with live Neo4j database persistence writes and SQLite long-term cold archival."""
from collections import defaultdict, deque
from uuid import uuid4
import os
import sqlite3
from datetime import datetime, timedelta
import neo4j


class _Mem:
    def __init__(self, store, sid, window, parent=None):
        self._s, self._sid, self._w = store, sid, window
        self.message_history = parent

    def add_message(self, m):
        self._s[self._sid].append(m)
        while len(self._s[self._sid]) > self._w:
            self._s[self._sid].popleft()

    @property
    def messages(self):
        return list(self._s[self._sid])

    def __iter__(self):
        return iter(self.messages)


class MessageHistory:
    _STORE = defaultdict(deque)

    def __init__(self, driver=None, database="governancemetadata", window=40, db_path=None):
        self._driver = driver
        self._db = database
        self._w = window
        self._db_path = db_path or os.path.join(os.path.dirname(__file__), "chat_history.db")
        self._init_sqlite()

    def _init_sqlite(self):
        """Initializes the local SQLite database for historical message archives."""
        try:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS archived_messages (
                session_id TEXT,
                question TEXT,
                cypher TEXT,
                answer TEXT,
                feedback TEXT,
                feedback_comment TEXT,
                timestamp TEXT
            )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Warning: Failed to initialize SQLite chat history database: {e}")

    def create_history(self, session_id=None):
        sid = session_id or str(uuid4())
        return _Mem(self._STORE, sid, self._w, parent=self), None, sid

    def record_message(self, session_id: str, question: str, cypher: str, answer: str):
        """
        Transactional History Persister: Appends conversation details
        directly to the Neo4j database under the governancemetadata db,
        and triggers a background cold-archival task to SQLite.
        """
        if not self._driver:
            return
            
        write_query = """
        MERGE (s:Session {id: $session_id})
        CREATE (m:Message {
            question: $question,
            cypher: $cypher,
            answer: $answer,
            timestamp: datetime()
        })
        CREATE (s)-[:HAS_MESSAGE]->(m)
        
        WITH s, m
        OPTIONAL MATCH (s)-[old:LAST_MESSAGE]->(prev)
        DELETE old
        CREATE (s)-[:LAST_MESSAGE]->(m)
        
        WITH prev, m
        WHERE prev IS NOT NULL
        CREATE (prev)-[:NEXT]->(m)
        """
        try:
            self._driver.execute_query(
                write_query,
                {"session_id": session_id, "question": question, "cypher": cypher, "answer": answer},
                database_=self._db,
                routing_=neo4j.RoutingControl.WRITE
            )
            
            # Automatically run the archival process to move messages older than 30 days into SQLite
            self.archive_old_messages()
            
        except Exception as e:
            # Log warning but do not crash user's search pipeline if history log fails
            print(f"Warning: Failed to persist conversation history to Neo4j: {e}")

    def archive_old_messages(self):
        """
        Extracts messages older than 30 days from Neo4j, writes them into SQLite,
        and deletes them from the active Neo4j database. 
        CRITICAL RULE: Keeps messages with 'poor' feedback in Neo4j forever for analytics.
        """
        if not self._driver:
            return

        # Query messages older than 30 days that are NOT rated 'poor'
        select_old_query = """
        MATCH (s:Session)-[r:HAS_MESSAGE]->(m:Message)
        WHERE m.timestamp < datetime() - duration('P30D')
          AND (m.feedback IS NULL OR m.feedback <> 'poor')
        RETURN s.id as session_id,
               m.question as question,
               m.cypher as cypher,
               m.answer as answer,
               m.feedback as feedback,
               m.feedbackComment as feedback_comment,
               toString(m.timestamp) as timestamp,
               elementId(m) as element_id
        """
        try:
            records, _, _ = self._driver.execute_query(
                select_old_query,
                database_=self._db,
                routing_=neo4j.RoutingControl.READ
            )

            if not records:
                return

            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()

            deleted_element_ids = []
            for record in records:
                # Save to SQLite archive
                cursor.execute("""
                INSERT INTO archived_messages (session_id, question, cypher, answer, feedback, feedback_comment, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    record.get("session_id"),
                    record.get("question"),
                    record.get("cypher"),
                    record.get("answer"),
                    record.get("feedback"),
                    record.get("feedback_comment"),
                    record.get("timestamp")
                ))
                deleted_element_ids.append(record.get("element_id"))

            conn.commit()
            conn.close()

            # Batch delete archived nodes from Neo4j
            if deleted_element_ids:
                delete_query = """
                MATCH (m:Message)
                WHERE elementId(m) IN $ids
                DETACH DELETE m
                """
                self._driver.execute_query(
                    delete_query,
                    {"ids": deleted_element_ids},
                    database_=self._db,
                    routing_=neo4j.RoutingControl.WRITE
                )
                print(f"Archived {len(deleted_element_ids)} old message(s) from Neo4j to SQLite.")

        except Exception as e:
            print(f"Warning during session history archival: {e}")

    def run_sqlite_query(self, sql: str, params: tuple = ()) -> list:
        """Executes a read-only SQL query against the SQLite history database."""
        results = []
        try:
            conn = sqlite3.connect(self._db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            for r in rows:
                results.append(dict(r))
            conn.close()
        except Exception as e:
            print(f"Error querying SQLite database: {e}")
        return results

    def submit_feedback(self, session_id: str, feedback: str, comment: str):
        """Rates the session's latest message in Neo4j, then in the SQLite archive."""
        self._driver.execute_query(
            """
            MATCH (a:Session {id: $session_id})-[r:LAST_MESSAGE]->(b)
            SET b.feedback = $feedback,
                b.feedbackComment = $comment
            RETURN a, r, b
            """,
            {"session_id": session_id, "feedback": feedback, "comment": comment},
            database_=self._db,
            routing_=neo4j.RoutingControl.WRITE
        )
        self._submit_sqlite_feedback(session_id, feedback, comment)

    def _submit_sqlite_feedback(self, session_id: str, feedback: str, comment: str):
        try:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()
            # Update feedback on the latest message within the session in SQLite
            cursor.execute("""
            UPDATE archived_messages
            SET feedback = ?, feedback_comment = ?
            WHERE session_id = ? AND timestamp = (
                SELECT MAX(timestamp) FROM archived_messages WHERE session_id = ?
            )
            """, (feedback, comment, session_id, session_id))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Warning: Failed to update feedback in SQLite: {e}")
