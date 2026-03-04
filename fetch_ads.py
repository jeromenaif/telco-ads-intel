#!/usr/bin/env python3
"""
Belgian Telco · Meta Ads Library Fetcher
Runs as a GitHub Action — saves output to data.json
"""

import os, json, time, datetime, urllib.request, urllib.parse

TOKEN    = os.environ["META_TOKEN"]
VERSION  = "v20.0"
BASE_URL = f"https://graph.facebook.com/{VERSION}/ads_archive"

BRANDS = [
    {"id": "proximus",  "name": "Proximus",       "color": "#7B2D8B", "pageId": "396653700450194"},
    {"id": "orange",    "name": "Orange",          "color": "#FF6600", "pageId": "688456044627534"},
    {"id": "telenet",   "name": "Telenet",         "color": "#E30613", "pageId": "21708711283"},
    {"id": "hey",       "name": "Hey!",            "color": "#00C896", "pageId": "106035051747489"},
    {"id": "digi",      "name": "Digi",            "color": "#FFDD00", "pageId": "146130408575824"},
    {"id": "scarlet",   "name": "Scarlet",         "color": "#CC0000", "pageId": "23927224422"},
    {"id": "mvikings",  "name": "Mobile Vikings",  "color": "#1DA1F2", "pageId": "126215907404355"},
]

FIELDS = ",".join([
    "id", "ad_creation_time", "ad_delivery_start_time", "ad_delivery_stop_time",
    "ad_creative_bodies", "ad_creative_link_titles", "ad_creative_link_descriptions",
    "spend", "impressions", "eu_total_reach",
    "target_ages", "target_gender", "publisher_platforms",
    "languages", "ad_snapshot_url", "page_name", "beneficiary_payers"
])

# Fetch last 18 months
today     = datetime.date.today()
date_to   = today.strftime("%Y-%m-%d")
date_from = (today - datetime.timedelta(days=548)).strftime("%Y-%m-%d")  # ~18 months


def api_get(params):
    url = BASE_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "telco-intel/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def fetch_brand(brand):
    ads, cursor, page = [], None, 0
    while page < 4:
        params = {
            "access_token":      TOKEN,
            "ad_reached_countries": "BE",
            "ad_active_status":  "ALL",
            "search_page_ids":   brand["pageId"],
            "fields":            FIELDS,
            "limit":             "50",
            "ad_delivery_date_min": date_from,
            "ad_delivery_date_max": date_to,
        }
        if cursor:
            params["after"] = cursor
        data = api_get(params)
        ads.extend(data.get("data", []))
        cursor = data.get("paging", {}).get("cursors", {}).get("after")
        if not data.get("paging", {}).get("next"):
            break
        page += 1
        time.sleep(0.3)  # be gentle with the API
    return ads


def classify(body, title):
    text = f"{body} {title}".lower()
    promo_kw   = ["promo","offer","deal","discount","save","free","gratuit","solde",
                  "réduction","korting","gratis","actie","cashback","special","limited","tijdelijk"]
    product_kw = ["5g","fiber","fibre","gbps","mbps","internet","bbox","tv","play","plan",
                  "pack","subscription","abonnement","forfait","unlimited","illimité","onbeperkt",
                  "data","sim","esim","4g","smart","flex","boost","premium"]
    if any(k in text for k in promo_kw) or "%" in text:
        return "Promo"
    if any(k in text for k in product_kw):
        return "Product"
    return "Brand"


MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

def normalize(raw, brand):
    bodies  = raw.get("ad_creative_bodies") or []
    titles  = raw.get("ad_creative_link_titles") or []
    body    = bodies[0] if bodies else (titles[0] if titles else "")
    title   = titles[0] if titles else ""
    date_str = raw.get("ad_delivery_start_time") or raw.get("ad_creation_time") or ""
    try:
        d = datetime.datetime.fromisoformat(date_str.replace("Z",""))
    except Exception:
        d = datetime.datetime.now()
    stop = raw.get("ad_delivery_stop_time")
    active = not stop or datetime.datetime.fromisoformat(stop.replace("Z","")) > datetime.datetime.now()

    def parse_int(v): 
        try: return int(v)
        except: return 0

    spend  = raw.get("spend", {}) or {}
    impr   = raw.get("impressions", {}) or {}
    payers = raw.get("beneficiary_payers") or []

    return {
        "id":               str(raw.get("id","")),
        "brand":            brand["id"],
        "brandName":        brand["name"],
        "brandColor":       brand["color"],
        "month":            d.month - 1,
        "monthLabel":       MONTHS[d.month - 1],
        "year":             d.year,
        "type":             classify(body, title),
        "title":            (body or title)[:200] or "(no copy)",
        "spend_lower":      parse_int(spend.get("lower_bound", 0)),
        "spend_upper":      parse_int(spend.get("upper_bound", 0)),
        "impressions_lower":parse_int(impr.get("lower_bound", 0)),
        "impressions_upper":parse_int(impr.get("upper_bound", 0)),
        "eu_total_reach":   raw.get("eu_total_reach", 0),
        "platforms":        raw.get("publisher_platforms") or [],
        "targeting": {
            "age":       ", ".join(raw.get("target_ages") or ["18-65+"]),
            "gender":    raw.get("target_gender") or "All",
            "interests": [p["name"] for p in payers if p.get("name")][:3],
        },
        "languages":        raw.get("languages") or [],
        "status":           "ACTIVE" if active else "INACTIVE",
        "start_date":       date_str[:10],
        "snapshot_url":     raw.get("ad_snapshot_url"),
        "source":           "live",
    }


def main():
    all_ads = []
    for brand in BRANDS:
        print(f"  → Fetching {brand['name']}...", flush=True)
        try:
            raws = fetch_brand(brand)
            ads  = [normalize(r, brand) for r in raws]
            all_ads.extend(ads)
            print(f"    ✓ {len(ads)} ads", flush=True)
        except Exception as e:
            print(f"    ✗ Error: {e}", flush=True)

    output = {
        "fetched_at":  datetime.datetime.utcnow().isoformat() + "Z",
        "date_from":   date_from,
        "date_to":     date_to,
        "total":       len(all_ads),
        "ads":         all_ads,
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, separators=(",", ":"))

    print(f"\n✅ Saved {len(all_ads)} ads to data.json", flush=True)


if __name__ == "__main__":
    main()
