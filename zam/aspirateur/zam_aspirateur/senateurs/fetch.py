import requests


URL = f"http://data.senat.fr/data/senateurs/ODSEN_GENERAL.csv"


def fetch_senateurs():
    resp = requests.get(URL)
    assert resp.status_code == 200

    text = resp.content.decode('cp1252')
    lines = text.splitlines()
    return lines
