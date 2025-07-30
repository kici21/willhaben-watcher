from flask import Flask
from threading import Thread
import time
import requests
from bs4 import BeautifulSoup

# Webserver starten
app = Flask('')

@app.route('/')
def home():
    return "✅✅ Willhaben-Watcher läuft!"

def run_server():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run_server).start()

# === Deine Daten hier eintragen ===
WILLHABEN_URLS = [
    "https://www.willhaben.at/iad/gebrauchtwagen/auto/bmw-gebrauchtwagen/x3",
    "https://www.willhaben.at/iad/gebrauchtwagen/auto/gebrauchtwagenboerse?sfId=79088eeb-d3c6-4a42-bd15-06b12af166d0&isNavigation=true&CAR_MODEL/MAKE=1005&CAR_MODEL/MODEL=1042&YEAR_MODEL_FROM=2017&PRICE_TO=20000&ENGINEEFFECT_FROM=169"
]

BOT_TOKEN = "8291502722:AAFZwL-g89YEiSSVNI0RFuEE53GNQnQSWzU"
CHAT_IDS = ["6369503548", ""]  # Füge beliebig viele IDs hinzu

gesehene_anzeigen = set()

# Nachricht an alle Chat-IDs senden
def sende_telegram_nachricht(text):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    for chat_id in CHAT_IDS:
        payload = {'chat_id': chat_id, 'text': text}
        try:
            requests.post(url, data=payload)
        except Exception as e:
            print(f"Fehler beim Senden an {chat_id}:", e)

# Neue Anzeigen abrufen
def hole_neue_anzeigen():
    neue = []
    headers = {'User-Agent': 'Mozilla/5.0'}

    for url in WILLHABEN_URLS:
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all("a", href=True)

            for a in links:
                href = a["href"]
                if (href.startswith("/iad/gebrauchtwagen") or href.startswith("/iad/kaufen-und-verkaufen")) \
                        and href not in gesehene_anzeigen:
                    full_link = "https://www.willhaben.at" + href
                    gesehene_anzeigen.add(href)
                    neue.append(full_link)
        except Exception as e:
            print("❌ Fehler beim Abrufen der Seite:", e)

    print(f"🔎 Gefundene neue Anzeigen: {len(neue)}")
    return neue

# Hauptloop
print("Starte Willhaben-Überwachung...\n")

while True:
    try:
        neue = hole_neue_anzeigen()
        if neue:
            for link in neue:
                nachricht = f"📌 Neues Willhaben-Inserat:\n{link}"
                sende_telegram_nachricht(nachricht)
                print("✅ Gesendet:", link)
        else:
            print("Keine neuen Anzeigen.")
        time.sleep(120)  # 2 Minuten
    except Exception as e:
        print("❌ Fehler im Hauptloop:", e)
        print("🔄 Neustart in 2 Minuten...")
        time.sleep(120)
