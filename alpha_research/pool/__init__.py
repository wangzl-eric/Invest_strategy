"""Strategy pool: lifecycle registry for registered strategies.

State lives in the ``strategy_pool`` table (``core.models.StrategyPoolEntry``);
the canonical spec is the git-versioned manifest YAML. See
``alpha_research.pool.registry`` and the CLI: ``python -m alpha_research.pool``.
"""

from alpha_research.pool.registry import (  # noqa: F401
    LIFECYCLE_STATES,
    PoolRegistry,
    TransitionError,
)

__all__ = ["PoolRegistry", "TransitionError", "LIFECYCLE_STATES"]
