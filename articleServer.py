# articleServer.py
"""
MCP tool-server exposing:
 - ArticleData(designation: str)
 - mouvement_stock_par_date(designation: str, date: str)
 - ClientDataParFiltre(critere: str)
 - ListeClients()
"""

from flask import json
from mcp.server.fastmcp import FastMCP
import requests
from datetime import datetime
from dotenv import load_dotenv
import os

# Load your Artis bearer token from .env
load_dotenv()
ARTIS_TOKEN = os.environ.get("ARTIS_BEARER_TOKEN")
if not ARTIS_TOKEN:
    raise RuntimeError("ARTIS_BEARER_TOKEN not set in .env")

BASE_URL = "http://localhost:8080/artis/api"
COMMON_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {ARTIS_TOKEN}"
}

mcp = FastMCP("churnandburn")

# ---------- Article endpoints ----------
@mcp.tool()
def ArticleData(designation: str) -> str:
    """This endpoint allows you to search for articles based on their designation (name or keyword). You
    can filter the results by stock availability and relevance to the cash register (POS). This endpoint is
    particularly  useful  for  querying  articles  in  an  inventory  system,  helping  to  retrieve  data  such  as
    prices, stock availability, and more.
    """
    headers = {
        "Content-Type": "application/json; utf-8",
        "Accept": "application/json",
        "Authorization": f"Bearer {ARTIS_TOKEN}"
    }
    try:
        resp = requests.get(
            "http://localhost:8080/artis/api/article/article_par_designation",
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


@mcp.tool()
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
            "http://localhost:8080/artis/api/mouvement_stock/mouvement_stock_tous",
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


# ---------- Client endpoints ----------
@mcp.tool()
def ClientDataParFiltre(critere: str) -> str:
    """This endpoint allows you to filter and search clients by any keyword (name, number, fidelity card).
    Returns matching records with ID, client number, name, and loyalty balance."""
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {ARTIS_TOKEN}"
    }
    try:
        resp = requests.get(
            "http://localhost:8080/artis/api/client/client_fid_par_critere",
            params={"critere": critere},
            headers=headers
        )
        resp.raise_for_status()
        clients = resp.json().get("content", [])
        if isinstance(clients, dict):
            clients = [clients]
        if not clients:
            return "❌ Aucun client ne correspond."

        lines = []
        for c in clients:
            lines.append(
                f"🆔 *ID:* {c.get('id')}\n"
                f"👤 *Nom:* {c.get('nomClient')}\n"
                f"🔢 *Numéro:* {c.get('numeroClient')}\n"
                f"💳 *Solde Fidélité:* {c.get('soldeFidelite')} {c.get('devise', {}).get('symbole','')}"
            )
        return "\n────────────────────────────\n".join(lines)

    except requests.exceptions.RequestException as e:
        return f"🚨 Erreur ClientDataParFiltre: {e}"


@mcp.tool()
def ListeClients() -> str:
    """This endpoint returns the full list of clients in the system,
    providing each client’s ID, name, and client number."""
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {ARTIS_TOKEN}"
    }
    try:
        resp = requests.get(
            "http://localhost:8080/artis/api/client/client",
            headers=headers
        )
        resp.raise_for_status()
        data = resp.json()
        clients = data.get("content", data) if isinstance(data, dict) else data
        if isinstance(clients, dict):
            clients = [clients]
        if not clients:
            return "❌ Aucun client trouvé."

        return "\n".join(
            f"🆔 *ID:* {c.get('id')} - *Nom:* {c.get('nomClient')} ({c.get('numeroClient')})"
            for c in clients
        )

    except requests.exceptions.RequestException as e:
        return f"🚨 Erreur ListeClients: {e}"

# … below your other @mcp.tool() definitions …

@mcp.tool()
def sales_order(sales_order: dict) -> str:
    """
    Create a sales order.
    
    :param sales_order: JSON object in the following format:
      {
        "client": "C_10002",
        "lignes": [
          {
            "article": {"designation": "FILTRE A HUILE MISFAT L138"},
            "quantite": 2
          }
        ]
      }
    :return: Confirmation string with montant_ht and montant_ttc, or error message.
    """
    # --- Helper functions ---
    def get_client_info(code: str) -> dict | None:
        resp = requests.get(
            f"{BASE_URL}/client/client_fid_par_critere",
            params={"critere": code},
            headers=COMMON_HEADERS
        )
        resp.raise_for_status()
        content = resp.json().get("content", [])
        return content[0] if content else None

    def get_article_info(designation: str) -> dict | None:
        resp = requests.get(
            f"{BASE_URL}/article/article_par_designation",
            params={"designation": designation},
            headers=COMMON_HEADERS
        )
        resp.raise_for_status()
        content = resp.json().get("content", [])
        return content[0] if content else None

    # --- Fetch and validate client ---
    client_code = sales_order.get("client")
    client_info = get_client_info(client_code)
    if not client_info:
        return f"❌ Aucun client trouvé pour '{client_code}'."

    # Replace client field with full object
    sales_order["client"] = {
        "id": client_info["id"],
        "numeroClient": client_info["numeroClient"]
    }

    # --- Build lines and totals ---
    total_ht = 0.0
    total_ttc = 0.0

    for ligne in sales_order.get("lignes", []):
        desig = ligne.get("article", {}).get("designation")
        qty = ligne.get("quantite", 1)

        art_info = get_article_info(desig)
        if not art_info:
            return f"❌ Article introuvable : '{desig}'."

        pu_ht = art_info.get("prixUnitaire", 0.0)
        pu_ttc = art_info.get("prixUnitaireTtc", 0.0)
        if pu_ht <= 0 or pu_ttc <= 0:
            return f"❌ Prix invalide pour '{desig}': HT={pu_ht}, TTC={pu_ttc}"

        montant_ht = pu_ht * qty
        montant_ttc = pu_ttc * qty

        total_ht += montant_ht
        total_ttc += montant_ttc

        # overwrite the line with enriched info
        ligne["ligneCommentaire"] = False
        ligne["article"] = {
            "id": art_info["id"],
            "designation": art_info["designation"]
        }
        ligne["quantite"] = qty
        ligne["montantHT"] = round(montant_ht, 6)
        ligne["montantTTC"] = round(montant_ttc, 6)

    total_tva = total_ttc - total_ht

    # --- Finalize order payload ---
    sales_order.update({
        "id": None,
        "montantHT": round(total_ht, 6),
        "montantTVA": round(total_tva, 6),
        "montantTTC": round(total_ttc, 6),
        "netHT": round(total_ht, 6),
        "devise": {
            "codeIso": "TND",
            "designation": "dinars",
            "precision": 3,
            "symbole": "TND",
            "designationFraction": "millimes",
            "precisionCalcul": 3
        },
        "magasinParDefault": {"id": "1"}
    })

    # --- Send creation request ---
    try:
        resp = requests.post(
            f"{BASE_URL}/commande_vente/commande_vente",
            headers=COMMON_HEADERS,
            json=sales_order
        )
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        # Return both the error and the payload for debugging
        return (
            f"❌ Échec création commande : {e}\n\n"
            f"{json.dumps(sales_order, indent=2, ensure_ascii=False)}"
        )

    # --- Success summary ---
    return (
        f"✅ Commande créée pour {client_info.get('nomClient')}  \n"
        f"• Total HT : {total_ht:.2f} TND  \n"
        f"• Total TVA : {total_tva:.2f} TND  \n"
        f"• Total TTC : {total_ttc:.2f} TND"
    )

if __name__ == "__main__":
    mcp.run(transport="stdio")