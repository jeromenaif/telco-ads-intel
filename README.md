# 🇧🇪 Belgian Telco · Meta Ads Intelligence

Competitive intelligence dashboard tracking Meta ad activity across 7 Belgian telecom brands.  
Data is refreshed automatically every day via GitHub Actions — colleagues just open the link.

---

## 🚀 Setup (one-time, ~10 minutes)

### 1. Create the GitHub repository

1. Go to [github.com/new](https://github.com/new)
2. Name it `telco-ads-intel` (or anything you like)
3. Set visibility to **Private** (recommended for competitive intel)
4. Click **Create repository**

### 2. Upload these files

Upload all files from this folder to the root of the repo:
- `index.html` — the dashboard
- `fetch_ads.py` — the data fetcher
- `.github/workflows/fetch.yml` — the daily scheduler
- `README.md` — this file

> **Tip:** Drag and drop directly on github.com, or use `git push`.

### 3. Store your Meta token as a secret

This is the key step — the token is stored encrypted in GitHub, never visible to anyone.

1. In your repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `META_TOKEN`
4. Value: your Meta API access token (from [developers.facebook.com/tools/accesstoken](https://developers.facebook.com/tools/accesstoken))
5. Click **Add secret**

> ⚠️ **Token expiry:** Meta user tokens expire after ~60 days.  
> When the Action fails, generate a new token and update the secret — takes 1 minute.

### 4. Run the first fetch manually

1. In your repo → **Actions** tab
2. Click **Fetch Meta Ads Data**
3. Click **Run workflow** → **Run workflow**
4. Wait ~2 minutes — it will create `data.json` in the repo

### 5. Enable GitHub Pages

1. In your repo → **Settings** → **Pages**
2. Source: **Deploy from a branch**
3. Branch: `main` / `root`
4. Click **Save**

Your dashboard will be live at:  
**`https://YOUR-ORG.github.io/telco-ads-intel/`**

Share this URL with colleagues — no login, no token, no proxy needed.

---

## 🔄 How it works

```
GitHub Actions (daily 8am Brussels time)
    ↓ runs fetch_ads.py with META_TOKEN secret
    ↓ calls Meta Ads Library API for 7 brands
    ↓ saves data.json to the repo
    ↓ GitHub Pages serves index.html + data.json
Colleagues open the URL → dashboard loads data.json
```

---

## 🛠 Customisation

| What | Where |
|---|---|
| Change refresh schedule | `.github/workflows/fetch.yml` → `cron:` line |
| Add/remove brands | `fetch_ads.py` → `BRANDS` list |
| Change date range | `fetch_ads.py` → `date_from` calculation |
| Update token | GitHub repo Settings → Secrets → `META_TOKEN` |

---

## 📋 Brands tracked

| Brand | Facebook Page ID |
|---|---|
| Proximus | 396653700450194 |
| Orange Belgium | 688456044627534 |
| Telenet | 21708711283 |
| Scarlet | 23927224422 |
| Mobile Vikings | 126215907404355 |
| Hey! | 106035051747489 |
| Digi Belgium | 146130408575824 |

---

*Built for Proximus Marketing Intelligence · EU DSA-compliant data only*
