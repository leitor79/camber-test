import requests
import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import time
import random
import argparse
from datetime import datetime

DEFAULT_MAX_ARTICLES = 100
DEFAULT_OUTPUT_FILE = "camber_scraper.csv"
ERROR_LOG_FILE = "scrape_errors.log"
SITEMAP_URL = "https://www.bhcoe.org/aba-therapy-sitemap1.xml"

# Extract URLs to scrape from the sitemap XML file.
def extract_urls_from_sitemap(xml_url, max_urls):
    response = requests.get(xml_url)
    soup = BeautifulSoup(response.content, "xml")
    url_tags = soup.find_all("url")
    urls = []
    for tag in url_tags:
        loc_tag = tag.find("loc")
        if loc_tag and loc_tag.text.strip().startswith("https://www.bhcoe.org/aba-therapy/"):
            urls.append(loc_tag.text.strip())
            if len(urls) >= max_urls:
                break
    return urls

# Scrape data from the provided URLs using Playwright.  
def scrape_from_urls(url_list):
    scraped_data = []
    seen_websites = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(user_agent="Mozilla/5.0 (compatible; ABAResearchBot/1.0)")

        for idx, url in enumerate(url_list):
            try:
                page = context.new_page()
                print(f"🔎 [{idx+1}/{len(url_list)}] Fetching: {url}")
                page.goto(url)
                page.wait_for_timeout(random.uniform(1000, 2000))

                try:
                    website = page.locator(".et_pb_blurb_1_tb_body a").first.inner_text().strip()
                except:
                    website = ""

                if not website:
                    print("⏭️ Skipping entry with missing website.")
                    page.close()
                    continue

                if website in seen_websites:
                    print(f"⏭️ Skipping duplicate website: {website}")
                    page.close()
                    continue

                try:
                    company = page.locator("div.et_pb_text_inner h1").first.inner_text().strip()
                except:
                    company = ""

                try:
                    expired_text = page.locator("h5").first.inner_text().strip()
                    expired = 1 if expired_text.lower().startswith("accreditation expired") else 0
                except:
                    expired = 0

                clean_name = company.split("–")[0].strip() if "–" in company else company.strip()

                scraped_data.append({
                    "Company": clean_name,
                    "Website": website,
                    "Expired": expired
                })

                seen_websites.add(website)

                page.close()
                time.sleep(random.uniform(0.5, 1.2))

            except Exception as e:
                with open(ERROR_LOG_FILE, "a") as log:
                    log.write(f"[{datetime.now()}] Error on URL {url}: {str(e)}\n")
                print(f"⚠️ Error scraping {url}: {e}")
        browser.close()
    return scraped_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape BHCOE ABA provider pages to a CSV output file.")
    parser.add_argument("--max", type=int, default=DEFAULT_MAX_ARTICLES, help="Maximum number of providers to scrape.")
    parser.add_argument("--out", type=str, default=DEFAULT_OUTPUT_FILE, help="Output CSV file name.")

    args = parser.parse_args()

    print(f"📥 Reading URLs from sitemap: {SITEMAP_URL}")
    urls = extract_urls_from_sitemap(SITEMAP_URL, args.max)

    print(f"🔗 Retrieved {len(urls)} URLs from sitemap.")
    scraped_data = scrape_from_urls(urls)

    if scraped_data:
        df = pd.DataFrame(scraped_data)
        df.to_csv(args.out, index=False)
        print(f"✅ Exported {len(df)} records to '{args.out}'")
        print(df.head())
    else:
        print("⚠️ No data was scraped.")
