import csv
import json
from collections import OrderedDict
from typing import List

import requests

from models import Amendement
from parser import (
    parse_amendement_from_csv,
    parse_amendement_from_json,
)


class NotFound(Exception):
    pass


def fetch_amendements(session: str, num: str) -> List[OrderedDict]:
    """
    Récupère tous les amendements, dans l'ordre de dépôt
    """
    url = f"http://www.senat.fr/amendements/{session}/{num}/jeu_complet_{session}_{num}.csv"  # noqa

    resp = requests.get(url)
    if resp.status_code == 404:
        raise NotFound(url)

    text = resp.content.decode('cp1252')
    lines = text.splitlines()[1:]
    reader = csv.DictReader(lines, delimiter='\t')
    items = list(reader)
    return items


def fetch_and_parse_amendements(session: str, num: str) -> List[Amendement]:
    return [
        parse_amendement_from_csv(item)
        for item in fetch_amendements(session, num)
    ]


def fetch_amendements_discussion(
    session: str,
    num: str,
    phase: str
) -> dict:
    """
    Récupère les amendements à discuter, dans l'ordre de passage

    NB : les amendements jugés irrecevables ne sont pas inclus.
    """
    assert phase in ('commission', 'seance')

    url = f'http://www.senat.fr/en{phase}/{session}/{num}/liste_discussion.json'  # noqa

    resp = requests.get(url)
    if resp.status_code == 404:
        raise NotFound(url)

    data = json.loads(resp.content)
    return data


def fetch_and_parse_amendements_discussion(
    session: str,
    num: str,
    phase: str,
) -> List[Amendement]:
    data = fetch_amendements_discussion(session, num, phase)
    return [
        parse_amendement_from_json(amend, subdiv)
        for subdiv in data['Subdivisions']
        for amend in subdiv['Amendements']
    ]
