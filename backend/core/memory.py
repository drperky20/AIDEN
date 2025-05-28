"""
Core Memory Management for AIDEN V2
Handles conversation history and other memory-related functionalities.
Integrates with SQLite for persistent storage and prepares for Mem0.
"""
import logging
import aiosqlite
import json
from datetime import datetime
from typing import List, Tuple, Dict, Any, Optional, Union

from backend.config import settings # Use the new config

logger = logging.getLogger(__name__)

class MemoryManager:
    """
    Manages AIDEN's memory, primarily conversation history using SQLite.
    Future extensions can include Mem0 integration or other vector stores.
    """
    def __init__(self, db_url: str = settings.DATABASE_URL):
        """
        Initializes the MemoryManager.
        Args:
            db_url: Connection string for the database. For SQLite, it's a file path.
        """
        self.db_url = db_url
        # For SQLite, db_url might be like "sqlite:///./data/aiden_memory.db"
        # We need to extract the actual file path for aiosqlite.connect()
        if self.db_url.startswith("sqlite:///"):
            self.sqlite_path = self.db_url[len("sqlite:///"):]
        else:
            # Handle other database types or raise an error if not supported
            # For now, we primarily focus on SQLite as per current setup
            logger.warning(f"Database URL {self.db_url} is not standard SQLite. Assuming it's a valid path for aiosqlite.")
            self.sqlite_path = self.db_url


    async def _get_db_connection(self):
        """Returns an aiosqlite connection object."""
        # Ensure the directory for the SQLite DB exists
        if self.sqlite_path != ":memory:":
            db_path_obj = settings.PROJECT_ROOT / self.sqlite_path
            db_path_obj.parent.mkdir(parents=True, exist_ok=True)
            return await aiosqlite.connect(str(db_path_obj))
        return await aiosqlite.connect(self.sqlite_path)


    async def initialize_database(self):
        """
        Initializes the database schema if it doesn't exist.
        Currently creates a 'conversations' table.
        """
        try:
            # Create fresh connection for initialization
            if self.sqlite_path != ":memory:":
                db_path_obj = settings.PROJECT_ROOT / self.sqlite_path
                db_path_obj.parent.mkdir(parents=True, exist_ok=True)
                db_path = str(db_path_obj)
            else:
                db_path = self.sqlite_path
                
            async with aiosqlite.connect(db_path) as db:
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT DEFAULT 'default', -- For multi-user or session support
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        user_message TEXT NOT NULL,
                        agent_response TEXT NOT NULL,
                        metadata TEXT  -- JSON string for additional data like tool calls
                    )
                """)
                # Example of a user preferences table (can be expanded)
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS user_preferences (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT UNIQUE NOT NULL,
                        preferences TEXT -- JSON string for preferences
                    )
                """)
                await db.commit()
            logger.info(f"📚 Database '{self.sqlite_path}' initialized/verified successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize database at {self.sqlite_path}: {e}", exc_info=True)
            raise

    async def add_conversation_turn(self, user_message: str, agent_response: str, session_id: str = "default", metadata: dict = None):
        """
        Adds a user message and agent response to the conversation history.
        Args:
            user_message: The message from the user.
            agent_response: The response from the agent.
            session_id: Identifier for the conversation session.
            metadata: Optional dictionary for storing additional context (e.g., tool calls).
        """
        try:
            # Create fresh connection
            if self.sqlite_path != ":memory:":
                db_path_obj = settings.PROJECT_ROOT / self.sqlite_path
                db_path = str(db_path_obj)
            else:
                db_path = self.sqlite_path
                
            async with aiosqlite.connect(db_path) as db:
                await db.execute(
                    "INSERT INTO conversations (session_id, user_message, agent_response, metadata, timestamp) VALUES (?, ?, ?, ?, ?)",
                    (session_id, user_message, agent_response, json.dumps(metadata) if metadata else None, datetime.now())
                )
                await db.commit()
            logger.debug(f"📝 Conversation turn saved for session {session_id}.")
        except Exception as e:
            logger.error(f"Failed to add conversation turn to DB: {e}", exc_info=True)


    async def get_conversation_history(self, session_id: str = "default", limit: int = settings.MAX_HISTORY_MESSAGES) -> List[Tuple[str, str]]:
        """
        Retrieves the last N conversation turns for a given session.
        Returns a list of tuples, where each tuple is (speaker, message).
        Speaker is 'User' or 'Agent'.
        Args:
            session_id: The session ID to retrieve history for.
            limit: The maximum number of messages (user + agent pairs) to retrieve.
        Returns:
            A list of tuples, e.g., [('User', 'Hello'), ('Agent', 'Hi there!')]
        """
        history = []
        try:
            # Create fresh connection
            if self.sqlite_path != ":memory:":
                db_path_obj = settings.PROJECT_ROOT / self.sqlite_path
                db_path = str(db_path_obj)
            else:
                db_path = self.sqlite_path
                
            async with aiosqlite.connect(db_path) as db:
                async with db.execute(
                    "SELECT user_message, agent_response FROM conversations WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
                    (session_id, limit)
                ) as cursor:
                    rows = await cursor.fetchall()
                    for row in reversed(rows):  # To maintain chronological order for the prompt
                        history.append(("User", row[0]))
                        history.append(("Agent", row[1]))
            logger.debug(f"Retrieved {len(rows)} conversation pairs for session {session_id}.")
            return history
        except Exception as e:
            logger.error(f"Error retrieving conversation history for session {session_id}: {e}", exc_info=True)
            return []

    async def get_formatted_conversation_history(self, session_id: str = "default", limit: int = settings.MAX_HISTORY_MESSAGES) -> str:
        """
        Retrieves the last N conversation turns as a single formatted string.
        """
        history_tuples = await self.get_conversation_history(session_id, limit)
        if not history_tuples:
            return ""
        
        formatted_history = []
        for speaker, message in history_tuples:
            formatted_history.append(f"{speaker}: {message}")
        return "\n".join(formatted_history)

    # --- Placeholder for Mem0 Integration ---
    async def store_memory_mem0(self, user_id: str, data: dict, namespace: Optional[str] = None):
        if not settings.is_mem0_api_key_valid:
            logger.warning("Mem0 API key not configured. Skipping memory storage.")
            return
        # try:
        #     from mem0 import MemoryClient # Import locally to avoid hard dependency if not used
        #     mem_client = MemoryClient(api_key=settings.MEM0_API_KEY)
        #     mem_client.upsert(user_id=user_id, namespace=namespace, data=data)
        #     logger.info(f"Stored memory in Mem0 for user {user_id}")
        # except ImportError:
        #     logger.error("Mem0 client library not installed. pip install mem0")
        # except Exception as e:
        #     logger.error(f"Failed to store memory in Mem0: {e}")
        logger.info("Mem0 store_memory_mem0 called (actual implementation commented out). Ensure 'mem0' is in requirements.txt if used.")


    async def query_memory_mem0(self, user_id: str, query: str, namespace: Optional[str] = None) -> Optional[str]:
        if not settings.is_mem0_api_key_valid:
            logger.warning("Mem0 API key not configured. Skipping memory query.")
            return None
        # try:
        #     from mem0 import MemoryClient
        #     mem_client = MemoryClient(api_key=settings.MEM0_API_KEY)
        #     result = mem_client.query(user_id=user_id, query=query, namespace=namespace)
        #     logger.info(f"Queried memory from Mem0 for user {user_id}")
        #     return result
        # except ImportError:
        #     logger.error("Mem0 client library not installed. pip install mem0")
        # except Exception as e:
        #     logger.error(f"Failed to query memory from Mem0: {e}")
        # return None
        logger.info("Mem0 query_memory_mem0 called (actual implementation commented out).")
        return "Placeholder Mem0 response."

# Global instance (optional, can be instantiated per request or globally)
memory_manager = MemoryManager()

# Example usage (for testing or direct script execution):
async def main():
    import json # Required for metadata in add_conversation_turn
    logging.basicConfig(level=logging.DEBUG)
    logger.info("Initializing memory manager and database...")
    await memory_manager.initialize_database()
    
    logger.info("Adding a test conversation...")
    await memory_manager.add_conversation_turn("Hello AIDEN V2!", "Hello User! How can I help you today in V2?")
    await memory_manager.add_conversation_turn("What's new?", "Lots of refactoring and new memory systems!", metadata={"tool_used": "self_reflection"})
    
    logger.info("Retrieving conversation history...")
    history_str = await memory_manager.get_formatted_conversation_history()
    print("--- Formatted History ---")
    print(history_str)
    
    history_tuples = await memory_manager.get_conversation_history()
    print("--- History Tuples ---")
    for speaker, msg in history_tuples:
        print(f"{speaker}: {msg}")

if __name__ == "__main__":
    # This import is needed for the main function when run directly
    import json 
    asyncio.run(main()) 