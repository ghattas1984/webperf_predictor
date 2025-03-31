import requests
from bs4 import BeautifulSoup
import time
import re
import os
import subprocess

def extract_features_from_url(url):
    try:
        start_time = time.time()
        response = requests.get(url, timeout=10)
        load_time = time.time() - start_time

        page_size = len(response.content) / (1024 * 1024)  # MB
        html = response.text

        soup = BeautifulSoup(html, "html.parser")
        elements = soup.find_all(["img", "script", "link", "iframe"])
        no_of_requests = len(elements)

        response_time = response.elapsed.total_seconds()
        document_complete_time = load_time
        time_to_interactive = document_complete_time + 1.2
        start_render_time = response_time + 0.5

        # حفظ HTML مؤقتاً للتحقق
        temp_file = "temp_page.html"
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(html)

        # تشغيل tidy أو html5validator يدويًا والتقاط عدد الأخطاء من stderr
        try:
            result = subprocess.run(
                ["html5validator", "--root", ".", "--files", temp_file, "--also-check-css"],
                capture_output=True, text=True
            )
            # نحسب عدد السطور التي تحتوي على "Error" في الإخراج
            errors = result.stderr.strip().splitlines()
            markup_validation = len([e for e in errors if "Error:" in e])
        except Exception as e:
            print("❌ HTML5 validation error fallback:", e)
            markup_validation = 0

        broken_links = 0
        for link in soup.find_all("a", href=True):
            href = link['href']
            if href.startswith("http"):
                try:
                    r = requests.head(href, timeout=3)
                    if r.status_code >= 400:
                        broken_links += 1
                except:
                    broken_links += 1

        compression = int(page_size * 1024 * 0.4)  # KB
        os.remove(temp_file)

        return [
            round(response_time, 2),          # Response_time
            round(load_time, 2),              # Load_time
            round(page_size, 2),              # Page Size (MB)
            broken_links,                     # Broken Links
            no_of_requests,                   # Number of Requests
            round(start_render_time, 2),      # Start Render Time
            round(time_to_interactive, 2),    # Time to Interactive
            markup_validation,                # HTML Validation Errors
            compression,                      # Compression Saved (KB)
            round(document_complete_time, 2)  # Document Complete Time
        ]

    except Exception as e:
        print("❌ Error while analyzing:", e)
        return [0] * 10


def get_recommendations(features):
    tips = []

    response_time = features[0]
    load_time = features[1]
    page_size = features[2]
    broken_link = features[3]
    no_of_request = features[4]
    start_render_time = features[5]
    time_to_interactive = features[6]
    markup_validation = features[7]
    compression = features[8]
    document_complete_time = features[9]

    if load_time > 3:
        tips.append("🔻 Reduce load time by optimizing images or using lazy loading.")
    if no_of_request > 80:
        tips.append("🧩 Reduce number of requests by combining or minifying JS/CSS.")
    if response_time > 1:
        tips.append("⚙️ Improve server response time. Consider using a CDN or better hosting.")
    if markup_validation > 0:
        tips.append("❌ Fix HTML markup validation errors.")
    if broken_link > 0:
        tips.append("🔗 Remove or fix broken links on the page.")
    if compression < 100:
        tips.append("📦 Enable better compression like GZIP or Brotli.")

    return tips
