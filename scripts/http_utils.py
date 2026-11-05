# scripts/http_utils.py
# Requête HTTP avec nouvelles tentatives. Pourquoi : une API gratuite peut
# répondre 429 (quota) ou échouer ponctuellement ; on réessaie proprement
# au lieu de planter, mais on s'arrête si le quota JOURNALIER est atteint.
import time
import requests

from config import (TIMEOUT_S, NB_TENTATIVES, PAUSE_RETRY_S,
                    ATTENTE_429_MINUTE_S, ATTENTE_429_HEURE_S)


class ErreurAPI(Exception):
    """Erreur définitive (paramètre invalide, échec après toutes les tentatives)."""


class QuotaJournalierAtteint(Exception):
    """Limite journalière atteinte : inutile de réessayer aujourd'hui."""


def _raison(reponse):
    """Extrait le message d'erreur Open-Meteo (champ 'reason') s'il existe."""
    try:
        return str(reponse.json().get("reason", reponse.text[:200]))
    except ValueError:
        return reponse.text[:200]


def requete_json(url, params):
    """GET avec timeout et NB_TENTATIVES essais ; renvoie le JSON (dict)."""
    derniere_erreur = "inconnue"
    for essai in range(1, NB_TENTATIVES + 1):
        try:
            rep = requests.get(url, params=params, timeout=TIMEOUT_S)
        except requests.RequestException as e:      # réseau, timeout...
            derniere_erreur = f"réseau : {e}"
            print(f"   essai {essai}/{NB_TENTATIVES} : {derniere_erreur}")
            time.sleep(PAUSE_RETRY_S * essai)
            continue

        # Quota dépassé : on distingue minute / heure / jour d'après le message.
        if rep.status_code == 429:
            raison = _raison(rep)
            derniere_erreur = f"429 : {raison}"
            low = raison.lower()
            if "daily" in low:
                raise QuotaJournalierAtteint(raison)
            attente = ATTENTE_429_HEURE_S if "hourly" in low else ATTENTE_429_MINUTE_S
            print(f"   essai {essai}/{NB_TENTATIVES} : {derniere_erreur} -> attente {attente}s")
            time.sleep(attente)
            continue

        # Erreur client (400...) : requête invalide, réessayer ne sert à rien.
        if 400 <= rep.status_code < 500:
            raise ErreurAPI(f"HTTP {rep.status_code} : {_raison(rep)}")

        # Erreur serveur : on réessaie.
        if rep.status_code != 200:
            derniere_erreur = f"HTTP {rep.status_code}"
            print(f"   essai {essai}/{NB_TENTATIVES} : {derniere_erreur}")
            time.sleep(PAUSE_RETRY_S * essai)
            continue

        # HTTP 200 : on vérifie quand même le champ "error" et le format JSON.
        try:
            data = rep.json()
        except ValueError:
            derniere_erreur = "réponse non JSON"
            time.sleep(PAUSE_RETRY_S * essai)
            continue
        if isinstance(data, dict) and data.get("error"):
            raise ErreurAPI(f"champ error : {data.get('reason')}")
        return data

    raise ErreurAPI(f"échec après {NB_TENTATIVES} tentatives ({derniere_erreur})")