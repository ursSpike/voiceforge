# HOSTING — deploy both surfaces to GitHub Pages

Spike opens this when he needs the two public URLs to paste into the submission
form at **11:45 AM IST** (mid-checkpoint) and **2:00 PM IST** (final).

Both surfaces are static. There is **no live server** behind them. The platform
surface inlines its data at build time via `pipeline/build_platform.py` — the
`window.__PLATFORM__` global is baked into `out/platform/platform_data.js`.
On Pages, the in-page "refresh" of `/platform/live` will 404; this is expected
and falls back to the inlined data gracefully (see Debugging below).

## URLs (after first successful deploy)

- **Presentation (8 scenes):** https://ursSpike.github.io/voiceforge/
- **Operator workspace (eval surface):** https://ursSpike.github.io/voiceforge/platform/

> If the GitHub username on `origin` differs (`git remote -v`), substitute it.
> The repo path comes from `<user>.github.io/<repo>/`.

---

## Step 1 — turn on Pages with Actions as source

1. Open the repo on github.com: `https://github.com/ursSpike/voiceforge`.
2. Click **Settings** (top-right of the repo nav, NOT account settings).
3. Left sidebar → **Pages** (under "Code and automation").
4. Under **Build and deployment** → **Source** dropdown → choose
   **GitHub Actions**. (Do NOT choose "Deploy from a branch" — that would
   bypass our workflow and try to serve raw markdown.)
5. No need to click Save — the source change persists immediately.

You do not need to pick a branch, set a base path, or upload anything. The
workflow at `.github/workflows/pages.yml` handles assembly + upload + deploy.

## Step 2 — decide visibility (one-day call)

GitHub Pages on a **private** repo requires GitHub Enterprise Cloud.
This repo is currently private (per the batch3 privacy gate).

**Default recommendation: flip the repo public for the day.**

- Settings → scroll to bottom → **Danger Zone** → **Change repository
  visibility** → **Change to public** → type the repo name to confirm.
- The privacy considerations already documented in the batch3 plan
  (SPEC.md §1 surface text, `dpo_export` history in commit log) remain
  the only items to be aware of — nothing new is exposed by going public
  that isn't already in the artifacts you ship.
- After the submission window closes, flip back to private the same way.

**Alternative (keep private):** only viable if the org has GitHub Enterprise
Cloud with Pages-for-private-repos enabled. If unsure, take the public path
above — it is reversible in 30 seconds.

## Step 3 — push, watch, copy URLs

```bash
git push origin main
```

Then:

1. Repo → **Actions** tab.
2. The "Deploy VoiceForge surfaces to GitHub Pages" workflow appears at the
   top, running. Two jobs: `build` then `deploy`. Together ~45–90 seconds.
3. When both are green, click into the `deploy` job. The job summary shows
   the deployed URL — that is the **presentation** URL.
4. Append `/platform/` to get the operator URL.

If you need to re-deploy without changing code (e.g. rebuilt
`out/platform/platform_data.js` locally and committed it), the same workflow
also runs on **Run workflow** (workflow_dispatch) from the Actions tab.

---

## Submission text (paste-ready)

**Mid-checkpoint (11:45 AM IST):**

> Live operator workspace (the eval surface):
> https://ursSpike.github.io/voiceforge/platform/

**Final (2:00 PM IST):**

> Walkthrough / presentation: https://ursSpike.github.io/voiceforge/
>
> Live operator workspace (the eval surface):
> https://ursSpike.github.io/voiceforge/platform/

## Offline fallback (for judges who clone)

Both surfaces are also runnable offline from `out/surface/index.html` and
`out/dashboard.html` — for judges who clone the repo, no server required.

---

## Debugging cheat-sheet (4 lines)

- **404 on `/platform/live`** — expected on Pages; the platform reads inlined
  data from `window.__PLATFORM__` on first render. The "refresh" button fails
  silently, ignore it.
- **Blank page** — Settings → Pages → Source must be **GitHub Actions**, not
  "Deploy from a branch". Switching back resolves it.
- **404 at root** — verify the latest `deploy` action shows `_site/index.html`
  in the "Assemble _site/" step log. If `out/surface/index.html` was missing,
  the build fails loud — re-run `pipeline/build_surface.py` and re-push.
- **CORS errors** — none expected; the page is fully static with relative
  paths. If you see one, the symptom points at a leftover absolute URL —
  grep `out/surface out/platform` for `src="/"` or `href="/"`.
