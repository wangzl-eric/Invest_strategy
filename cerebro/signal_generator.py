"""Signal code generator for the Cerebro research pipeline.

Translates research paper methodology into BaseSignal subclass code
via LLM, validates the output, and saves to auto_signals directory.

All generated files are tagged for manual review before use.
"""

import ast
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import FrozenSet, Optional, Tuple

from cerebro.config import cerebro_config
from cerebro.processing.llm_summarizer import CerebroLLMClient

logger = logging.getLogger(__name__)

# Directory where generated signals are saved
AUTO_SIGNALS_DIR = (
    Path(__file__).parent.parent / "backtests" / "strategies" / "auto_signals"
)

# Tag prepended to every generated file
GENERATED_TAG = (
    "# [CEREBRO-AUTO] — Generated signal. Manual review required before use."
)

# Modules that generated code must never import
FORBIDDEN_MODULES: FrozenSet[str] = frozenset(
    {
        "os",
        "sys",
        "subprocess",
        "shutil",
        "pathlib",
        "socket",
        "http",
        "urllib",
        "requests",
        "httpx",
        "ftplib",
        "smtplib",
        "ctypes",
        "importlib",
        "pickle",
        "shelve",
        "marshal",
        "multiprocessing",
        "threading",
        "webbrowser",
        "code",
        "codeop",
        "compileall",
    }
)

# Built-in names that must not appear in generated code
FORBIDDEN_BUILTINS: FrozenSet[str] = frozenset(
    {
        "exec",
        "eval",
        "compile",
        "__import__",
        "open",
        "globals",
        "locals",
        "breakpoint",
    }
)

# Required class methods for a valid BaseSignal subclass
REQUIRED_METHODS: FrozenSet[str] = frozenset({"compute"})

_SIGNAL_CODE_PROMPT = """\
You are a quantitative developer. Generate a Python file with ONE BaseSignal subclass.

BaseSignal has: name (str), lookback (int), compute(prices: pd.DataFrame) -> Series|DataFrame,
to_positions(signal) -> Series|DataFrame (default: sign, clipped to [-1,1]).
prices has DatetimeIndex and ticker columns with close values.

## Paper: {paper_summary}
## Signal: {signal_description}

Rules:
- Module docstring citing the paper. Import ONLY numpy, pandas, BaseSignal.
- ONE class inheriting BaseSignal with name, lookback, __init__ with defaults, compute().
- Handle NaN/inf/insufficient data. Single-column -> Series, multi-column -> DataFrame.
- ONLY pandas/numpy ops. NO network, file I/O, exec/eval. Under 120 lines.
- Output ONLY Python code, no markdown fences.
"""


@dataclass(frozen=True)
class ValidationResult:
    """Immutable result of code validation.

    Attributes:
        is_valid: Whether the code passed all checks.
        errors: Tuple of error messages (empty if valid).
    """

    is_valid: bool
    errors: Tuple[str, ...]


class SignalGenerator:
    """Generates, validates, and saves BaseSignal subclass code from paper descriptions."""

    def __init__(self, llm_client: Optional[CerebroLLMClient] = None) -> None:
        if llm_client is not None:
            self._llm = llm_client
        else:
            self._llm = CerebroLLMClient(
                model=cerebro_config.llm.premium_model,
                temperature=0.1,
            )

    async def generate_signal_code(
        self,
        paper_summary: str,
        signal_description: str,
    ) -> str:
        """Generate Python code for a BaseSignal subclass via LLM."""
        if not self._llm.is_configured:
            raise ValueError(
                "QWEN_API_KEY not configured. Set it in .env or environment."
            )

        prompt = _SIGNAL_CODE_PROMPT.format(
            paper_summary=paper_summary,
            signal_description=signal_description,
        )

        raw_response = await self._llm._call_llm_raw(prompt)
        code = _strip_markdown_fences(raw_response)
        return f"{GENERATED_TAG}\n\n{code}"

    def validate_generated_code(self, code_str: str) -> ValidationResult:
        """Validate generated code: syntax, forbidden imports/builtins, compute() method."""
        errors = []

        # 1. Syntax check
        try:
            tree = ast.parse(code_str)
        except SyntaxError as exc:
            return ValidationResult(
                is_valid=False,
                errors=(f"Syntax error: {exc}",),
            )

        # 2. Forbidden imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top_module = alias.name.split(".")[0]
                    if top_module in FORBIDDEN_MODULES:
                        errors.append(f"Forbidden import: {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module is not None:
                    top_module = node.module.split(".")[0]
                    if top_module in FORBIDDEN_MODULES:
                        errors.append(f"Forbidden import: {node.module}")

        # 3. Forbidden builtins
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id in FORBIDDEN_BUILTINS:
                errors.append(f"Forbidden builtin usage: {node.id}")
            elif isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id in FORBIDDEN_BUILTINS:
                    errors.append(f"Forbidden call: {func.id}()")

        # 4. Must contain a class with compute()
        class_names = []
        has_compute = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_names.append(node.name)
                method_names = frozenset(
                    item.name
                    for item in node.body
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                )
                if REQUIRED_METHODS.issubset(method_names):
                    has_compute = True

        if not class_names:
            errors.append("No class definition found in generated code.")
        elif not has_compute:
            errors.append(
                "No class with a compute() method found. "
                f"Classes found: {', '.join(class_names)}"
            )

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=tuple(errors),
        )

    def save_signal(self, code_str: str, signal_name: str) -> Path:
        """Save validated signal code to backtests/strategies/auto_signals/<name>.py."""
        result = self.validate_generated_code(code_str)
        if not result.is_valid:
            raise ValueError(
                "Code validation failed. Errors:\n"
                + "\n".join(f"  - {e}" for e in result.errors)
            )

        safe_name = _sanitize_filename(signal_name)
        AUTO_SIGNALS_DIR.mkdir(parents=True, exist_ok=True)

        init_file = AUTO_SIGNALS_DIR / "__init__.py"
        if not init_file.exists():
            init_file.write_text(
                "# [CEREBRO-AUTO] — Auto-generated signals directory.\n"
                "# Signals in this package are generated by "
                "cerebro/signal_generator.py.\n"
                "# Manual review is required before use in live trading.\n"
            )

        target = AUTO_SIGNALS_DIR / f"{safe_name}.py"
        target.write_text(code_str, encoding="utf-8")
        logger.info("Saved auto-generated signal to %s", target)
        return target


# ---------------------------------------------------------------------------
# CerebroLLMClient extension: raw text response (no JSON parsing)
# ---------------------------------------------------------------------------


def _patch_llm_client() -> None:
    """Add _call_llm_raw to CerebroLLMClient for plain-text code generation."""
    if hasattr(CerebroLLMClient, "_call_llm_raw"):
        return

    import httpx as _httpx

    async def _call_llm_raw(self: CerebroLLMClient, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self._model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": self._max_tokens,
            "temperature": self._temperature,
        }
        async with _httpx.AsyncClient(timeout=90.0) as client:
            try:
                resp = await client.post(
                    f"{self._base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()
                self._record_usage(data)
                return data["choices"][0]["message"]["content"]
            except _httpx.HTTPStatusError as exc:
                logger.error("LLM HTTP error: %s", exc.response.status_code)
                self._record_failure(str(exc))
                raise RuntimeError(f"LLM API error: {exc.response.status_code}")
            except Exception as exc:
                logger.error("LLM error: %s", exc)
                self._record_failure(str(exc))
                raise RuntimeError(f"LLM API error: {exc}")

    CerebroLLMClient._call_llm_raw = _call_llm_raw  # type: ignore[attr-defined]


_patch_llm_client()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _strip_markdown_fences(text: str) -> str:
    """Remove markdown code fences (```python ... ```) from LLM output."""
    text = text.strip()
    text = re.sub(r"^```(?:python)?\s*\n?", "", text)
    text = re.sub(r"\n?```\s*$", "", text)
    return text.strip()


def _sanitize_filename(name: str) -> str:
    """Sanitize a signal name into a valid Python module filename."""
    sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    sanitized = re.sub(r"_+", "_", sanitized).strip("_").lower()
    if sanitized and sanitized[0].isdigit():
        sanitized = f"signal_{sanitized}"
    return sanitized or "unnamed_signal"
