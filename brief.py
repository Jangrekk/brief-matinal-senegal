import requests
import feedparser

from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import quote_plus
from zoneinfo import ZoneInfo
from pathlib import Path


# ============================================================
# 🇸🇳 LE BRIEF MATINAL SÉNÉGAL
# Actualités récentes + météo des 14 régions
# ============================================================

FUSEAU_HORAIRE = ZoneInfo("Africa/Dakar")
NOMBRE_ARTICLES = 5
AGE_MAXIMUM_HEURES = 48


# ============================================================
# 🌦️ COORDONNÉES DES 14 RÉGIONS DU SÉNÉGAL
# ============================================================

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


# ============================================================
# 📰 ACTUALITÉS : SÉNÉGAL, MONDE, TECHNOLOGIE ET EMPLOI
# ============================================================

def get_news():

    lignes = [
        "",
        "=" * 45,
        "📰 ACTUALITÉS ET INFORMATIONS",
        "=" * 45,
        f"📅 Articles recherchés sur les dernières "
        f"{AGE_MAXIMUM_HEURES} heures.",
        "ℹ️ Les dates indiquées sont celles fournies par les flux RSS."
    ]

    recherches = [
        (
            "🇸🇳 ACTUALITÉS DU SÉNÉGAL",
            "Sénégal actualités politique économie société"
        ),
        (
            "🌍 ACTUALITÉS INTERNATIONALES",
            "actualités internationales monde"
        ),
        (
            "💻 TECHNOLOGIE ET CYBERSÉCURITÉ",
            "intelligence artificielle technologie cybersécurité"
        ),
        (
            "🎓 EMPLOI, CONCOURS, BOURSES ET FORMATIONS",
            "Sénégal emploi recrutement concours bourses formations"
        ),
    ]

    maintenant = datetime.now(timezone.utc)
    limite = maintenant - timedelta(hours=AGE_MAXIMUM_HEURES)

    for categorie, recherche in recherches:

        lignes.append("")
        lignes.append("-" * 40)
        lignes.append(categorie)
        lignes.append("-" * 40)

        requete = quote_plus(f"{recherche} when:2d")

        url = (
            "https://news.google.com/rss/search?q="
            f"{requete}"
            "&hl=fr&gl=SN&ceid=SN:fr"
        )

        try:
            reponse = requests.get(
                url,
                timeout=25,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 "
                        "(compatible; BriefMatinalSenegal/1.0)"
                    )
                },
            )

            reponse.raise_for_status()

            flux = feedparser.parse(reponse.content)

            articles_recents = []

            for article in flux.entries:

                date_brute = article.get("published")

                if not date_brute:
                    continue

                try:
                    date_article = parsedate_to_datetime(date_brute)

                    if date_article.tzinfo is None:
                        date_article = date_article.replace(
                            tzinfo=timezone.utc
                        )

                    date_article = date_article.astimezone(
                        timezone.utc
                    )

                except (ValueError, TypeError, OverflowError):
                    continue

                # Garder uniquement les articles des dernières 48 heures.
                if limite <= date_article <= maintenant:

                    articles_recents.append(
                        (date_article, article)
                    )

            # Trier les articles du plus récent au plus ancien.
            articles_recents.sort(
                key=lambda element: element[0],
                reverse=True
            )

            if not articles_recents:
                lignes.append(
                    "Aucune actualité récente avec une date "
                    "de publication vérifiable n'a été trouvée."
                )
                continue

            # Limiter le nombre d'articles par catégorie.
            for date_article, article in articles_recents[
                :NOMBRE_ARTICLES
            ]:

                titre = article.get(
                    "title",
                    "Titre indisponible"
                )

                lien = article.get("link", "")

                date_locale = date_article.astimezone(
                    FUSEAU_HORAIRE
                )

                lignes.append("")
                lignes.append(f"• {titre}")

                lignes.append(
                    "  📅 Publié le : "
                    + date_locale.strftime(
                        "%d/%m/%Y à %H:%M"
                    )
                    + " (heure du Sénégal)"
                )

                if lien:
                    lignes.append(
                        f"  🔗 Lire la source : {lien}"
                    )

        except requests.RequestException:
            lignes.append(
                "Impossible de contacter la source d'actualités."
            )

        except Exception as erreur:
            lignes.append(
                "Erreur pendant la récupération des actualités : "
                + type(erreur).__name__
            )

    return "\n".join(lignes)


# ============================================================
# 🌦️ MÉTÉO DES 14 RÉGIONS DU SÉNÉGAL
# ============================================================

def get_weather():

    lignes = [
        "",
        "=" * 45,
        "🌦️ MÉTÉO DES 14 RÉGIONS DU SÉNÉGAL",
        "=" * 45,
        "Prévisions quotidiennes fournies par Open-Meteo.",
        "Les valeurs représentent un point de référence "
        "dans chaque région."
    ]

    for region, latitude, longitude in SENEGAL:

        try:
            reponse = requests.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "daily": (
                        "temperature_2m_max,"
                        "temperature_2m_min,"
                        "precipitation_probability_max"
                    ),
                    "timezone": "Africa/Dakar",
                    "forecast_days": 1,
                },
                timeout=25,
            )

            reponse.raise_for_status()

            donnees = reponse.json()
            meteo = donnees["daily"]

            minimum = meteo["temperature_2m_min"][0]
            maximum = meteo["temperature_2m_max"][0]
            pluie = meteo["precipitation_probability_max"][0]

            if minimum is None or maximum is None:
                lignes.append(
                    f"📍 {region} : températures indisponibles."
                )
                continue

            risque_pluie = (
                f"{pluie}%"
                if pluie is not None
                else "indisponible"
            )

            lignes.append(
                f"📍 {region} : "
                f"{minimum}–{maximum} °C"
                f" | Risque maximal de pluie : {risque_pluie}"
            )

        except Exception:
            lignes.append(
                f"📍 {region} : prévisions indisponibles."
            )

    return "\n".join(lignes)


# ============================================================
# 🧾 GÉNÉRATION DU BULLETIN COMPLET
# ============================================================

def main():

    maintenant = datetime.now(FUSEAU_HORAIRE)

    entete = [
        "🇸🇳 LE BRIEF MATINAL SÉNÉGAL",
        "",
        "Votre rendez-vous quotidien avec l'information.",
        "",
        f"📅 Date : {maintenant.strftime('%A %d/%m/%Y')}",
        f"🕗 Heure de génération : {maintenant.strftime('%H:%M')}",
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "📰 INFORMER • APPRENDRE • PROGRESSER",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    ]

    actualites = get_news()

    meteo = get_weather()

    pied_de_page = [
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "📌 CONSEILS AUX LECTEURS",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
        "• Consultez les liens pour lire les articles complets.",
        "• Vérifiez les concours et offres sur les sites officiels.",
        "• Ne payez jamais pour une offre d'emploi sans vérification.",
        "",
        "🌦️ Source météo : Open-Meteo.",
        "📰 Source des actualités : Google News RSS.",
        "",
        "🇸🇳 LE BRIEF MATINAL SÉNÉGAL",
        "L'essentiel pour commencer la journée.",
    ]

    contenu = "\n".join(
        entete
        + [actualites]
        + [meteo]
        + pied_de_page
    )

    chemin = Path("bulletin.txt")

    chemin.write_text(
        contenu,
        encoding="utf-8"
    )

    print(contenu)

    print("")
    print("✅ Bulletin généré avec succès.")
    print(f"📄 Fichier enregistré : {chemin.resolve()}")


# ============================================================
# 🚀 LANCEMENT DU PROGRAMME
# ============================================================

if __name__ == "__main__":
    main()
