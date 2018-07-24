from datetime import date
from functools import partial
from typing import Dict, IO, List, Optional

from lxml import etree

from zam_repondeur.clean import clean_html
from zam_repondeur.data import get_data
from zam_repondeur.fetch.an.dossiers.models import Chambre, Dossier, Texte
from zam_repondeur.fetch.dates import parse_date
from zam_repondeur.fetch.division import _parse_subdiv
from zam_repondeur.fetch.models import Amendement


NS = "{http://schemas.assemblee-nationale.fr/referentiel}"


def import_liasse_xml(xml_file: IO[bytes]) -> List[Amendement]:
    try:
        tree = etree.parse(xml_file)
    except etree.XMLSyntaxError:
        raise ValueError("Not a valid XML file")

    root = tree.getroot()
    if root.tag != "amendements":
        raise ValueError("Expecting 'amendements' as a root element")

    return [_make_amendement(child) for child in root]


def _make_amendement(node: etree.Element) -> Amendement:
    extract = partial(extract_from_node, node)

    titre = extract("pointeurFragmentTexte", "division", "titre")
    if titre is None:
        raise ValueError("Missing division")
    subdiv = _parse_subdiv(titre)

    texte_uid = extract("identifiant", "saisine", "refTexteLegislatif")
    if texte_uid is None:
        raise ValueError("Missing refTexteLegislatif")

    auteur_uid = extract("signataires", "auteur", "acteurRef")
    if auteur_uid is None:
        raise ValueError("Missing auteur acteurRef")

    groupe_uid = extract("signataires", "auteur", "groupePolitiqueRef")
    if groupe_uid is None:
        raise ValueError("Missing auteur groupePolitiqueRef")

    return Amendement(  # type: ignore
        chambre=Chambre.AN.value,
        session=extract("identifiant", "legislature"),
        num_texte=get_texte_number(texte_uid),
        organe=extract("identifiant", "saisine", "organeExamen"),
        subdiv_type=subdiv.type_,
        subdiv_num=subdiv.num,
        subdiv_mult=subdiv.mult,
        subdiv_pos=subdiv.pos,
        alinea=to_int(extract("pointeurFragmentTexte", "alinea", "numero")),
        num=to_int(extract("identifiant", "numero")),
        auteur=get_auteur_name(auteur_uid),
        matricule=auteur_uid,
        groupe=get_groupe_name(groupe_uid),
        date_depot=to_date(extract("dateDepot")),
        sort=get_sort(extract("etat")),
        dispositif=clean_html(extract("corps", "dispositif") or ""),
        objet=clean_html(extract("corps", "exposeSommaire") or ""),
    )


def extract_from_node(node: etree.Element, *path: str) -> Optional[str]:
    element_path = "." + "/".join((NS + elem) for elem in path)
    elem: Optional[etree.Element] = node.find(element_path)
    if elem is None:
        return None
    text: str = elem.text
    return text


def to_int(text: Optional[str]) -> Optional[int]:
    if text is None:
        return None
    return int(text)


def to_date(text: Optional[str]) -> Optional[date]:
    if text is None:
        return None
    return parse_date(text)


def get_texte_number(uid: str) -> int:
    texte = _find_texte(uid)
    numero: int = texte.numero
    return numero


def _find_texte(uid: str) -> Texte:
    # FIXME: this is not efficient
    dossiers: Dict[str, Dossier] = get_data("dossiers")
    for dossier in dossiers.values():
        for lecture in dossier.lectures:
            if lecture.texte.uid == uid:
                return lecture.texte
    raise ValueError(f"Unknown texte {uid}")


def get_sort(text: Optional[str]) -> str:
    if text is None:
        return ""
    if text == "En traitement":
        return ""
    return text


def get_auteur_name(uid: str) -> str:
    acteurs = get_data("acteurs")
    if uid not in acteurs:
        raise ValueError(f"Unknown auteur {uid}")
    acteur = acteurs[uid]
    ident: Dict[str, str] = acteur["etatCivil"]["ident"]
    return ident["prenom"] + " " + ident["nom"]


def get_groupe_name(uid: str) -> str:
    organes = get_data("organes")
    if uid not in organes:
        raise ValueError(f"Unknown groupe {uid}")
    libelle: str = organes[uid]["libelle"]
    return libelle
