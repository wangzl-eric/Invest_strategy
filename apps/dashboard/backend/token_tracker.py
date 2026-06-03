"""Token usage tracking for LLM API calls.

Tracks token usage across LLM calls to monitor costs and usage patterns.
Stores usage stats in memory and provides retrieval API.
"""

import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class TokenUsageRecord:
    """Single token usage record."""

    model: str
    prompt_tokens: int
    completion_tokens: int
    endpoint: str
    success: bool
    timestamp: datetime = field(default_factory=datetime.utcnow)

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


class TokenTracker:
    """Thread-safe token usage tracker (singleton)."""

    def __init__(self) -> None:
        self._records: List[TokenUsageRecord] = []
        self._lock = threading.Lock()

    def record_usage(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        endpoint: str,
        success: bool = True,
    ) -> None:
        record = TokenUsageRecord(
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            endpoint=endpoint,
            success=success,
        )
        with self._lock:
            self._records.append(record)

    def get_summary(self) -> Dict:
        with self._lock:
            records = list(self._records)
        total_prompt = sum(r.prompt_tokens for r in records)
        total_completion = sum(r.completion_tokens for r in records)
        return {
            "total_calls": len(records),
            "total_prompt_tokens": total_prompt,
            "total_completion_tokens": total_completion,
            "total_tokens": total_prompt + total_completion,
            "successful_calls": sum(1 for r in records if r.success),
            "failed_calls": sum(1 for r in records if not r.success),
        }

    def get_records(self) -> List[TokenUsageRecord]:
        with self._lock:
            return list(self._records)


_tracker: Optional[TokenTracker] = None
_tracker_lock = threading.Lock()


def get_token_tracker() -> TokenTracker:
    global _tracker
    if _tracker is None:
        with _tracker_lock:
            if _tracker is None:
                _tracker = TokenTracker()
    return _tracker
