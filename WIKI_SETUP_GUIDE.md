# GitHub Wiki Setup Guide

This guide sets up your repo wiki as a static backup of the web app.

## 1) Generate Wiki Pages From Current Data

Run from repo root:

```bash
python3 export_github_wiki.py
```

This writes pages into:

- `wiki/Home.md`
- `wiki/Top-Picks-For-You.md`
- `wiki/More-Recommendations.md`
- `wiki/Challenge-Yourself.md`
- `wiki/Fredrics-Top-10-List.md`
- `wiki/Casual-Silly.md`
- `wiki/All-Games-Index.md`
- `wiki/_Sidebar.md`

## 2) Enable Wiki In GitHub

1. Open your repository on GitHub.
2. Go to **Settings -> Features**.
3. Make sure **Wikis** is enabled.
4. Open the **Wiki** tab once (GitHub initializes the wiki repository).

## 3) Publish Pages (Preferred: Git)

GitHub wikis are a separate Git repo (`<repo>.wiki.git`).

### Clone wiki repo

```bash
git clone https://github.com/<OWNER>/<REPO>.wiki.git /tmp/<REPO>.wiki
```

If this returns `Repository not found`:
1. Open `https://github.com/<OWNER>/<REPO>/wiki` in browser.
2. If prompted, enable wiki and create the first page (`Home`).
3. For private repos, ensure auth has write access (PAT/SSH).

### Copy generated pages

```bash
cp wiki/*.md /tmp/<REPO>.wiki/
```

### Commit + push wiki pages

```bash
cd /tmp/<REPO>.wiki
git add .
git commit -m "Update wiki backup from recommendations export"
git push
```

## 3b) One-Command Publish (Recommended)

From repo root:

```bash
python3 publish_github_wiki.py
```

If you're currently in another folder (for example `web/local`), run:

```bash
python3 /mnt/c/gitrepo/LovemonkeyGuides/publish_github_wiki.py --wiki-url https://github.com/lovemonkeyz/LovemonkeyGuides.wiki.git
```

This will:
1. Regenerate files in `wiki/`
2. Clone/pull `<repo>.wiki.git` into `/tmp/LovemonkeyGuides.wiki`
3. Copy wiki pages into that repo
4. Commit and push to GitHub Wiki

If your repo is private and HTTPS auth is flaky in WSL, use SSH URL:

```bash
python3 publish_github_wiki.py --wiki-url git@github.com:<OWNER>/<REPO>.wiki.git
```

## 4) Alternative: Manual Copy/Paste

If you do not want to use wiki git:

1. Open each file in `wiki/`.
2. Create corresponding wiki pages in GitHub web UI.
3. Paste content and save.

## 5) Refresh Workflow (Whenever Rankings/Content Change)

```bash
python3 web/app/scripts/build_recommendations_json.py --input NephewGamingRecommendations.md --output web/local/data/recommendations.json
python3 export_github_wiki.py
```

Then repeat Step 3 to republish wiki pages.

## Notes

- Wiki backup is static markdown; interactive web features (filters, hidden state, local save) are not available.
- Current structure and limits are documented in `GITHUB_WIKI_BACKUP_PLAN.md`.
