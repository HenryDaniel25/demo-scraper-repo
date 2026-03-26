#!/usr/bin/env python3
"""
CareLink Transmissions Scraper - Production Ready Version
"""

import argparse
import base64
import csv
import logging
import os
import re
import time
from pathlib import Path
from typing import Dict, List, Set

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

import db as portal_db

# --------------------------------------------------
# ENV + CONFIG
# --------------------------------------------------

load_dotenv()

LOGIN_URL = os.getenv("CARELINK_LOGIN_URL")
HOME_URL = os.getenv("CARELINK_HOME_URL")
TRANSMISSION_LIST_URL = os.getenv("CARELINK_TRANSMISSION_LIST_URL")

if not all([LOGIN_URL, HOME_URL, TRANSMISSION_LIST_URL]):
    raise ValueError("Missing CareLink URLs in .env")

PDF_OUTPUT_DIR = "output/carelink/pdfs"
OUTPUT_CSV = "output/carelink/carelink_transmissions.csv"

# --------------------------------------------------
# LOGGING
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def normalize_text(value: str) -> str:
    return " ".join(str(value).strip().lower().split())


def patient_id_variants(value: str) -> Set[str]:
    normalized = normalize_text(value)
    if not normalized:
        return set()

    variants = {normalized}
    variants.add(normalized.replace(" ", ""))

    first = normalized.split(" ")[0]
    if first:
        variants.add(first)

    digits = re.sub(r"\D+", "", normalized)
    if digits:
        variants.add(digits)

    return variants


def retry(max_attempts=3, delay=2):
    def wrapper(func):
        def inner(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    logger.warning(f"Retry {attempt+1}/{max_attempts} failed: {e}")
                    time.sleep(delay * (attempt + 1))
        return inner
    return wrapper


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

def login(playwright, user_id, password, headless):
    logger.info("Logging in...")

    browser = playwright.chromium.launch(
        headless=headless,
        args=[
            "--no-sandbox",
            "--disable-dev-shm-usage"
        ]
    )

    context = browser.new_context()
    page = context.new_page()

    page.set_default_timeout(60000)

    page.goto(LOGIN_URL)
    page.get_by_role("textbox", name="User ID").fill(user_id)
    page.get_by_role("textbox", name="Password").fill(password)
    page.get_by_role("button", name="Sign In").click()

    page.wait_for_url("**/home**")

    return browser, context, page


# --------------------------------------------------
# SCRAPE TABLE
# --------------------------------------------------

def scrape_current_page(page, allowed_patient_ids):
    page.wait_for_selector("table tbody tr")

    rows_data = page.evaluate("""
        () => {
            const clean = v => (v || '').trim();

            const rows = document.querySelectorAll('table tbody tr');

            return Array.from(rows).map((row, idx) => {
                const cells = row.querySelectorAll('td');

                return {
                    rowIndex: idx,
                    text: row.innerText,
                };
            });
        }
    """)

    matched = []

    for row in rows_data:
        text = row["text"]
        variants = patient_id_variants(text)

        if variants & allowed_patient_ids:
            matched.append(row)

    return matched


# --------------------------------------------------
# PDF DOWNLOAD
# --------------------------------------------------

@retry()
def download_pdf(page, context, row_idx, clinic_id):
    rows = page.locator("table tbody tr")

    if row_idx >= rows.count():
        return False

    row = rows.nth(row_idx)

    # select checkbox
    row.locator("input[type='checkbox']").click(force=True)

    pdf_btn = page.locator("mat-icon:has-text('picture_as_pdf')")

    with context.expect_page() as new_page_info:
        pdf_btn.first.click(force=True)

    new_page = new_page_info.value
    new_page.wait_for_load_state()

    blob_url = new_page.url

    pdf_base64 = new_page.evaluate("""
        async (url) => {
            const resp = await fetch(url);
            const blob = await resp.blob();
            return new Promise(resolve => {
                const reader = new FileReader();
                reader.onload = () => resolve(reader.result.split(',')[1]);
                reader.readAsDataURL(blob);
            });
        }
    """, blob_url)

    pdf_bytes = base64.b64decode(pdf_base64)

    filename = f"{clinic_id}_{int(time.time())}.pdf"

    output_dir = Path(PDF_OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    filepath = output_dir / filename
    filepath.write_bytes(pdf_bytes)

    new_page.close()

    return True


# --------------------------------------------------
# MAIN PROCESS
# --------------------------------------------------

def process(page, context, allowed_patient_ids):
    logger.info("Scraping page...")

    rows = scrape_current_page(page, allowed_patient_ids)

    logger.info(f"Matched rows: {len(rows)}")

    downloaded = 0

    for row in rows:
        idx = row["rowIndex"]

        if download_pdf(page, context, idx, "patient"):
            downloaded += 1

    return downloaded


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--headless", action="store_true")
    args = parser.parse_args()

    portal_db.init_table("carelink")

    # TODO: replace with DB credentials
    user_id = os.getenv("CARELINK_USER")
    password = os.getenv("CARELINK_PASS")

    allowed_patient_ids = {"123", "456"}  # replace

    with sync_playwright() as pw:
        browser, context, page = login(pw, user_id, password, args.headless)

        page.goto(HOME_URL)

        total = process(page, context, allowed_patient_ids)

        logger.info(f"Downloaded PDFs: {total}")

        browser.close()


if __name__ == "__main__":
    main()