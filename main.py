from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "✅ Willhaben-Watcher läuft!"

def run_server():
    app.run(host='0.0.0.0', port=8080)

# Webserver starten
Thread(target=run_server).start()
import time
import requests
from bs4 import BeautifulSoup

# === Hier DEINE Daten eintragen ===
WILLHABEN_URL = "https://www.willhaben.at/iad/gebrauchtwagen/auto/bmw-gebrauchtwagen/x3"
BOT_TOKEN = "8291502722:AAFZwL-g89YEiSSVNI0RFuEE53GNQnQSWzU"
CHAT_ID = "6369503548"

gesehene_anzeigen = set()

def sende_telegram_nachricht(text):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    payload = {'chat_id': CHAT_ID, 'text': text}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Fehler beim Senden der Nachricht:", e)

def hole_neue_anzeigen():
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(WILLHABEN_URL, headers=headers)
    except Exception as e:
        print("Fehler beim Abrufen der Seite:", e)
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    anzeigen_links = soup.find_all("a", href=True)
    neue = []

    for a in anzeigen_links:
        href = a["href"]
        if (
            href.startswith("/iad/gebrauchtwagen") or
            href.startswith("/iad/kaufen-und-verkaufen")
        ) and href not in gesehene_anzeigen:
            full_link = "https://www.willhaben.at" + href
            gesehene_anzeigen.add(href)
            neue.append(full_link)

    print(f"🔍 Gefundene Anzeigen: {len(neue)}")
    return neue

# Hauptprogramm
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
        time.sleep(30)  # oder 60, je nachdem wie oft du abfragen willst
    except Exception as e:
        print("💥 Fehler im Hauptloop:", e)
        print("🔁 Neustart in 60 Sekunden...")
        time.sleep(60)
