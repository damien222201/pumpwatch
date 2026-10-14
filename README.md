# PumpWatch

A community-reported fuel price tracker for Nigeria. No official source publishes real-time, station-level pump prices, so PumpWatch is crowdsourced: people report what they paid for petrol (PMS) or diesel (AGO), and anyone can look up recent prices for their state or see which states are cheapest right now.

## Why

Fuel prices in Nigeria can vary a lot between stations and states, and change with little warning. PumpWatch turns "what's fuel going for right now" from a round of phone calls into a quick lookup — and builds a running picture of where prices are lowest.

## Features

- **Report a price** — state, station name/area, fuel type (PMS or AGO), price per litre, optional note. Email required (not shown publicly) to cut spam, with rate limiting (max 5 reports/hour per email or IP). Prices outside a sane ₦50–₦5000/litre range are rejected as likely typos.
- **Find cheapest** — browse recent reports for a state, sorted cheapest first. Reports older than 24h are flagged as possibly outdated (prices move slower than power status, so the staleness window is longer than LightWatch's).
- **Prices by state** — average reported price per state over the last 7 or 30 days, ranked cheapest to priciest, plus a national average.
- **JSON API** (`/api/reports`) — last 72 hours of reports, for future use (e.g. a map view).

## Tech stack

Same stack as [LightWatch](../lightwatch) for consistency: Flask + Flask-SQLAlchemy, PostgreSQL on Render, server-rendered Jinja2 templates, no JS framework.

## Running locally

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
export $(cat .env | xargs)

python app.py
```

Falls back to a local SQLite file (`pumpwatch_dev.db`) if `DATABASE_URL` isn't set. Visit `http://localhost:5000`.

## Deploying to Render

**Option A — blueprint:** push to GitHub, then "New Blueprint" in Render pointed at the repo — `render.yaml` sets up the web service and a free Postgres database together.

**Option B — manual:**
1. Create a Postgres database on Render (free tier).
2. Create a Web Service from this repo — build command `pip install -r requirements.txt`, start command `gunicorn app:app`.
3. Add env vars: `DATABASE_URL` (from your Postgres instance) and `SECRET_KEY` (any random string).

`app.py` automatically rewrites Render's `postgres://` URLs to `postgresql://` for SQLAlchemy.

## Project structure

```
app.py              # routes + app factory
models.py           # PriceReport model
reference_data.py   # Nigeria's 36 states + FCT, and tracked fuel types
utils.py            # email validation, rate limiting, price stats
templates/           # index, prices, stats pages + shared base layout
static/style.css     # all styling
```

## Known limitations / next steps

- **PMS and AGO only** — kerosene (DPK) and cooking gas (LPG) aren't tracked yet. LPG is priced per kg rather than per litre, so adding it means extending the schema with a unit field rather than just adding another fuel-type option.
- **No email verification** — same tradeoff as LightWatch: email cuts casual spam without adding a verification-link flow.
- **No map view yet** — `/api/reports` exists specifically so one can be added later.
- **Station name matching is free text** — "NNPC Mega Station, Opebi Rd" and "NNPC Opebi" are treated as different entries. Fine for browsing recent reports; would need normalization for station-level price history over time.

## License

MIT — see [LICENSE](LICENSE).
