from config import BASE_URL, COMMON_HEADERS
import requests
from flask import json

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

def register_tools(mcp):
    mcp.tool()(sales_order)