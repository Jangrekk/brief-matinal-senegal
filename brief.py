import requests
import feedparser
from datetime import datetime
from zoneinfo import ZoneInfo

SENEGAL = [
    ("Dakar", 14.7167, -17.4677),
    ("Diourbel", 14.655, -16.234),
    ("Fatick", 14.339, -16.411),
    ("Kaffrine", 14.105, -15.550),
    ("Kaolack", 14.151, -16.072),
    ("Kédougou", 12.555, -12.175),
    ("Kolda", 12.883, -14.950),
    ("Louga", 15.618, -16.224),
    ("Matam", 15.655, -13.255),
    ("Saint-Louis", 16.017, -16.489),
    ("Sédhiou", 12.708, -15.556),
    ("Tambacounda", 13.770, -13.668),
    ("Thiès", 14.791, -16.935),
    ("Ziguinchor", 12.583, -16.271),
]

def get_weather():
    print("\n🌦️ MÉTÉO DES 14 RÉGIONS DU SÉNÉGAL\n")

    for region, lat, lon in SENEGAL:
        try:
            url = "https://api.open-meteo.com/v1/forecast"

            params = {
                "latitude": lat,
                "longitude": lon,
                "daily": (
                    "temperature_2m_max,"
                    "temperature_2m_min,"
                    "precipitation_probability_max"
                ),
                "timezone": "Africa/Dakar",
                "forecast_days": 1,
            }

            response = requests.get(
                url, params=params, timeout=20
            )
            response.raise_for_status()
            data = response.json()["daily"]

            minimum = data["temperature_2m_min"][0]
            maximum = data["temperature_2m_max"][0]
            pluie = data[
                "precipitation_probability_max"
            ][0]

            print(
                f"📍 {region} : {minimum}–{maximum} °C"
                f" | Probabilité maximale de pluie : {pluie}%"
            )

        except Exception as error:
            print(
                f"📍 {region} : prévisions indisponibles "
                f"({type(error).__name__})"
            )

def get_news():
    print("\n📰 ACTUALITÉS DU SÉNÉGAL ET DU MONDE\n")

    feeds = [
        (
            "Sénégal",
            "https://news.google.com/rss/search?"
            "q=S%C3%A9n%C3%A9gal&hl=fr&gl=SN&ceid=SN:fr"
        ),
        (
            "Monde",
            "https://news.google.com/rss/search?"
            "q=actualit%C3%A9s+internationales&"
            "hl=fr&gl=SN&ceid=SN:fr"
        ),
        (
            "Technologie",
            "https://news.google.com/rss/search?"
            "q=intelligence+artificielle+cybers%C3%A9curit%C3%A9&"
            "hl=fr&gl=SN&ceid=SN:fr"
        ),
        (
            "Emploi et formations",
            "https://news.google.com/rss/search?"
            "q=S%C3%A9n%C3%A9gal+emploi+concours+bourses&"
            "hl=fr&gl=SN&ceid=SN:fr"
        ),
    ]

    for category, url in feeds:
        print(f"\n🔎 {category}")

        try:
            feed = feedparser.parse(url)

            if not feed.entries:
                print("Aucun article récupéré.")
                continue

            for article in feed.entries[:4]:
                title = article.get("title", "Sans titre")
                link = article.get("link", "")

                print(f"• {title}")
                if link:
                    print(f"  Source : {link}")

        except Exception as error:
            print(
                f"Flux indisponible : {type(error).__name__}"
            )

def main():
    now = datetime.now(ZoneInfo("Africa/Dakar"))

    print("=" * 45)
    print("🇸🇳 LE BRIEF MATINAL SÉNÉGAL")
    print(now.strftime("📅 %d/%m/%Y à %H:%M"))
    print("=" * 45)

    get_news()
    get_weather()

    print("\n✅ Fin de la génération du bulletin.")
    print("ℹ️ Les articles doivent être vérifiés avant diffusion.")
    print("ℹ️ Ce programme ne publie pas encore sur WhatsApp.")

if __name__ == "__main__":
    main()
