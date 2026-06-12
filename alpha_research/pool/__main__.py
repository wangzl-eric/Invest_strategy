"""Strategy pool CLI.

Usage (from repo root, PYTHONPATH=.):

    python -m alpha_research.pool list [--state candidate]
    python -m alpha_research.pool show <strategy_id>
    python -m alpha_research.pool promote <strategy_id> --to paper --reason "..."
    python -m alpha_research.pool retire <strategy_id> --reason "..."
"""

from __future__ import annotations

import argparse
import json
import sys

from alpha_research.pool.registry import LIFECYCLE_STATES, PoolRegistry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="alpha_research.pool")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List pool entries")
    p_list.add_argument("--state", choices=LIFECYCLE_STATES, default=None)

    p_show = sub.add_parser("show", help="Show one entry (full JSON)")
    p_show.add_argument("strategy_id")

    p_promote = sub.add_parser("promote", help="Transition lifecycle state")
    p_promote.add_argument("strategy_id")
    p_promote.add_argument("--to", required=True, choices=LIFECYCLE_STATES)
    p_promote.add_argument("--reason", required=True)

    p_retire = sub.add_parser("retire", help="Retire a strategy")
    p_retire.add_argument("strategy_id")
    p_retire.add_argument("--reason", required=True)

    args = parser.parse_args(argv)
    pool = PoolRegistry()

    if args.command == "list":
        df = pool.list_entries(state=args.state)
        if df.empty:
            print("(pool is empty)")
        else:
            cols = [
                "strategy_id",
                "track",
                "state",
                "latest_run_id",
                "latest_verdict",
                "registered_at",
            ]
            print(df[cols].to_string(index=False))
        return 0

    if args.command == "show":
        print(json.dumps(pool.get(args.strategy_id), indent=2))
        return 0

    if args.command == "promote":
        entry = pool.set_state(args.strategy_id, args.to, reason=args.reason)
        print(f"{args.strategy_id}: -> {entry['state']}")
        return 0

    if args.command == "retire":
        entry = pool.set_state(args.strategy_id, "retired", reason=args.reason)
        print(f"{args.strategy_id}: -> {entry['state']}")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
