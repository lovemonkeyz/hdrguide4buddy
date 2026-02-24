# GitHub Wiki Backup Plan

## Goal
Create a static fallback version of the recommendation project that works in a GitHub Wiki using Markdown only.

## What Works In GitHub Wiki
- Headings and anchor links (table of contents style navigation).
- Markdown tables.
- Images (from repo paths or external URLs).
- Internal links between wiki pages.
- Collapsible sections via `<details><summary>...</summary>...</details>` (HTML in Markdown).

## What Does Not Work
- Custom JavaScript logic (filter buttons, local save/hidden state, dynamic sorting).
- App-style interactivity with per-user state persistence.
- Rich SPA tab behavior from `web/local/app.js`.

## Recommended Wiki Structure
- `Home`
  - Quick intro and links to each page.
- `Top-Picks-For-You`
  - Split into `Single Player Only` and `Co-Op / Hybrid`.
- `More-Recommendations`
  - Same split.
- `Challenge-Yourself`
  - Ranked list with short explanations.
- `Fredrics-Top-10-List`
  - Ranked unified list with co-op/hybrid labels.
- `Casual-Silly`
  - Unified list.
- `All-Games-Index`
  - Master table with tags (`Mood`, `Pace`, `Difficulty`, `Viewpoint`, `Co-Op`).

## Markdown Pattern For Each Game
Use a repeatable compact card pattern:

```md
### 1) Red Dead Redemption 2
⭐ **PS5 Store:** 4.75/5 | **Critics:** 97/100 | **Community:** 9.0/10  
**Mode:** Single Player Only | **Viewpoint:** Third-Person | **Difficulty:** Medium  
**Theme:** ...  
**Story:** ...  
**Gameplay:** ...  
[Open PlayStation Store](https://store.playstation.com/...)
```

## Practical Workflow
1. Keep the web app as primary version.
2. Keep wiki pages as static fallback snapshot.
3. Regenerate/update wiki pages only when major ranking/content changes happen.
4. Use one source of truth for text (`NephewGamingRecommendations.md` + `recommendations.json`) to avoid drift.

## Suggested Next Automation (Optional)
- Add a script to export curated tabs from `web/local/data/recommendations.json` into wiki-ready Markdown files.
- Commit/export those pages into a `.wiki` repo when needed.
