# Minimal ABA Provider Scraper (BHCOE)

This Python script scrapes ABA therapy providers from BHCOE using their public XML sitemap and extracts:

- ✅ Clean company name (left of the first “–” if present)
- ✅ Website

It avoids:
- ❌ Duplicate websites
- ❌ Entries with missing websites

## 🚀 Setup

### 1. Create & activate a virtual environment (recommended)

```bash
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate      # macOS/Linux
```

### 2. Install requirements

```bash
pip install -r requirements.txt
```

### 3. Install Playwright browser (Chromium only)

```bash
playwright install chromium
```

## 🧪 Run the script

```bash
python camber_scraper.py --max 100 --out results.csv
```

Options:
- `--max`: Number of providers to scrape (default: 100)
- `--out`: Output CSV file name (default: `camber_scraper.csv`)

## 📁 Output columns

- `Company`
- `Website`
- `Expired`

## 🪵 Error handling

Errors are logged to `scrape_errors.log`.
