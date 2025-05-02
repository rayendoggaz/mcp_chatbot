from config import BASE_URL, COMMON_HEADERS, ARTIS_TOKEN
import requests

def ClientDataParFiltre(critere: str) -> str:
    """This endpoint allows you to filter and search clients by any keyword (name, number, fidelity card).
    Returns matching records with ID, client number, name, and loyalty balance."""
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {ARTIS_TOKEN}"
    }
    try:
        resp = requests.get(
            f"{BASE_URL}/client/client_fid_par_critere",
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

def ListeClients() -> str:
    """This endpoint returns the full list of clients in the system,
    providing each client’s ID, name, and client number."""
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {ARTIS_TOKEN}"
    }
    try:
        resp = requests.get(
            f"{BASE_URL}/client/client",
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

def register_tools(mcp):
    mcp.tool()(ClientDataParFiltre)
    mcp.tool()(ListeClients)