"""Broker interfaces."""

from __future__ import annotations

from typing import Protocol

from execution.types import Fill, OrderRequest


class Broker(Protocol):
    name: str

    def submit_order(self, order: OrderRequest) -> str:
        """Submit an order and return external order id."""

    def poll_fills(self) -> list[Fill]:
        """Return any new fills since last poll."""

