from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse
from datetime import datetime
import time
import os

# ================== Website eingeben ==================
website = input("Website eingeben (ohne https://): ").strip()

if not website.startswith(("http://", "https://")):
    URL = "https://" + website
else:
    URL = website

print(f"Verwende URL: {URL}")
# ======================================================

# Domain sauber extrahieren
parsed = urlparse(URL)
domain = parsed.netloc
if domain.startswith("www."):
    domain = domain[4:]

today = datetime.now().strftime("%Y-%m-%d")
folder = os.path.join("screenshots", domain, today)
os.makedirs(folder, exist_ok=True)

print(f"Speicherordner: {folder}")

# Chrome-Optionen (mit Fix für DevToolsActivePort)
options = Options()
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-notifications")
options.add_argument("--disable-popup-blocking")
options.add_argument("--disable-extensions")
options.add_argument("--remote-debugging-port=9222")          # ← Fix
options.add_argument("--user-data-dir=/tmp/chrome_selenium")  # ← Fix
options.page_load_strategy = "none"

# Headless AUS – Browser muss sichtbar sein
# options.add_argument("--headless=new")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

driver.set_script_timeout(30)

try:
    print(f"Öffne Website: {URL}")

    try:
        driver.get(URL)
    except TimeoutException:
        print("→ Renderer-Timeout – ignoriere und mache weiter...")

    time.sleep(3)

    print("\n" + "="*60)
    print("Bitte den Cookie-Banner jetzt manuell bestätigen/akzeptieren.")
    print("Danach hier im Terminal ENTER drücken, um die Screenshots zu starten.")
    print("="*60 + "\n")
    input(">>> ENTER drücken, wenn bereit...")

    # Höhen berechnen
    viewport_height = driver.execute_script("return window.innerHeight")
    total_height = driver.execute_script(
        "return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);"
    )

    scroll_position = 0
    screenshot_nr = 1

    print(f"\nSeitenhöhe: {total_height}px | Viewport: {viewport_height}px")
    print("Starte Screenshot-Serie...\n")

    while scroll_position < total_height:
        driver.execute_script(f"window.scrollTo(0, {scroll_position});")
        time.sleep(0.9)

        timestamp = datetime.now().strftime("%H-%M-%S")
        dateiname = os.path.join(folder, f"screenshot_{timestamp}_{screenshot_nr:03d}.png")
        driver.save_screenshot(dateiname)
        print(f"Gespeichert: {dateiname}  (Scroll-Position: {scroll_position}px)")

        scroll_position += viewport_height
        screenshot_nr += 1

        total_height = driver.execute_script(
            "return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);"
        )

    print(f"\nFertig! {screenshot_nr - 1} Screenshots gespeichert in: {folder}")

finally:
    driver.quit()
