import datetime
import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest


HERE = Path(os.path.dirname(__file__))


DOSSIERS = HERE.parent / "sample_data" / "Dossiers_Legislatifs_XV.json"


@pytest.fixture(scope="module")
def textes():
    from zam_aspirateur.textes.dossiers_legislatifs import parse_textes

    with open(DOSSIERS) as f_:
        data = json.load(f_)
    return parse_textes(data["export"])


@pytest.fixture(scope="module")
def dossiers():
    from zam_aspirateur.textes.dossiers_legislatifs import get_dossiers_legislatifs

    with patch(
        "zam_aspirateur.textes.dossiers_legislatifs.extract_from_remote_zip"
    ) as m_open:
        m_open.return_value = DOSSIERS.open()
        dossiers_by_uid = get_dossiers_legislatifs(legislature=15)

    return dossiers_by_uid


def test_number_of_dossiers(dossiers):
    assert len(dossiers) == 605


@pytest.fixture
def dossier_plfss_2018():
    with open(HERE.parent / "sample_data" / "dossier-DLR5L15N36030.json") as f_:
        return json.load(f_)["dossierParlementaire"]


def test_parse_dossier_plfss_2018(dossier_plfss_2018, textes):
    from zam_aspirateur.textes.dossiers_legislatifs import parse_dossier
    from zam_aspirateur.textes.models import Chambre, Lecture, Dossier, Texte, TypeTexte

    dossier = parse_dossier(dossier_plfss_2018, textes)

    assert dossier == Dossier(
        uid="DLR5L15N36030",
        titre="Sécurité sociale : loi de financement 2018",
        lectures={
            "PRJLANR5L15B0269": Lecture(
                chambre=Chambre.AN,
                titre="Première lecture – Séance publique",
                texte=Texte(
                    uid="PRJLANR5L15B0269",
                    type_=TypeTexte.PROJET,
                    numero=269,
                    titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                    titre_court="PLFSS pour 2018",
                    date_depot=datetime.date(2017, 10, 11),
                ),
            ),
            "PRJLSNR5S299B0063": Lecture(
                chambre=Chambre.SENAT,
                titre="Première lecture – Séance publique",
                texte=Texte(
                    uid="PRJLSNR5S299B0063",
                    type_=TypeTexte.PROJET,
                    numero=63,
                    titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                    titre_court="PLFSS pour 2018",
                    date_depot=datetime.date(2017, 11, 6),
                ),
            ),
            "PRJLANR5L15B0387": Lecture(
                chambre=Chambre.AN,
                titre="Nouvelle lecture – Séance publique",
                texte=Texte(
                    uid="PRJLANR5L15B0387",
                    type_=TypeTexte.PROJET,
                    numero=387,
                    titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                    titre_court="PLFSS pour 2018",
                    date_depot=datetime.date(2017, 11, 21),
                ),
            ),
            "PRJLSNR5S299B0121": Lecture(
                chambre=Chambre.SENAT,
                titre="Nouvelle lecture – Séance publique",
                texte=Texte(
                    uid="PRJLSNR5S299B0121",
                    type_=TypeTexte.PROJET,
                    numero=121,
                    titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                    titre_court="PLFSS pour 2018",
                    date_depot=datetime.date(2017, 11, 30),
                ),
            ),
            "PRJLANR5L15B0434": Lecture(
                chambre=Chambre.AN,
                titre="Lecture définitive – Séance publique",
                texte=Texte(
                    uid="PRJLANR5L15B0434",
                    type_=TypeTexte.PROJET,
                    numero=434,
                    titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                    titre_court="PLFSS pour 2018",
                    date_depot=datetime.date(2017, 12, 1),
                ),
            ),
        },
    )


@pytest.fixture
def dossier_essoc():
    with open(HERE.parent / "sample_data" / "dossier-DLR5L15N36159.json") as f_:
        return json.load(f_)["dossierParlementaire"]


def test_parse_dossier_essoc(dossier_essoc, textes):
    from zam_aspirateur.textes.dossiers_legislatifs import parse_dossier
    from zam_aspirateur.textes.models import Chambre, Lecture, Dossier, Texte, TypeTexte

    dossier = parse_dossier(dossier_essoc, textes)

    assert dossier == Dossier(
        uid="DLR5L15N36159",
        titre="Fonction publique : un Etat au service d'une société de confiance",
        lectures={
            "PRJLANR5L15B0424": Lecture(
                chambre=Chambre.AN,
                titre="Première lecture – Commission saisie au fond",
                texte=Texte(
                    uid="PRJLANR5L15B0424",
                    type_=TypeTexte.PROJET,
                    numero=424,
                    titre_long="projet de loi pour un Etat au service d’une société de confiance",  # noqa
                    titre_court="Etat service société de confiance",
                    date_depot=datetime.date(2017, 11, 27),
                ),
            ),
            "PRJLANR5L15BTC0575": Lecture(
                chambre=Chambre.AN,
                titre="Première lecture – Séance publique",
                texte=Texte(
                    uid="PRJLANR5L15BTC0575",
                    type_=TypeTexte.PROJET,
                    numero=575,
                    titre_long="projet de loi sur le projet de loi, après engagement de la procédure accélérée, pour un Etat au service d’une société de confiance (n°424).",  # noqa
                    titre_court="Etat service société de confiance",
                    date_depot=datetime.date(2018, 1, 18),
                ),
            ),
            "PRJLSNR5S299B0259": Lecture(
                chambre=Chambre.SENAT,
                titre="Première lecture – Commission saisie au fond",
                texte=Texte(
                    uid="PRJLSNR5S299B0259",
                    type_=TypeTexte.PROJET,
                    numero=259,
                    titre_long="projet de loi pour un Etat au service d'une société de confiance",  # noqa
                    titre_court="État au service d'une société de confiance",
                    date_depot=datetime.date(2018, 1, 31),
                ),
            ),
            "PRJLSNR5S299BTC0330": Lecture(
                chambre=Chambre.SENAT,
                titre="Première lecture – Séance publique",
                texte=Texte(
                    uid="PRJLSNR5S299BTC0330",
                    type_=TypeTexte.PROJET,
                    numero=330,
                    titre_long="projet de loi  sur le projet de loi, adopté, par l'Assemblée nationale après engagement de la procédure accélérée, pour un Etat au service d'une société de confiance (n°259).",  # noqa
                    titre_court="État au service d'une société de confiance",
                    date_depot=datetime.date(2018, 2, 22),
                ),
            ),
            "PRJLANR5L15B0806": Lecture(
                chambre=Chambre.AN,
                titre="Nouvelle lecture – Commission saisie au fond",
                texte=Texte(
                    uid="PRJLANR5L15B0806",
                    type_=TypeTexte.PROJET,
                    numero=806,
                    titre_long="projet de loi renforçant l'efficacité de l'administration pour une relation de confiance avec le public",  # noqa
                    titre_court="Renforcement de l'efficacité de l'administration pour une relation de confiance avec le public",  # noqa
                    date_depot=datetime.date(2018, 3, 21),
                ),
            ),
            "PRJLANR5L15BTC1056": Lecture(
                chambre=Chambre.AN,
                titre="Nouvelle lecture – Séance publique",
                texte=Texte(
                    uid="PRJLANR5L15BTC1056",
                    type_=TypeTexte.PROJET,
                    numero=1056,
                    titre_long="projet de loi , en nouvelle lecture, sur le projet de loi, modifié par le Sénat, renforçant l'efficacité de l'administration pour une relation de confiance avec le public (n°806).",  # noqa
                    titre_court="Renforcement de l'efficacité de l'administration pour une relation de confiance avec le public",  # noqa
                    date_depot=datetime.date(2018, 6, 13),
                ),
            ),
        },
    )


def test_extract_actes(dossier_essoc):
    from zam_aspirateur.textes.dossiers_legislatifs import extract_actes

    assert len(extract_actes(dossier_essoc)) == 4


def test_gen_lectures(dossier_essoc, textes):
    from zam_aspirateur.textes.dossiers_legislatifs import (
        gen_lectures,
        Chambre,
        Lecture,
        Texte,
        TypeTexte,
    )

    acte = dossier_essoc["actesLegislatifs"]["acteLegislatif"][0]

    res = list(gen_lectures(acte, textes))
    assert res == [
        Lecture(
            chambre=Chambre.AN,
            titre="Première lecture – Commission saisie au fond",
            texte=Texte(
                uid="PRJLANR5L15B0424",
                type_=TypeTexte.PROJET,
                numero=424,
                titre_long="projet de loi pour un Etat au service d’une société de confiance",  # noqa
                titre_court="Etat service société de confiance",
                date_depot=datetime.date(2017, 11, 27),
            ),
        ),
        Lecture(
            chambre=Chambre.AN,
            titre="Première lecture – Séance publique",
            texte=Texte(
                uid="PRJLANR5L15BTC0575",
                type_=TypeTexte.PROJET,
                numero=575,
                titre_long="projet de loi sur le projet de loi, après engagement de la procédure accélérée, pour un Etat au service d’une société de confiance (n°424).",  # noqa
                titre_court="Etat service société de confiance",
                date_depot=datetime.date(2018, 1, 18),
            ),
        ),
    ]


def test_walk_actes(dossier_essoc, textes):
    from zam_aspirateur.textes.dossiers_legislatifs import walk_actes

    acte = dossier_essoc["actesLegislatifs"]["acteLegislatif"][0]
    assert list(walk_actes(acte)) == [
        ("COM-FOND", "PRJLANR5L15B0424"),
        ("DEBATS", "PRJLANR5L15BTC0575"),
    ]
