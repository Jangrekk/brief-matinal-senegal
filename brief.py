import requests
import feedparser
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

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
    lignes = ["\n🌦️ MÉTÉO DES 14 RÉGIONS DU SÉNÉGAL\n"]

    for region, lat, lon in SENEGAL:
        try:
            response = requests.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "daily": (
                        "temperature_2m_max,"
                        "temperature_2m_min,"
                        "precipitation_probability_max"
                    ),
                    "timezone": "Africa/Dakar",
                    "forecast_days": 1,
                },
                timeout=20,
            )
            response.raise_for_status()
            data = response.json()["daily"]

            minimum = data["temperature_2m_min"][0]
            maximum = data["temperature_2m_max"][0]
            pluie = data["precipitation_probability_max"][0]

            lignes.append(
                f"📍 {region} : {minimum}–{maximum} °C"
                f" | Risque maximal de pluie : {pluie}%"
            )

        except Exception:
            lignes.append(f"📍 {region} : prévisions indisponibles")

    return "\n".join(lignes)

def get_news():
    lignes = ["\n📰 ACTUALITÉS ET INFORMATIONS\n"]

    flux = [
        (
            "🇸🇳 Sénégal",
            "https://news.google.com/rss/search?q=S%C3%A9n%C3%A9gal"
            "&hl=fr&gl=SN&ceid=SN:fr",
        ),
        (
            "🌍 Monde",
            "https://news.google.com/rss/search?q=actualit%C3%A9s"
            "+internationales&hl=fr&gl=SN&ceid=SN:fr",
        ),
        (
            "💻 Technologie et cybersécurité",
            "https://news.google.com/rss/search?q=intelligence"
            "+artificielle+cybers%C3%A9curit%C3%A9"
            "&hl=fr&gl=SN&ceid=SN:fr",
        ),
        (
            "🎓 Emploi, concours et formations",
            "https://news.google.com/rss/search?q=S%C3%A9n%C3%A9gal"
            "+emploi+concours+bourses&hl=fr&gl=SN&ceid=SN:fr",
        ),
    ]

    for categorie, url in flux:
        lignes.append(f"\n{categorie}\n")

        try:
            feed = feedparser.parse(url)
            articles = feed.entries[:4]

            if not articles:
                lignes.append("Aucun article récupéré.")
                continue

            for article in articles:
                titre = article.get("title", "Sans titre")
                lien = article.get("link", "")

                lignes.append(f"• {titre}")

                if lien:
                    lignes.append(f"  🔗 Lire la source :{lien}")

        except Exception:
            lignes.append("Flux d'actualités indisponible.")

    return "\n".join(lignes)

def main():
    maintenant = datetime.now(ZoneInfo("Africa/Dakar"))

    bulletin = [
        "🇸🇳 LE BRIEF MATINAL SÉNÉGAL",
        f"📅 {maintenant.strftime('%d/%m/%Y')}",
        "",
        "Votre rendez-vous quotidien avec l'information.",
        get_news(),
        get_weather(),
        "",
        "ℹ️ Vérifiez les informations et les annonces officielles "
        "avant toute décision.",
        "📡 Sources : liens des articles et Open-Meteo pour la météo.",
    ]

    contenu = "\n".join(bulletin)
    Path("bulletin.txt").write_text(contenu, encoding="utf-8")

    print(contenu)
    print("\n✅ Bulletin enregistré dans bulletin.txt")

if __name__ == "__main__":
    main()
