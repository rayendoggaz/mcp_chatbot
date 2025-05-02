from config import BASE_URL, COMMON_HEADERS, ARTIS_TOKEN
import requests
from datetime import datetime

def ArticleData(designation: str) -> str:
    """This endpoint allows you to search for articles based on their designation (name or keyword). You
    can filter the results by stock availability and relevance to the cash register (POS). This endpoint is
    particularly useful for querying articles in an inventory system, helping to retrieve data such as
    prices, stock availability, and more.
    """
    headers = {
        "Content-Type": "application/json; utf-8",
        "Accept": "application/json",
        "Authorization": f"Bearer {ARTIS_TOKEN}"
    }
    try:
        resp = requests.get(
            f"{BASE_URL}/article/article_par_designation",
            params={"designation": designation},
            headers=headers
        )
        resp.raise_for_status()
        data = resp.json().get("content", [])
        if not data:
            return "❌ Aucun article trouvé avec cette désignation."
        a = data[0]
        return (
            f"🆔 *ID:* {a.get('id')}\n"
            f"📦 *Article:* {a.get('designation')}\n"
            f"💰 *Prix HT:* {a.get('prixUnitaire')}\n"
            f"💸 *Prix TTC:* {a.get('prixUnitaireTtc')}\n"
            f"📦 *Qte:* {a.get('qtStock')}\n"
            f"🧾 *TVA:* {a.get('tva', {}).get('tva')}"
        )
    except requests.exceptions.RequestException as e:
        return f"🚨 Erreur lors de la récupération des données: {e}"

def mouvement_stock_par_date(designation: str, date: str) -> str:
    """This link lets you see all the movements of products by date in and out of the warehouse using the designation and the date.
        - To see all movements
        - Or to search by product
        - Or to search by date
        - Or to search by product and date
    """
    headers = {
        "Content-Type": "application/json; utf-8",
        "Accept": "application/json",
        "Authorization": f"Bearer {ARTIS_TOKEN}"
    }
    params = {"designation": designation}
    if date:
        try:
            datetime.strptime(date, "%d/%m/%Y")
            params["dateMouvementStock"] = date
        except ValueError:
            return "📅❌ Format de date invalide. Utilisez jj/mm/aaaa."

    try:
        resp = requests.get(
            f"{BASE_URL}/mouvement_stock/mouvement_stock_tous",
            params=params,
            headers=headers
        )
        resp.raise_for_status()
        moves = resp.json().get("content", [])
        if not moves:
            return "📭 Aucun mouvement de stock trouvé pour cet article à cette date."

        out = []
        for m in moves:
            raw = m.get("dateMouvementStock")
            try:
                fmt = datetime.strptime(raw, "%Y-%m-%d").strftime("%d/%m/%Y")
            except Exception:
                fmt = raw
            out.append(
                f"🏷️ *Désignation:* {m['article']['designation']}\n"
                f"🏷️ *Code article:* {m['article']['codeArticle']}\n"
                f"📅 *Date du Mouvement:* {fmt}\n"
                f"📦 *Quantité:* {m.get('quantite')}\n"
                f"🧾 *Numéro de Mouvement:* {m.get('numero')}\n"
                f"🧭 *Catégorie de Mouvement:* {m.get('typeMouvementStock')}\n"
                f"🏬 *Magasin:* {m.get('magasin', {}).get('nom','N/A')}"
            )
        return "\n────────────────────────────\n".join(out)

    except requests.exceptions.RequestException as e:
        return f"🚨 Erreur d'accès au service de stock: {e}"

def register_tools(mcp):
    mcp.tool()(ArticleData)
    mcp.tool()(mouvement_stock_par_date)