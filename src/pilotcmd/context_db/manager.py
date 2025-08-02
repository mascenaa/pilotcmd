"""
Context manager for storing and retrieving command history and context.
"""

import sqlite3
import json
import os
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from pathlib import Path

from pilotcmd.nlp.parser import Command
from pilotcmd.executor.command_executor import ExecutionResult
from pilotcmd.os_utils.detector import OSInfo


@dataclass
class HistoryEntry:
    """Represents a command history entry."""
    id: Optional[int]
    timestamp: str
    prompt: str
    commands: List[str]
    os_info: str
    success: bool
    execution_time: float
    results: Optional[str] = None


class ContextManager:
    """Manages the local SQLite database for command context and history."""
    
    def __init__(self, db_path: Optional[str] = None):
        # Default database location
        if db_path is None:
            home_dir = Path.home()
            app_dir = home_dir / ".pilotcmd"
            app_dir.mkdir(exist_ok=True)
            db_path = str(app_dir / "context.db")
        
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize the SQLite database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Command history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS command_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    commands TEXT NOT NULL,  -- JSON array of commands
                    os_info TEXT NOT NULL,   -- JSON object with OS details
                    success BOOLEAN NOT NULL,
                    execution_time REAL NOT NULL,
                    results TEXT             -- JSON array of execution results
                )
            """)
            
            # Context metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS context_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Command templates table (for future use)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS command_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    template TEXT NOT NULL,  -- JSON template structure
                    tags TEXT,               -- JSON array of tags
                    usage_count INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Create indexes for better search performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_command_history_timestamp 
                ON command_history(timestamp DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_command_history_prompt 
                ON command_history(prompt)
            """)
            
            conn.commit()
    
    def save_prompt(self, prompt: str, commands: List[Command], os_info: OSInfo) -> int:
        """
        Save a prompt and its generated commands before execution.
        
        Args:
            prompt: The natural language prompt
            commands: List of generated commands
            os_info: Operating system information
            
        Returns:
            The ID of the saved entry
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            commands_json = json.dumps([cmd.command for cmd in commands])
            os_info_json = json.dumps({
                "type": os_info.type.value,
                "name": os_info.name,
                "version": os_info.version,
                "architecture": os_info.architecture,
                "shell": os_info.shell,
                "package_manager": os_info.package_manager
            })
            
            cursor.execute("""
                INSERT INTO command_history 
                (timestamp, prompt, commands, os_info, success, execution_time)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (timestamp, prompt, commands_json, os_info_json, False, 0.0))
            
            conn.commit()
            return cursor.lastrowid
    
    def save_execution_results(self, results: List[ExecutionResult]) -> None:
        """
        Update the most recent entry with execution results.
        
        Args:
            results: List of execution results
        """
        if not results:
            return
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get the most recent entry
            cursor.execute("""
                SELECT id FROM command_history 
                ORDER BY timestamp DESC 
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            if not row:
                return
            
            entry_id = row[0]
            
            # Calculate overall success and execution time
            success = all(result.success for result in results)
            total_execution_time = sum(result.execution_time for result in results)
            
            # Serialize results
            results_json = json.dumps([
                {
                    "command": result.command.command,
                    "status": result.status.value,
                    "return_code": result.return_code,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "execution_time": result.execution_time,
                    "error_message": result.error_message
                }
                for result in results
            ])
            
            # Update the entry
            cursor.execute("""
                UPDATE command_history 
                SET success = ?, execution_time = ?, results = ?
                WHERE id = ?
            """, (success, total_execution_time, results_json, entry_id))
            
            conn.commit()
    
    def get_history(self, limit: int = 10, search: Optional[str] = None) -> List[HistoryEntry]:
        """
        Get command history entries.
        
        Args:
            limit: Maximum number of entries to return
            search: Optional search term to filter results
            
        Returns:
            List of HistoryEntry objects
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT id, timestamp, prompt, commands, os_info, success, execution_time, results
                FROM command_history
            """
            params = []
            
            if search:
                query += " WHERE prompt LIKE ? OR commands LIKE ?"
                search_term = f"%{search}%"
                params.extend([search_term, search_term])
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            entries = []
            for row in rows:
                commands_list = json.loads(row[3]) if row[3] else []
                
                entry = HistoryEntry(
                    id=row[0],
                    timestamp=row[1],
                    prompt=row[2],
                    commands=commands_list,
                    os_info=row[4],
                    success=bool(row[5]),
                    execution_time=row[6],
                    results=row[7]
                )
                entries.append(entry)
            
            return entries
    
    def get_similar_commands(self, prompt: str, limit: int = 5) -> List[HistoryEntry]:
        """
        Find similar commands based on prompt similarity.
        
        Args:
            prompt: The current prompt to find similar commands for
            limit: Maximum number of similar commands to return
            
        Returns:
            List of similar HistoryEntry objects
        """
        # Simple keyword-based similarity for now
        # In the future, this could use vector embeddings
        keywords = set(prompt.lower().split())
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, timestamp, prompt, commands, os_info, success, execution_time, results
                FROM command_history
                WHERE success = 1
                ORDER BY timestamp DESC
            """)
            
            rows = cursor.fetchall()
            scored_entries = []
            
            for row in rows:
                entry_prompt = row[2].lower()
                entry_keywords = set(entry_prompt.split())
                
                # Calculate simple keyword overlap score
                overlap = len(keywords.intersection(entry_keywords))
                if overlap > 0:
                    commands_list = json.loads(row[3]) if row[3] else []
                    
                    entry = HistoryEntry(
                        id=row[0],
                        timestamp=row[1],
                        prompt=row[2],
                        commands=commands_list,
                        os_info=row[4],
                        success=bool(row[5]),
                        execution_time=row[6],
                        results=row[7]
                    )
                    scored_entries.append((overlap, entry))
            
            # Sort by score and return top results
            scored_entries.sort(key=lambda x: x[0], reverse=True)
            return [entry for _, entry in scored_entries[:limit]]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total commands
            cursor.execute("SELECT COUNT(*) FROM command_history")
            total_commands = cursor.fetchone()[0]
            
            # Successful commands
            cursor.execute("SELECT COUNT(*) FROM command_history WHERE success = 1")
            successful_commands = cursor.fetchone()[0]
            
            # Average execution time
            cursor.execute("SELECT AVG(execution_time) FROM command_history WHERE success = 1")
            avg_execution_time = cursor.fetchone()[0] or 0.0
            
            # Most common prompts
            cursor.execute("""
                SELECT prompt, COUNT(*) as count 
                FROM command_history 
                GROUP BY prompt 
                ORDER BY count DESC 
                LIMIT 5
            """)
            common_prompts = cursor.fetchall()
            
            return {
                "total_commands": total_commands,
                "successful_commands": successful_commands,
                "success_rate": successful_commands / total_commands if total_commands > 0 else 0.0,
                "average_execution_time": avg_execution_time,
                "common_prompts": [{"prompt": row[0], "count": row[1]} for row in common_prompts]
            }
    
    def clear_history(self, older_than_days: Optional[int] = None) -> int:
        """
        Clear command history.
        
        Args:
            older_than_days: If specified, only clear entries older than this many days
            
        Returns:
            Number of entries deleted
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if older_than_days:
                from datetime import timedelta
                cutoff_date = (datetime.now() - timedelta(days=older_than_days)).isoformat()
                cursor.execute("DELETE FROM command_history WHERE timestamp < ?", (cutoff_date,))
            else:
                cursor.execute("DELETE FROM command_history")
            
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count
