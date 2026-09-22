"""Market/alt data connectors (retrieval only)."""

from alpha_research.quant_data.connectors.akshare_global import (
    AKSHARE_BARS_DATASETS,
    AkShareConnector,
    AkShareUnavailable,
)

__all__ = [
    "AkShareConnector",
    "AkShareUnavailable",
    "AKSHARE_BARS_DATASETS",
]
