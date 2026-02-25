#!/usr/bin/env python3
"""Publish generated wiki pages to GitHub Wiki repo (<repo>.wiki.git)."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
EXPORT_SCRIPT = REPO_ROOT / "export_github_wiki.py"
DEFAULT_WIKI_URL = "https://github.com/lovemonkeyz/LovemonkeyGuides.wiki.git"
DEFAULT_WIKI_DIR = Path("/tmp/LovemonkeyGuides.wiki")
DEFAULT_SOURCE_DIR = REPO_ROOT / "wiki"


def run(cmd: list[str], cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=True)


def detect_default_branch(wiki_dir: Path) -> str:
    try:
        out = subprocess.check_output(
            ["git", "symbolic-ref", "refs/remotes/origin/HEAD"],
            cwd=str(wiki_dir),
            text=True,
        ).strip()
        return out.rsplit("/", 1)[-1]
    except Exception:
        return "master"


def ensure_wiki_repo(wiki_url: str, wiki_dir: Path) -> str:
    if (wiki_dir / ".git").exists():
        run(["git", "fetch", "origin"], cwd=wiki_dir)
        branch = detect_default_branch(wiki_dir)
        run(["git", "checkout", branch], cwd=wiki_dir)
        run(["git", "pull", "--ff-only", "origin", branch], cwd=wiki_dir)
        return branch

    if wiki_dir.exists():
        shutil.rmtree(wiki_dir)
    try:
        run(["git", "clone", wiki_url, str(wiki_dir)])
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            "Failed to clone wiki repo. Common causes:\\n"
            "1) Wiki is disabled or not initialized (create first wiki page in GitHub UI).\\n"
            "2) Repository is private and your auth token/SSH key lacks access.\\n"
            "3) Wiki URL is wrong. Expected format: https://github.com/<owner>/<repo>.wiki.git\\n"
            "After fixing that, rerun publish_github_wiki.py."
        ) from exc
    return detect_default_branch(wiki_dir)


def clean_and_copy(source_dir: Path, wiki_dir: Path) -> None:
    for item in wiki_dir.iterdir():
        if item.name == ".git":
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    for src in sorted(source_dir.glob("*.md")):
        shutil.copy2(src, wiki_dir / src.name)


def commit_and_push(wiki_dir: Path, message: str, branch: str) -> None:
    run(["git", "add", "."], cwd=wiki_dir)

    diff = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=str(wiki_dir),
    )
    if diff.returncode == 0:
        print("No wiki changes to commit.")
        return

    run(["git", "commit", "-m", message], cwd=wiki_dir)
    run(["git", "push", "origin", branch], cwd=wiki_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish generated markdown pages to GitHub Wiki")
    parser.add_argument(
        "--wiki-url",
        default=DEFAULT_WIKI_URL,
        help="Wiki git URL, e.g. https://github.com/<owner>/<repo>.wiki.git",
    )
    parser.add_argument(
        "--wiki-dir",
        type=Path,
        default=DEFAULT_WIKI_DIR,
        help="Local checkout path for the wiki repo",
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=DEFAULT_SOURCE_DIR,
        help="Directory containing generated .md wiki pages",
    )
    parser.add_argument(
        "--skip-export",
        action="store_true",
        help="Skip running export_github_wiki.py before publish",
    )

    args = parser.parse_args()

    source_dir = args.source_dir.resolve()

    if not args.skip_export:
        run(["python3", str(EXPORT_SCRIPT), "--output-dir", str(source_dir)])
    elif not source_dir.exists():
        raise FileNotFoundError(f"Source wiki pages not found: {source_dir}")

    branch = ensure_wiki_repo(args.wiki_url, args.wiki_dir)
    clean_and_copy(source_dir, args.wiki_dir)

    commit_msg = f"Update wiki backup ({datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')})"
    commit_and_push(args.wiki_dir, commit_msg, branch)


if __name__ == "__main__":
    main()
