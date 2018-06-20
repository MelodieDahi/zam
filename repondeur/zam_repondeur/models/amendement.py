from sqlalchemy import Boolean, Column, Date, Integer, Table, Text
from sqlalchemy.orm import mapper
from sqlalchemy.schema import ForeignKeyConstraint

from zam_aspirateur.amendements.models import Amendement

from .base import metadata


AVIS = [
    "Favorable",
    "Défavorable",
    "Favorable sous réserve de",
    "Retrait",
    "Retrait au profit de",
    "Retrait sinon rejet",
    "Retrait sous réserve de",
    "Sagesse",
]


amendements_table = Table(
    "amendements",
    metadata,
    #
    # Identification du texte
    #
    Column("chambre", Text, primary_key=True),
    Column("session", Text, primary_key=True),
    Column("num_texte", Integer, primary_key=True),
    ForeignKeyConstraint(
        ["chambre", "session", "num_texte"],
        ["lectures.chambre", "lectures.session", "lectures.num_texte"],
    ),
    #
    # Partie du texte visée
    #
    Column("subdiv_type", Text, nullable=False),  # article, ...
    Column("subdiv_num", Text, nullable=False),  # numéro
    Column("subdiv_mult", Text, nullable=True),  # bis, ter...
    Column("subdiv_pos", Text, nullable=True),  # avant / après
    Column("alinea", Text, nullable=True),  # libellé de l'alinéa de l'article concerné
    #
    # Numéro de l'amendement
    #
    Column("num", Integer, primary_key=True),
    #
    # Numéro de révision de l'amendement
    #
    Column("rectif", Integer, nullable=False, default=0),
    #
    # Auteur de l'amendement
    #
    Column("auteur", Text, nullable=True),
    Column("matricule", Text, nullable=True),
    Column("groupe", Text, nullable=True),  # groupe parlementaire
    #
    # Date de dépôt de l'amendement (est-ce la date initiale,
    # ou bien est-ce mis à jour si l'amendement est rectifié ?)
    #
    Column("date_depot", Date, nullable=True),
    #
    Column("sort", Text, nullable=True),  # retiré, adopté, etc.
    #
    # Ordre et regroupement lors de la discussion
    #
    Column("position", Integer, nullable=True),
    Column("discussion_commune", Integer, nullable=True),
    Column("identique", Boolean, nullable=True),
    #
    # Contenu de l'amendement
    #
    Column("dispositif", Text, nullable=True),  # texte de l'amendement
    Column("objet", Text, nullable=True),  # motivation
    Column("resume", Text, nullable=True),  # résumé de l'objet
    #
    # Avis et réponse
    #
    Column("avis", Text, nullable=True),  # position du gouvernemnt
    Column("observations", Text, nullable=True),
    Column("reponse", Text, nullable=True),
)


mapper(
    Amendement,
    amendements_table,
    properties={
        # for some reason, those fields do not get mapped automatically,
        # so we map them explicitly here
        "subdiv_mult": amendements_table.c.subdiv_mult,
        "subdiv_pos": amendements_table.c.subdiv_pos,
        "alinea": amendements_table.c.alinea,
        "num": amendements_table.c.num,
        "rectif": amendements_table.c.rectif,
        "auteur": amendements_table.c.auteur,
        "groupe": amendements_table.c.groupe,
    },
)
