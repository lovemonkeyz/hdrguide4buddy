#!/usr/bin/env python3
"""Export GitHub Wiki markdown pages from recommendations data."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TOP_SINGLE = [
    "red-dead-redemption-2",
    "cyberpunk-2077",
    "mad-max",
    "god-of-war",
    "star-wars-jedi-fallen-order",
]

TOP_COOP = [
    "split-fiction",
    "dying-light",
    "dying-light-2-stay-human",
    "the-forest",
    "world-war-z-aftermath",
]

MORE_SINGLE = [
    "dishonored",
    "god-of-war",
    "god-of-war-ragnar-k",
    "mad-max",
    "star-wars-jedi-survivor",
    "hogwarts-legacy",
    "tomb-raider",
    "rise-of-the-tomb-raider",
    "shadow-of-the-tomb-raider",
    "bioshock-remastered",
    "bioshock-2-remastered",
    "bioshock-infinite",
    "spider-man-remastered",
    "ghost-of-tsushima-director-s-cut",
]

MORE_COOP = [
    "dead-island-2",
    "rust-console-edition",
    "warhammer-40-000-darktide",
    "helldivers-2",
    "no-man-s-sky",
    "deep-rock-galactic",
    "destiny-2",
]

CHALLENGE = [
    "elden-ring",
    "dark-souls-iii",
    "bloodborne",
    "dark-souls-remastered",
    "warhammer-40-000-space-marine-2",
    "sekiro-shadows-die-twice",
    "nioh",
    "clair-obscur-expedition-33",
    "lies-of-p",
]

FREDRIC_TOP10 = [
    "clair-obscur-expedition-33",
    "baldur-s-gate-3",
    "the-witcher-3-the-wild-hunt",
    "red-dead-redemption-2",
    "cyberpunk-2077",
    "god-of-war-ragnar-k",
    "mass-effect-legendary-edition",
    "bioshock-2-remastered",
    "bioshock-remastered",
    "horizon-zero-dawn-remastered",
]

CASUAL_SILLY = [
    "high-on-life",
    "saints-row-the-third-remastered",
    "saints-row-iv-re-elected",
    "saints-row-gat-out-of-hell",
    "ratchet-clank-rift-apart",
]

ID_ALIASES = {
    "spider-man-remastered": ["spider-man"],
}


def format_tag(value: str) -> str:
    return " ".join(part.capitalize() for part in str(value).replace("_", "-").split("-"))


def has_coop(game: dict[str, Any]) -> bool:
    play_modes = str(game.get("play_modes", "")).lower()
    return bool(game.get("dual_mode") or game.get("section") == "coop" or "co-op ✅" in play_modes)


def resolve_mode_label(game: dict[str, Any]) -> str:
    if has_coop(game) and (game.get("dual_mode") or game.get("section") == "single_player"):
        return "Solo + Co-Op"
    if has_coop(game):
        return "Co-Op Focused"
    return "Solo Focused"


def primary_label(game: dict[str, Any]) -> str:
    return "Co-Op / Hybrid" if has_coop(game) else "Single Player Only"


def score(value: Any, max_score: int | float) -> str:
    if value is None:
        return "N/A"
    return f"{value}/{max_score}"


def bool_label(value: bool) -> str:
    return "Yes" if value else "No"


def game_block(game: dict[str, Any], rank: int | None = None) -> str:
    title = game["title"]
    heading = f"### {rank}) {title}" if rank is not None else f"### {title}"
    ratings = game["ratings"]
    lines = [
        heading,
        "",
        f"⭐ **PS5 Store:** {score(ratings.get('ps_store'), 5)} | **Critics:** {score(ratings.get('critics'), 100)} | **Community:** {score(ratings.get('community'), 10)}",
        "",
        (
            "**Primary:** "
            f"{primary_label(game)} | "
            f"**Mode:** {resolve_mode_label(game)} | "
            f"**Viewpoint:** {format_tag(game.get('tags', {}).get('viewpoint', 'third-person'))} | "
            f"**Difficulty:** {format_tag(game.get('tags', {}).get('difficulty', 'medium'))} | "
            f"**Adjustable Difficulty:** {bool_label(bool(game.get('tags', {}).get('adjustable_difficulty')))}"
        ),
        "",
        f"**Theme:** {game.get('theme', '')}",
        "",
        f"**Story:** {game.get('story', '')}",
        "",
        f"**Gameplay:** {game.get('gameplay', '')}",
        "",
        f"**Genres:** {', '.join(game.get('genres', []))}",
        "",
        f"[Open PlayStation Store]({game.get('ps_store_url', '')})",
        "",
        "---",
        "",
    ]
    return "\n".join(lines)


def resolve_id(game_id: str, by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
    if game_id in by_id:
        return by_id[game_id]
    for alias in ID_ALIASES.get(game_id, []):
        if alias in by_id:
            return by_id[alias]
    raise KeyError(f"Game id not found in dataset: {game_id}")


def render_list(ids: list[str], by_id: dict[str, dict[str, Any]], ranked: bool = False) -> str:
    blocks = []
    for idx, gid in enumerate(ids, start=1):
        blocks.append(game_block(resolve_id(gid, by_id), rank=idx if ranked else None))
    return "".join(blocks)


def page_home(total_games: int) -> str:
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"""# Game Recommendations Wiki

Static backup of the recommendation web app, formatted for GitHub Wiki.

- Generated: **{generated}**
- Total games in catalog: **{total_games}**

## Pages

- [Top Picks For You](Top-Picks-For-You)
- [More Recommendations](More-Recommendations)
- [Challenge Yourself](Challenge-Yourself)
- [Fredric's Top 10 List](Fredrics-Top-10-List)
- [Casual/Silly](Casual-Silly)
- [All Games Index](All-Games-Index)

## Notes

- The wiki version is intentionally static.
- Interactive features from the web app (filters, save state) are not available in GitHub Wiki.
"""


def page_top_picks(by_id: dict[str, dict[str, Any]]) -> str:
    return (
        "# Top Picks For You\n\n"
        "## Single Player Only\n\n"
        + render_list(TOP_SINGLE, by_id, ranked=True)
        + "## Co-Op / Hybrid\n\n"
        + "Some games in this section are fully enjoyable solo too, but co-op makes them even better.\n\n"
        + render_list(TOP_COOP, by_id, ranked=True)
    )


def page_more_recommendations(by_id: dict[str, dict[str, Any]]) -> str:
    return (
        "# More Recommendations\n\n"
        "## Single Player Only\n\n"
        + render_list(MORE_SINGLE, by_id, ranked=False)
        + "## Co-Op / Hybrid\n\n"
        + "Some games in this section are fully enjoyable solo too, but co-op makes them even better.\n\n"
        + render_list(MORE_COOP, by_id, ranked=False)
    )


def page_challenge(by_id: dict[str, dict[str, Any]]) -> str:
    return (
        "# Challenge Yourself\n\n"
        "> Hard games but extremely rewarding.\n\n"
        + render_list(CHALLENGE, by_id, ranked=True)
    )


def page_fredric_top10(by_id: dict[str, dict[str, Any]]) -> str:
    return (
        "# Fredric's Top 10 List\n\n"
        "> Some of these games are not on any of the other lists, but I strongly recommend all of them.\n\n"
        + render_list(FREDRIC_TOP10, by_id, ranked=True)
    )


def page_casual_silly(by_id: dict[str, dict[str, Any]]) -> str:
    return "# Casual/Silly\n\n" + render_list(CASUAL_SILLY, by_id, ranked=False)


def page_all_games_index(games: list[dict[str, Any]]) -> str:
    rows = []
    for g in sorted(games, key=lambda x: x["title"].lower()):
        rows.append(
            "| "
            + " | ".join(
                [
                    g["title"],
                    primary_label(g),
                    "Yes" if has_coop(g) else "No",
                    format_tag(g.get("tags", {}).get("viewpoint", "third-person")),
                    format_tag(g.get("tags", {}).get("difficulty", "medium")),
                    format_tag(g.get("tags", {}).get("mood", "mixed")),
                    format_tag(g.get("tags", {}).get("pace", "mixed")),
                    f"[Store]({g.get('ps_store_url', '')})",
                ]
            )
            + " |"
        )

    return (
        "# All Games Index\n\n"
        "Use browser search (`Ctrl+F`) in this page to find specific titles/tags.\n\n"
        "| Title | Primary | Co-Op | Viewpoint | Difficulty | Mood | Pace | Link |\n"
        "|---|---|---|---|---|---|---|---|\n"
        + "\n".join(rows)
        + "\n"
    )


def page_sidebar() -> str:
    return """## Navigation

- [Home](Home)
- [Top Picks For You](Top-Picks-For-You)
- [More Recommendations](More-Recommendations)
- [Challenge Yourself](Challenge-Yourself)
- [Fredric's Top 10 List](Fredrics-Top-10-List)
- [Casual/Silly](Casual-Silly)
- [All Games Index](All-Games-Index)
"""


def write_page(output_dir: Path, filename: str, content: str) -> None:
    path = output_dir / filename
    path.write_text(content.strip() + "\n", encoding="utf-8")


def export_wiki(input_json: Path, output_dir: Path) -> None:
    data = json.loads(input_json.read_text(encoding="utf-8"))
    games: list[dict[str, Any]] = data["games"]
    by_id = {g["id"]: g for g in games}

    output_dir.mkdir(parents=True, exist_ok=True)

    write_page(output_dir, "Home.md", page_home(len(games)))
    write_page(output_dir, "Top-Picks-For-You.md", page_top_picks(by_id))
    write_page(output_dir, "More-Recommendations.md", page_more_recommendations(by_id))
    write_page(output_dir, "Challenge-Yourself.md", page_challenge(by_id))
    write_page(output_dir, "Fredrics-Top-10-List.md", page_fredric_top10(by_id))
    write_page(output_dir, "Casual-Silly.md", page_casual_silly(by_id))
    write_page(output_dir, "All-Games-Index.md", page_all_games_index(games))
    write_page(output_dir, "_Sidebar.md", page_sidebar())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export static GitHub Wiki pages from recommendations JSON")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("web/local/data/recommendations.json"),
        help="Path to recommendations.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("wiki"),
        help="Directory to write wiki markdown pages",
    )

    args = parser.parse_args()
    if not args.input.exists():
        raise FileNotFoundError(f"Input JSON not found: {args.input}")

    export_wiki(args.input, args.output_dir)
    print(f"Wrote wiki pages to: {args.output_dir}")
