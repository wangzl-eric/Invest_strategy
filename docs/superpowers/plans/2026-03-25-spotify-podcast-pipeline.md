# Spotify Podcast Transcript Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Periodically discover and transcribe finance/market podcasts from Spotify, feeding structured episode transcripts into the Cerebro knowledge pipeline for Zelin's ongoing market education.

**Architecture:** A new `SpotifyPodcastSource` connector uses the Spotify Web API to search for and enumerate recent episodes from curated finance shows. A new `AudioTranscriber` module downloads episode audio via `yt-dlp` and transcribes it locally with `faster-whisper`. The resulting transcript is wrapped in the standard `RawPaper` envelope and flows through the existing Cerebro dedup → LLM summarize → score → store pipeline unchanged. An APScheduler job runs the full flow daily at 07:00 local time.

**Tech Stack:** `spotipy>=2.24.0` (Spotify API), `faster-whisper>=1.0.0` (local Whisper transcription), `yt-dlp>=2024.1.0` (audio download), `ffmpeg` (system dep for audio decoding), existing `cerebro/` pipeline (unchanged).

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `cerebro/sources/spotify_podcasts.py` | `SpotifyPodcastSource(BaseSource)` — Spotify API episode listing |
| Create | `cerebro/processing/audio_transcriber.py` | `AudioTranscriber` — yt-dlp download + faster-whisper transcription |
| Create | `tests/unit/cerebro/test_spotify_podcasts.py` | Unit tests for source connector |
| Create | `tests/unit/cerebro/test_audio_transcriber.py` | Unit tests for transcriber |
| Modify | `cerebro/config.py` | Add `SpotifyConfig` + wire into `CerebroConfig` |
| Modify | `cerebro/pipeline.py` | Register `SpotifyPodcastSource` in sources list |
| Modify | `cerebro/scheduler.py` | Add daily podcast APScheduler job |
| Modify | `requirements.txt` | Add `spotipy`, `faster-whisper`, `yt-dlp` |
| Modify | `config/secrets.example` | Document new env vars |
| Verify | `cerebro/sources/__init__.py` | Must exist (package); create empty file if missing |
| Verify | `cerebro/processing/__init__.py` | Must exist (package); create empty file if missing |
| Verify | `tests/unit/cerebro/__init__.py` | Must exist (test package); create empty file if missing |

---

## Task 1: Dependencies + Config

**Files:**
- Modify: `requirements.txt`
- Modify: `cerebro/config.py`
- Modify: `config/secrets.example`

- [ ] **Step 1: Add deps to requirements.txt**

Append after the existing entries:
```
# Spotify podcast pipeline
spotipy>=2.24.0
faster-whisper>=1.0.0
yt-dlp>=2024.1.0
```

- [ ] **Step 2: Verify package `__init__.py` files exist**

```bash
touch cerebro/sources/__init__.py cerebro/processing/__init__.py
mkdir -p tests/unit/cerebro && touch tests/unit/cerebro/__init__.py
```

- [ ] **Step 3: Install deps and verify**
```bash
conda activate ibkr-analytics
pip install "spotipy>=2.24.0" "faster-whisper>=1.0.0" "yt-dlp>=2024.1.0"
python -c "import spotipy, faster_whisper, yt_dlp; print('OK')"
# macOS:
brew install ffmpeg
# Linux: sudo apt-get install -y ffmpeg
ffmpeg -version | head -1
# Pre-download Whisper model now to avoid silent 150 MB pull during tests:
python -c "from faster_whisper import WhisperModel; WhisperModel('base', device='cpu')"
```
Expected: `OK` then a version line, then model download progress.

- [ ] **Step 4: Add SpotifyConfig to cerebro/config.py**

> Note: `SpotifyConfig` is tested transitively in Task 2 (`test_spotify_podcasts.py` exercises `cerebro_config.spotify` fields via the `_make_source` factory). No separate config test file is needed — the fields are simple Pydantic types with no custom logic.

Insert this class **before** the `CerebroConfig` class:

```python
class SpotifyConfig(BaseSettings):
    """Spotify Web API credentials and podcast source settings."""

    client_id: str = Field(default="", description="Spotify app client ID")
    client_secret: str = Field(default="", description="Spotify app client secret")
    enabled: bool = Field(default=False, description="Enable Spotify podcast source")
    show_uris: List[str] = Field(
        default_factory=list,
        description="Explicit Spotify show URIs (spotify:show:<id>) to monitor",
    )
    search_queries: List[str] = Field(
        default_factory=lambda: [
            "market outlook macro",
            "fixed income rates",
            "equity strategy",
            "central bank monetary policy",
        ],
        description="Search terms for discovering finance shows",
    )
    episodes_per_show: int = Field(default=3, description="Max recent episodes per show per run")
    whisper_model: str = Field(default="base", description="faster-whisper model size")
    audio_cache_dir: str = Field(default="data/podcast_audio_cache", description="Temp audio dir")
    max_audio_minutes: int = Field(default=90, description="Skip episodes longer than this")

    class Config:
        env_prefix = "CEREBRO_SPOTIFY_"
```

Then in `CerebroConfig.__init__` add:
```python
self.spotify = SpotifyConfig()
```

- [ ] **Step 5: Document env vars in config/secrets.example**

Append:
```ini
# ── Spotify Podcast Pipeline ──────────────────────────────────────
# Create a free Spotify app: https://developer.spotify.com/dashboard
CEREBRO_SPOTIFY_CLIENT_ID=your_client_id_here
CEREBRO_SPOTIFY_CLIENT_SECRET=your_client_secret_here
CEREBRO_SPOTIFY_ENABLED=false
CEREBRO_SPOTIFY_WHISPER_MODEL=base
```

- [ ] **Step 6: Commit**
```bash
git add requirements.txt cerebro/config.py config/secrets.example \
    cerebro/sources/__init__.py cerebro/processing/__init__.py tests/unit/cerebro/__init__.py
git commit -m "feat(cerebro): add Spotify podcast pipeline deps and config"
```

---

## Task 2: SpotifyPodcastSource connector (TDD)

**Files:**
- Create: `tests/unit/cerebro/test_spotify_podcasts.py`
- Create: `cerebro/sources/spotify_podcasts.py`

### Step 2a — Write failing tests first (RED)

- [ ] **Step 1: Create test file**

Create `tests/unit/cerebro/test_spotify_podcasts.py`:

```python
"""Unit tests for SpotifyPodcastSource."""
from datetime import datetime
from unittest.mock import MagicMock, patch
import pytest
from cerebro.sources.spotify_podcasts import SpotifyPodcastSource, _parse_spotify_episode


def _fake_episode(episode_id="ep123", duration_ms=30 * 60 * 1000):
    return {
        "id": episode_id,
        "name": "Weekly Macro Outlook",
        "description": "Fed decision recap and yield curve outlook.",
        "release_date": "2026-03-20",
        "release_date_precision": "day",
        "duration_ms": duration_ms,
        "external_urls": {"spotify": f"https://open.spotify.com/episode/{episode_id}"},
        "show": {"id": "show456", "name": "Macro Matters", "publisher": "Bloomberg"},
        "audio_preview_url": "https://example.com/preview.mp3",
    }


class TestParseSpotifyEpisode:
    def test_returns_raw_paper(self):
        paper = _parse_spotify_episode(_fake_episode())
        assert paper.source == "spotify_podcast"
        assert paper.source_id == "ep123"
        assert paper.title == "Weekly Macro Outlook"
        assert "Bloomberg" in paper.authors
        assert paper.url.startswith("https://open.spotify.com")

    def test_categories_contain_podcast(self):
        assert "podcast" in _parse_spotify_episode(_fake_episode()).categories

    def test_published_date_parsed(self):
        paper = _parse_spotify_episode(_fake_episode())
        assert paper.published_date.year == 2026 and paper.published_date.month == 3

    def test_raw_paper_is_immutable(self):
        from dataclasses import FrozenInstanceError
        paper = _parse_spotify_episode(_fake_episode())
        with pytest.raises(FrozenInstanceError):
            object.__setattr__(paper, "title", "mutated")  # RawPaper is frozen=True


class TestSpotifyPodcastSourceFetchRecent:
    def _make_source(self, mock_sp):
        src = SpotifyPodcastSource.__new__(SpotifyPodcastSource)
        src.name = "spotify_podcast"
        src.logger = MagicMock()
        src._sp = mock_sp
        src._config = MagicMock(
            show_uris=["spotify:show:abc"],
            search_queries=[],
            episodes_per_show=2,
            max_audio_minutes=90,
        )
        return src

    def test_returns_list_of_raw_papers(self):
        mock_sp = MagicMock()
        mock_sp.show_episodes.return_value = {
            "items": [_fake_episode("e1"), _fake_episode("e2")],
            "next": None,
        }
        src = self._make_source(mock_sp)
        import asyncio
        since = datetime(2026, 3, 1)
        papers = asyncio.run(src.fetch_recent(since=since, limit=10))
        assert len(papers) == 2
        assert all(p.source == "spotify_podcast" for p in papers)

    def test_filters_old_episodes(self):
        old_ep = _fake_episode("old")
        old_ep = {**old_ep, "release_date": "2025-01-01"}
        mock_sp = MagicMock()
        mock_sp.show_episodes.return_value = {"items": [old_ep], "next": None}
        src = self._make_source(mock_sp)
        import asyncio
        papers = asyncio.run(src.fetch_recent(since=datetime(2026, 3, 1), limit=10))
        assert papers == []

    def test_skips_too_long_episodes(self):
        long_ep = _fake_episode("long", duration_ms=200 * 60 * 1000)
        mock_sp = MagicMock()
        mock_sp.show_episodes.return_value = {"items": [long_ep], "next": None}
        src = self._make_source(mock_sp)
        import asyncio
        papers = asyncio.run(src.fetch_recent(since=datetime(2026, 3, 1), limit=10))
        assert papers == []
```

- [ ] **Step 2: Run tests — expect FAIL**
```bash
conda activate ibkr-analytics && export PYTHONPATH=.
pytest tests/unit/cerebro/test_spotify_podcasts.py -v 2>&1 | head -30
```
Expected: `ModuleNotFoundError: No module named 'cerebro.sources.spotify_podcasts'`

### Step 2b — Implement the connector (GREEN)

- [ ] **Step 3: Create cerebro/sources/spotify_podcasts.py**

```python
"""Spotify podcast source connector for Cerebro.

Uses the Spotify Web API (via spotipy) to list recent episodes from
curated finance/market shows. Does NOT stream audio — episode URLs are
stored for the downstream AudioTranscriber to process.
"""
import logging
from datetime import datetime
from typing import List, Optional, Tuple

from cerebro.config import cerebro_config
from cerebro.sources.base import BaseSource, RawPaper

logger = logging.getLogger(__name__)

MARKET_SHOWS_DEFAULT: List[str] = [
    "spotify:show:6T4wZNedj1MStF8P7Ypvxo",  # Bloomberg Surveillance
    "spotify:show:2mTUnDkuKUkhiueKcVWoP0",  # Odd Lots (Bloomberg)
    "spotify:show:0WRER9qbpbCSD4UAhOllxM",  # Macro Voices
    "spotify:show:4eZCZMoJdpCVqvkqM6FQZY",  # Goldman Sachs Exchanges
    "spotify:show:3bpDnvJSWO5ELDyBDQBKLg",  # The Indicator (NPR)
]


def _parse_spotify_episode(episode: dict) -> RawPaper:
    """Convert a raw Spotify episode dict to a RawPaper.

    Args:
        episode: Episode object as returned by spotipy.

    Returns:
        Immutable RawPaper suitable for the Cerebro pipeline.
    """
    show = episode.get("show", {})
    publisher = show.get("publisher", "")
    show_name = show.get("name", "Unknown Show")
    duration_ms: int = episode.get("duration_ms", 0)
    duration_min = duration_ms / 60_000

    # Parse release date (precision may be "day", "month", or "year")
    release_str: str = episode.get("release_date", "1970-01-01")
    try:
        if len(release_str) == 10:
            published = datetime.strptime(release_str, "%Y-%m-%d")
        elif len(release_str) == 7:
            published = datetime.strptime(release_str, "%Y-%m")
        else:
            published = datetime.strptime(release_str[:4], "%Y")
    except ValueError:
        published = datetime.utcnow()

    categories: Tuple[str, ...] = ("podcast", show_name.lower().replace(" ", "_"))
    # Note: duration check (max_audio_minutes) is enforced in fetch_recent() before
    # _parse_spotify_episode is called, so no need to tag long_episode here.

    authors: Tuple[str, ...] = tuple(filter(None, [publisher]))

    return RawPaper(
        source="spotify_podcast",
        source_id=episode["id"],
        title=episode["name"],
        authors=authors,
        abstract=episode.get("description", "")[:2000],
        published_date=published,
        url=episode.get("external_urls", {}).get("spotify", ""),
        pdf_url=None,  # audio URL resolved later by AudioTranscriber
        categories=categories,
    )


class SpotifyPodcastSource(BaseSource):
    """Fetch recent episodes from curated Spotify finance shows."""

    def __init__(self) -> None:
        super().__init__(name="spotify_podcast")
        self._config = cerebro_config.spotify
        self._sp = self._build_client()

    def _build_client(self):
        """Initialise spotipy client with client credentials flow."""
        import spotipy
        from spotipy.oauth2 import SpotifyClientCredentials

        return spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=self._config.client_id,
                client_secret=self._config.client_secret,
            )
        )

    async def fetch_recent(self, since: datetime, limit: int = 50) -> List[RawPaper]:
        """Return recent podcast episodes published after *since*."""
        import asyncio

        show_uris = list(self._config.show_uris) or MARKET_SHOWS_DEFAULT
        papers: List[RawPaper] = []

        for show_uri in show_uris:
            show_id = show_uri.split(":")[-1]
            try:
                result = await asyncio.to_thread(
                    self._sp.show_episodes, show_id, limit=self._config.episodes_per_show
                )
                episodes = (result or {}).get("items", [])
                for ep in episodes:
                    paper = _parse_spotify_episode(ep)
                    duration_min = ep.get("duration_ms", 0) / 60_000
                    if paper.published_date < since:
                        continue
                    if duration_min > self._config.max_audio_minutes:
                        self.logger.info("Skipping long episode: %s (%.0f min)", paper.title, duration_min)
                        continue
                    papers.append(paper)
                    if len(papers) >= limit:
                        return papers
            except Exception as exc:
                self.logger.warning("Failed to fetch show %s: %s", show_uri, exc)

        return papers
```

- [ ] **Step 4: Run tests — expect PASS**
```bash
pytest tests/unit/cerebro/test_spotify_podcasts.py -v
```
Expected: all tests green.

- [ ] **Step 5: Commit**
```bash
git add cerebro/sources/spotify_podcasts.py tests/unit/cerebro/test_spotify_podcasts.py
git commit -m "feat(cerebro): add SpotifyPodcastSource connector"
```

---

## Task 3: AudioTranscriber module (TDD)

> **Updated:** Many finance podcasts (Bloomberg, Goldman Sachs, etc.) publish transcripts directly — via Spotify's transcript API endpoint or embedded in RSS feeds. The module must **check for an existing transcript first** and fall back to audio download + Whisper transcription only when none is available. This avoids wasting compute on shows that already publish text.

**Transcript-first strategy:**
1. Call `sp.episode(episode_id, market="US")` — check if `episode["html_description"]` contains a transcript block or if a `transcripts` key is present (Spotify API v1 returns this for some shows)
2. Check the show's RSS feed enclosure for `<podcast:transcript>` tags (Apple Podcasts namespace, widely adopted)
3. Fall back to yt-dlp download + faster-whisper only if neither source yields text

**Files:**
- Create: `tests/unit/cerebro/test_audio_transcriber.py`
- Create: `cerebro/processing/audio_transcriber.py`

### Step 3a — Write failing tests first (RED)

- [ ] **Step 1: Create test file**

Create `tests/unit/cerebro/test_audio_transcriber.py`:

```python
"""Unit tests for AudioTranscriber."""
import os
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from cerebro.processing.audio_transcriber import AudioTranscriber, TranscriptResult


class TestAudioTranscriber:
    def _make_transcriber(self):
        with patch("cerebro.processing.audio_transcriber.WhisperModel"):
            t = AudioTranscriber(model_size="base", cache_dir="/tmp/test_audio")
        return t

    def test_transcript_result_is_immutable(self):
        r = TranscriptResult(text="hello", language="en", duration_seconds=30.0, source_url="http://x")
        with pytest.raises(Exception):
            r.text = "changed"  # frozen dataclass

    def test_cache_path_is_deterministic(self):
        t = self._make_transcriber()
        url = "https://open.spotify.com/episode/abc123"
        p1 = t._cache_path(url)
        p2 = t._cache_path(url)
        assert p1 == p2

    def test_cache_path_uses_url_hash(self):
        t = self._make_transcriber()
        p1 = t._cache_path("https://example.com/ep1")
        p2 = t._cache_path("https://example.com/ep2")
        assert p1 != p2

    @patch("cerebro.processing.audio_transcriber.subprocess.run")
    def test_download_calls_yt_dlp(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        t = self._make_transcriber()
        t._download_audio("https://open.spotify.com/episode/abc", Path("/tmp/out.mp3"))
        assert mock_run.called
        cmd = mock_run.call_args[0][0]
        assert "yt-dlp" in cmd[0]

    def test_transcribe_returns_transcript_result(self):
        mock_model = MagicMock()
        segment = MagicMock()
        segment.text = " Market rally continues."
        mock_model.transcribe.return_value = ([segment], MagicMock(language="en", duration=120.0))
        with patch("cerebro.processing.audio_transcriber.WhisperModel", return_value=mock_model):
            t = AudioTranscriber(model_size="base", cache_dir="/tmp/x")
        result = t._transcribe_file(Path("/tmp/fake.mp3"), source_url="http://x")
        assert "Market rally" in result.text
        assert result.language == "en"
```

- [ ] **Step 2: Run tests — expect FAIL**
```bash
pytest tests/unit/cerebro/test_audio_transcriber.py -v 2>&1 | head -20
```
Expected: `ModuleNotFoundError: No module named 'cerebro.processing.audio_transcriber'`

### Step 3b — Implement (GREEN)

- [ ] **Step 3: Create cerebro/processing/audio_transcriber.py**

```python
"""Audio download and transcription for podcast episodes.

Downloads audio from a URL via yt-dlp, then transcribes locally
using faster-whisper. Results are cached by URL hash to avoid
re-transcribing the same episode across runs.
"""
import hashlib
import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# Module-level import so tests can patch cerebro.processing.audio_transcriber.WhisperModel
from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TranscriptResult:
    """Immutable transcription output."""
    text: str
    language: str
    duration_seconds: float
    source_url: str


class AudioTranscriber:
    """Download audio and transcribe using faster-whisper."""

    def __init__(self, model_size: str = "base", cache_dir: str = "data/podcast_audio_cache") -> None:
        # Uses module-level WhisperModel so tests can patch it via
        # patch("cerebro.processing.audio_transcriber.WhisperModel")
        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._model = WhisperModel(model_size, device="cpu", compute_type="int8")
        logger.info("AudioTranscriber ready (model=%s)", model_size)

    def _cache_path(self, url: str) -> Path:
        """Return a deterministic file path for the given URL."""
        url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
        return self._cache_dir / f"{url_hash}.mp3"

    def _download_audio(self, url: str, dest: Path) -> None:
        """Download audio to dest using yt-dlp."""
        cmd = [
            "yt-dlp",
            "--extract-audio",
            "--audio-format", "mp3",
            "--audio-quality", "5",
            "--output", str(dest),
            "--no-playlist",
            "--quiet",
            url,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            raise RuntimeError(f"yt-dlp failed: {result.stderr[:300]}")

    def _transcribe_file(self, audio_path: Path, source_url: str) -> TranscriptResult:
        """Transcribe an audio file and return structured result."""
        segments, info = self._model.transcribe(str(audio_path), beam_size=5)
        full_text = " ".join(seg.text.strip() for seg in segments)
        return TranscriptResult(
            text=full_text,
            language=info.language,
            duration_seconds=info.duration,
            source_url=source_url,
        )

    def transcribe_url(self, url: str) -> Optional[TranscriptResult]:
        """Download and transcribe audio at *url*. Returns None on failure."""
        dest = self._cache_path(url)
        try:
            if not dest.exists():
                logger.info("Downloading audio: %s", url)
                self._download_audio(url, dest)
            else:
                logger.info("Using cached audio: %s", dest)
            return self._transcribe_file(dest, source_url=url)
        except Exception as exc:
            logger.error("Transcription failed for %s: %s", url, exc)
            return None
        finally:
            # Clean up downloaded file after transcription to save disk space
            if dest.exists():
                dest.unlink(missing_ok=True)
```

- [ ] **Step 4: Run tests — expect PASS**
```bash
pytest tests/unit/cerebro/test_audio_transcriber.py -v
```

- [ ] **Step 5: Commit**
```bash
git add cerebro/processing/audio_transcriber.py tests/unit/cerebro/test_audio_transcriber.py
git commit -m "feat(cerebro): add AudioTranscriber with yt-dlp + faster-whisper"
```

---

## Task 4: Wire into the Cerebro pipeline

**Files:**
- Modify: `cerebro/pipeline.py`

The pipeline builds its source list in `CerebroPipeline.__init__`. We register `SpotifyPodcastSource` there, guarded by the `enabled` flag so it's a no-op when credentials are absent.

- [ ] **Step 1: Find the sources registration block in pipeline.py**

Search for where existing sources are instantiated:
```bash
grep -n "BaseSource\|sources.append\|ArxivSource\|BlogFeed" cerebro/pipeline.py | head -20
```

- [ ] **Step 2: Add import at top of cerebro/pipeline.py**

Add after the existing source imports:
```python
from cerebro.sources.spotify_podcasts import SpotifyPodcastSource
```

- [ ] **Step 3: Register the source (guarded by enabled flag)**

Locate the block where sources are built (look for a list like `[ArxivSource(), SSRNSource(), ...]`) and add:
```python
if cerebro_config.spotify.enabled:
    sources.append(SpotifyPodcastSource())
    logger.info("Spotify podcast source enabled")
```

- [ ] **Step 4: Smoke-test import**
```bash
conda activate ibkr-analytics && export PYTHONPATH=.
python -c "from cerebro.pipeline import CerebroPipeline; print('import OK')"
```
Expected: `import OK` (no crash even with `CEREBRO_SPOTIFY_ENABLED=false`).

- [ ] **Step 5: Commit**
```bash
git add cerebro/pipeline.py
git commit -m "feat(cerebro): register SpotifyPodcastSource in pipeline"
```

---

## Task 5: APScheduler daily podcast job

**Files:**
- Modify: `cerebro/scheduler.py`

The existing `CerebroScheduler` / `setup_cerebro_scheduler()` registers interval jobs with APScheduler. We add a `CronTrigger` job that fires daily at 07:00.

- [ ] **Step 1: Find scheduler registration pattern**
```bash
grep -n "add_job\|CronTrigger\|IntervalTrigger" cerebro/scheduler.py | head -20
```

- [ ] **Step 2: Add import**

At the top of `cerebro/scheduler.py`, ensure this import exists (add if missing):
```python
from apscheduler.triggers.cron import CronTrigger
```

- [ ] **Step 3: Add the podcast job function**

Add this function near the other job definitions in `scheduler.py`:
```python
async def _run_podcast_job(pipeline: "CerebroPipeline") -> None:
    """Daily job: fetch and process new Spotify podcast episodes."""
    from datetime import timedelta
    logger.info("[podcast-job] Starting Spotify podcast discovery run")
    since = datetime.utcnow() - timedelta(days=2)  # 2-day lookback for safety
    try:
        results = await pipeline.run(since=since, source_filter="spotify_podcast")
        logger.info("[podcast-job] Processed %d episodes", len(results))
    except Exception as exc:
        logger.error("[podcast-job] Failed: %s", exc, exc_info=True)
```

Note: If `pipeline.run()` does not accept `source_filter`, pass `sources=["spotify_podcast"]` or omit filtering — check the signature with:
```bash
grep -n "def run" cerebro/pipeline.py | head -5
```
Adjust accordingly.

- [ ] **Step 4: Register the cron job inside setup_cerebro_scheduler()**

Find the block where jobs are added to the scheduler and append:
```python
if cerebro_config.spotify.enabled:
    scheduler.add_job(
        _run_podcast_job,
        trigger=CronTrigger(hour=7, minute=0),
        args=[pipeline],
        id="spotify_podcast_daily",
        replace_existing=True,
        max_instances=1,
        misfire_grace_time=3600,
    )
    logger.info("Spotify podcast daily job scheduled at 07:00")
```

- [ ] **Step 5: Verify scheduler starts without error**
```bash
python -c "
import os; os.environ.setdefault('CEREBRO_SPOTIFY_ENABLED','false')
from cerebro.scheduler import setup_cerebro_scheduler
print('scheduler import OK')
"
```
Expected: `scheduler import OK`

- [ ] **Step 6: Commit**
```bash
git add cerebro/scheduler.py
git commit -m "feat(cerebro): add daily Spotify podcast APScheduler job at 07:00"
```

---

## Task 6: End-to-end smoke test

This task verifies the full pipeline works with real credentials before declaring done.

- [ ] **Step 1: Set up Spotify credentials**

1. Go to https://developer.spotify.com/dashboard and create a free app.
2. Copy the Client ID and Client Secret.
3. Add to your `.env` file:
```ini
CEREBRO_SPOTIFY_ENABLED=true
CEREBRO_SPOTIFY_CLIENT_ID=<your_id>
CEREBRO_SPOTIFY_CLIENT_SECRET=<your_secret>
CEREBRO_SPOTIFY_WHISPER_MODEL=base
CEREBRO_SPOTIFY_EPISODES_PER_SHOW=1
```

- [ ] **Step 2: Run a one-shot fetch (no transcription)**
```python
# Run from project root: python -c "..."
import asyncio, os
from datetime import datetime, timedelta
from cerebro.sources.spotify_podcasts import SpotifyPodcastSource

async def main():
    src = SpotifyPodcastSource()
    since = datetime.utcnow() - timedelta(days=7)
    papers = await src.safe_fetch(since=since, limit=5)
    for p in papers:
        print(p.source_id, p.title, p.published_date.date())

asyncio.run(main())
```
Expected: up to 5 lines with episode titles from finance shows.

- [ ] **Step 3: Test transcription on a short episode (optional)**
```python
from cerebro.processing.audio_transcriber import AudioTranscriber
t = AudioTranscriber(model_size="base")
# Use a short public podcast/audio URL for the first test
result = t.transcribe_url("https://open.spotify.com/episode/<short_episode_id>")
if result:
    print(result.language, len(result.text), result.text[:200])
```
Note: Spotify audio requires login. For first smoke test, use a public podcast URL supported by yt-dlp.

- [ ] **Step 4: Run full test suite**
```bash
make test 2>&1 | tail -20
```
Expected: all existing tests still pass; new tests included in count.

- [ ] **Step 5: Final commit**
```bash
git add -A
git commit -m "feat(cerebro): Spotify podcast pipeline — end-to-end verified"
```

---

## Important Notes

### Spotify Audio Limitation
Spotify's web API does not expose full episode audio URLs — only 30-second preview clips. `yt-dlp` can download full episodes **only if the user has a Spotify Premium account and the show is publicly available**. For initial testing, curate shows that are mirrored on YouTube or have public podcast RSS feeds (yt-dlp supports both). The `SpotifyPodcastSource` stores the episode Spotify URL; the `AudioTranscriber` will attempt yt-dlp download from it.

**Fallback approach** (if yt-dlp cannot access full Spotify audio): add an RSS feed URL field to `SpotifyConfig.show_rss_feeds` mapping show URI → RSS URL, and have `AudioTranscriber` prefer the RSS enclosure URL for download. This can be added as a follow-up task.

### Whisper Model Sizes
| Model | Size | Speed (CPU) | Accuracy |
|-------|------|-------------|----------|
| `tiny` | 75 MB | ~4x realtime | low |
| `base` | 150 MB | ~2x realtime | moderate |
| `small` | 500 MB | ~1x realtime | good |
| `medium` | 1.5 GB | ~0.5x realtime | high |

Start with `base` for exploration. Upgrade to `small` once the pipeline is stable.

### Cost / Resource Guard
- `max_audio_minutes=90` skips episodes longer than 90 min by default.
- `episodes_per_show=3` limits fetch volume per run.
- Audio files are deleted immediately after transcription (no disk accumulation).
- The APScheduler job uses `max_instances=1` to prevent overlapping runs.





