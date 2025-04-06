"""
Token Counter Module for VoiceScribe Studio

This module provides functions and classes for counting tokens used in LLM API
calls and tracking usage metrics. It supports both DeepSeek and Claude models.
"""

import tiktoken
import time
import json
import logging
import os
import sqlite3
from typing import Dict, Any, Tuple, Optional, List

logger = logging.getLogger(__name__)

# Token counting functions
def count_tokens(text: str, model: str = "cl100k_base") -> int:
    """
    Count tokens for text using the specified encoding.
    Both DeepSeek and Claude use approximately the same tokenization as cl100k_base.

    Args:
        text: The text to count tokens for
        model: The encoding model to use (default: cl100k_base)

    Returns:
        int: Number of tokens
    """
    if not text:
        return 0

    try:
        encoding = tiktoken.get_encoding(model)
        return len(encoding.encode(text))
    except Exception as e:
        logger.error(f"Error counting tokens: {e}")
        # Fallback token estimation: ~4 chars per token
        return len(text) // 4


class TokenTracker:
    """
    Class for tracking token usage across different LLM models.
    """

    def __init__(self, db_path="data/token_usage.db"):
        """
        Initialize the token tracker with a database connection.

        Args:
            db_path: Path to the SQLite database for storing token usage
        """
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        """Create database tables if they don't exist"""
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create token usage table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS token_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL NOT NULL,
            model TEXT NOT NULL,
            template TEXT,
            is_fallback INTEGER DEFAULT 0,
            input_tokens INTEGER NOT NULL,
            output_tokens INTEGER NOT NULL,
            total_tokens INTEGER NOT NULL,
            word_count INTEGER,
            tokens_per_word REAL,
            audience TEXT,
            length TEXT,
            tone TEXT,
            subject TEXT,
            session_id TEXT,
            processing_time REAL,
            success INTEGER DEFAULT 1,
            is_test INTEGER DEFAULT 0
        )
        ''')

        conn.commit()
        conn.close()

    def track_generation(self,
                         model: str,
                         input_text: str,
                         output_text: str,
                         template: Optional[str] = None,
                         is_fallback: bool = False,
                         parameters: Optional[Dict[str, Any]] = None,
                         session_id: Optional[str] = None,
                         is_test: bool = False,
                         success: bool = True) -> Dict[str, Any]:
        """
        Track token usage for a script generation request.

        Args:
            model: Model used ("deepseek" or "claude")
            input_text: The prompt sent to the model
            output_text: The response from the model
            template: The template used
            is_fallback: Whether this was a fallback generation
            parameters: Generation parameters (length, tone, etc)
            session_id: Optional session identifier
            is_test: Whether this was a test generation
            success: Whether the generation was successful

        Returns:
            Dict with token usage metrics
        """
        start_time = time.time()
        parameters = parameters or {}

        # Count tokens
        input_tokens = count_tokens(input_text)
        output_tokens = count_tokens(output_text)
        total_tokens = input_tokens + output_tokens

        # Calculate token efficiency
        word_count = len(output_text.split()) if output_text else 0
        tokens_per_word = output_tokens / max(word_count, 1)  # Avoid division by zero

        # Calculate estimated cos
        cost = self.estimate_cost(model, input_tokens, output_tokens)

        # Prepare data for database
        usage_data = {
            "timestamp": time.time(),
            "model": model,
            "template": template,
            "is_fallback": 1 if is_fallback else 0,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "word_count": word_count,
            "tokens_per_word": tokens_per_word,
            "audience": parameters.get("audience"),
            "length": parameters.get("length"),
            "tone": parameters.get("tone"),
            "subject": parameters.get("subject"),
            "session_id": session_id,
            "processing_time": time.time() - start_time,
            "success": 1 if success else 0,
            "is_test": 1 if is_test else 0
        }

        # Save to database
        self._save_to_db(usage_data)

        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "word_count": word_count,
            "tokens_per_word": tokens_per_word,
            "estimated_cost": cost,
            "processing_time": time.time() - start_time
        }

    def _save_to_db(self, usage_data: Dict[str, Any]):
        """Save token usage data to the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create placeholders and values list
            placeholders = ", ".join(["?"] * len(usage_data))
            columns = ", ".join(usage_data.keys())
            values = list(usage_data.values())

            # Insert data
            cursor.execute(
                f"INSERT INTO token_usage ({columns}) VALUES ({placeholders})",
                values
            )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error saving token usage to database: {e}")

    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """
        Estimate the cost of a generation based on current pricing.

        Args:
            model: Model used ("deepseek" or "claude")
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            float: Estimated cost in USD
        """
        if model.lower() == "deepseek":
            # DeepSeek pricing (~$15 per 1M output tokens)
            return output_tokens * 0.000015
        elif model.lower() == "claude":
            # Claude pricing ($3 per 1M input, $15 per 1M output)
            return (input_tokens * 0.000003) + (output_tokens * 0.000015)
        else:
            # Default case
            return 0.0

    def get_usage_summary(self, days: int = 30, include_tests: bool = False) -> Dict[str, Any]:
        """
        Get summary of token usage for the specified time period.

        Args:
            days: Number of days to include
            include_tests: Whether to include test runs

        Returns:
            Dict with usage summary
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Calculate cutoff time
            cutoff_time = time.time() - (days * 24 * 60 * 60)

            # Base query parts
            query_base = """
            FROM token_usage
            WHERE timestamp > ?
            """

            params = [cutoff_time]

            # Add test filter if needed
            if not include_tests:
                query_base += " AND is_test = 0"

            # Get total token usage by model
            cursor.execute(f"""
            SELECT model,
                   SUM(input_tokens) as input_tokens,
                   SUM(output_tokens) as output_tokens,
                   SUM(total_tokens) as total_tokens,
                   COUNT(*) as request_coun
            {query_base}
            GROUP BY model
            """, params)

            model_usage = {}
            for row in cursor.fetchall():
                model_usage[row['model']] = {
                    "input_tokens": row['input_tokens'],
                    "output_tokens": row['output_tokens'],
                    "total_tokens": row['total_tokens'],
                    "request_count": row['request_count'],
                    "estimated_cost": self.estimate_cost(
                        row['model'],
                        row['input_tokens'],
                        row['output_tokens']
                    )
                }

            # Get usage by template
            cursor.execute(f"""
            SELECT template, SUM(total_tokens) as total_tokens, COUNT(*) as request_coun
            {query_base}
            GROUP BY template
            """, params)

            template_usage = {}
            for row in cursor.fetchall():
                if row['template']:  # Skip None templates
                    template_usage[row['template']] = {
                        "total_tokens": row['total_tokens'],
                        "request_count": row['request_count']
                    }

            # Get fallback percentage
            cursor.execute(f"""
            SELECT COUNT(*) as total, SUM(is_fallback) as fallbacks
            {query_base}
            """, params)

            row = cursor.fetchone()
            total = row['total']
            fallbacks = row['fallbacks']
            fallback_rate = (fallbacks / total) if total > 0 else 0

            # Get usage over time (daily)
            cursor.execute(f"""
            SELECT
                CAST(((timestamp - ?) / 86400) AS INT) as day,
                SUM(total_tokens) as tokens
            {query_base}
            GROUP BY day
            ORDER BY day
            """, params + params[:1])

            daily_usage = []
            for row in cursor.fetchall():
                day_timestamp = cutoff_time + (row['day'] * 86400)
                daily_usage.append({
                    "day": row['day'],
                    "date": time.strftime("%Y-%m-%d", time.localtime(day_timestamp)),
                    "tokens": row['tokens']
                })

            conn.close()

            # Calculate total cos
            total_cost = sum(model['estimated_cost'] for model in model_usage.values())

            return {
                "model_usage": model_usage,
                "template_usage": template_usage,
                "fallback_rate": fallback_rate,
                "daily_usage": daily_usage,
                "total_cost": total_cost,
                "total_requests": total,
                "days": days,
                "include_tests": include_tests
            }

        except Exception as e:
            logger.error(f"Error getting usage summary: {e}")
            return {
                "error": str(e),
                "model_usage": {},
                "template_usage": {},
                "fallback_rate": 0,
                "daily_usage": [],
                "total_cost": 0,
                "total_requests": 0,
                "days": days,
                "include_tests": include_tests
            }

# Create a global instance of the token tracker
token_tracker = TokenTracker()