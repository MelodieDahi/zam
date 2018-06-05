"""
Récupérer la liste des amendements à un texte de loi au Sénat
"""
import argparse
import math
import sys
from typing import Dict, Iterable, Iterator, List, Optional

from zam_aspirateur.amendements.fetch import (
    fetch_and_parse_all,
    fetch_and_parse_discussed,
    fetch_title,
    NotFound,
)
from zam_aspirateur.amendements.models import Amendement
from zam_aspirateur.amendements.writer import (
    write_csv,
    write_json_for_viewer,
    write_xlsx,
)
from zam_aspirateur.senateurs.fetch import fetch_senateurs
from zam_aspirateur.senateurs.models import Senateur
from zam_aspirateur.senateurs.parse import parse_senateurs


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv=argv)

    print("Récupération du titre...")
    title = fetch_title(session=args.session, num=args.texte)

    print("Récupération des amendements déposés...")
    try:
        amendements = fetch_and_parse_all(session=args.session, num=args.texte)
    except NotFound:
        print("Aucun amendement déposé pour l'instant!")
        return 1

    processed_amendements = process_amendements(
        amendements=amendements, session=args.session, num=args.texte
    )

    format = args.output_format
    default_filename = f"amendements_{args.session}_{args.texte}.{format}"

    save_output(
        title=title,
        amendements=processed_amendements,
        filename=args.output or default_filename,
        format=format,
    )

    return 0


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--session", required=True, help="session parlementaire (p.ex. 2017-2018)"
    )
    parser.add_argument(
        "--texte", required=True, help="numéro du texte au Sénat (p.ex. 330)"
    )
    parser.add_argument("--output", help="nom de fichier de la sortie")
    parser.add_argument(
        "--output-format",
        default="csv",
        choices=["csv", "xlsx", "json"],
        help="format de sortie à générer",
    )
    return parser.parse_args(argv)


def process_amendements(
    amendements: Iterable[Amendement], session: str, num: str
) -> Iterable[Amendement]:

    # Les amendements discutés en séance, par ordre de passage
    print("Récupération des amendements soumis à la discussion...")
    amendements_derouleur = fetch_and_parse_discussed(
        session=session, num=num, phase="seance"
    )
    if len(amendements_derouleur) == 0:
        print("Aucun amendement soumis à la discussion pour l'instant!")

    print("Récupération de la liste des sénateurs...")
    senateurs_by_matricule = fetch_and_parse_senateurs()

    amendements_avec_groupe = _enrich_groupe_parlementaire(
        amendements, senateurs_by_matricule
    )

    return _sort(
        _enrich(amendements_avec_groupe, amendements_derouleur), amendements_derouleur
    )


def fetch_and_parse_senateurs() -> Dict[str, Senateur]:
    lines = fetch_senateurs()
    by_matricule = parse_senateurs(lines)  # type: Dict[str, Senateur]
    return by_matricule


def _enrich_groupe_parlementaire(
    amendements: Iterable[Amendement], senateurs_by_matricule: Dict[str, Senateur]
) -> Iterator[Amendement]:
    """
    Enrichir les amendements avec le groupe parlementaire de l'auteur
    """
    return (
        amendement.replace(
            groupe=(
                senateurs_by_matricule[amendement.matricule].groupe
                if amendement.matricule is not None
                else None
            )
        )
        for amendement in amendements
    )


def _enrich(
    amendements: Iterable[Amendement], amendements_derouleur: Iterable[Amendement]
) -> Iterator[Amendement]:
    """
    Enrichir les amendements avec les informations du dérouleur

    - discussion commune ?
    - amendement identique ?
    """
    amendements_discussion_by_num = {
        amend.num_int: amend for amend in amendements_derouleur
    }
    return (
        _enrich_one(amend, amendements_discussion_by_num.get(amend.num_int))
        for amend in amendements
    )


def _enrich_one(
    amend: Amendement, amend_discussion: Optional[Amendement]
) -> Amendement:
    if amend_discussion is None:
        return amend
    return amend.replace(
        discussion_commune=amend_discussion.discussion_commune,
        identique=amend_discussion.identique,
    )


def _sort(
    amendements: Iterable[Amendement], amendements_derouleur: Iterable[Amendement]
) -> List[Amendement]:
    """
    Trier les amendements par ordre de passage, puis par numéro
    """
    amendements_discussion_order = {
        amend.num_int: index for index, amend in enumerate(amendements_derouleur)
    }
    return sorted(
        amendements,
        key=lambda a: (
            amendements_discussion_order.get(a.num_int, math.inf),
            a.num_int,
        ),
    )


def save_output(
    title: str, amendements: Iterable[Amendement], filename: str, format: str
) -> None:
    """
    Save amendments

    - as a spreadsheet, either in CSV or XLSX format
    - as a JSON file suitable for opening with the viewer
    """
    if format in ("csv", "xlsx"):
        write_func = write_csv if format == "csv" else write_xlsx
        print("Écriture du tableau...")
        nb_rows = write_func(amendements, filename)
        print(f"{nb_rows} amendements écrits dans {filename}")
    elif format == "json":
        print("Écriture du fichier...")
        nb_rows = write_json_for_viewer(1, title, amendements, filename)
        print(f"{nb_rows} amendements écrits dans {filename}")
    else:
        raise NotImplementedError


if __name__ == "__main__":
    sys.exit(main())
