from datetime import datetime

from models import Amendement


def parse_amendement_from_csv(d_amend: dict) -> Amendement:
    return Amendement(
        num=d_amend['Numéro '],
        article=d_amend['Subdivision '],
        alinea=d_amend['Alinéa'].strip(),
        auteur=d_amend['Auteur '],
        date_depot=parse_date(d_amend['Date de dépôt ']),
    )


def parse_date(text):
    if text == '':
        return None
    return datetime.strptime(text, '%Y-%m-%d').date()


def parse_amendement_from_json(
    amend: dict,
    subdiv: dict,
) -> Amendement:
    return Amendement(
        num=amend['num'],
        article=subdiv['libelle_subdivision'],
        alinea=amend['libelleAlinea'],
        auteur=amend['auteur'],
        identique=parse_bool(amend['isIdentique']),
        discussion_commune=(
            amend['idDiscussionCommune']
            if parse_bool(amend['isDiscussionCommune'])
            else None
        ),
    )


def parse_bool(text: str) -> bool:
    if text == 'true':
        return True
    if text == 'false':
        return False
    raise ValueError
