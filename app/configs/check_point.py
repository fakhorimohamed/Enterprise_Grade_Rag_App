import logfire
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool

from app.configs.config import settings


class CheckpointManager:
    """Manages LangGraph checkpointers with production-grade resilience."""

    def __init__(self):
        self._pool: ConnectionPool | None = None
        self._checkpointer: BaseCheckpointSaver | None = None

    def get_checkpointer(self) -> BaseCheckpointSaver:
        """Return cached checkpointer or create new one with fallback."""
        if self._checkpointer is not None:
            return self._checkpointer

        try:
            self._create_pool()

            try:
                with PostgresSaver.from_conn_string(settings.postgres_uri) as setup_saver:
                    setup_saver.setup()
            except Exception as e:
                logfire.warning(f"️ Postgres setup failed ({e}); falling back to MemorySaver.")
                self._pool.close()
                self._pool = None
                self._checkpointer = MemorySaver()
                return self._checkpointer

            self._checkpointer = PostgresSaver(self._pool)
            logfire.info("Postgres checkpointer configured.")

        except Exception as e:
            logfire.warning(
                f"Postgres unavailable ({e}); using MemorySaver. "
                "WARNING: State will be lost on restart!"
            )
            self._checkpointer = MemorySaver()

        return self._checkpointer
    def _create_pool (self) :
        self._pool = ConnectionPool(
                        conninfo=settings.postgres_uri,
                        max_size=20,
                        open=False,
                        timeout=10,
                        num_workers=3,
                        check=ConnectionPool.check_connection,
                        max_idle=240,
                    )
        self._pool.open()
        conn = self._pool.getconn()
        self._pool.putconn(conn)

    def close(self):
        """Clean up resources on shutdown."""
        if self._pool:
            self._pool.close()
            self._pool = None
        self._checkpointer = None