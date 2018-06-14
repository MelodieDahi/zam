from typing import Any, List

from sqlalchemy import Column, Text, desc

from .base import Base, DBSession


CHAMBRES = {"assemblee": "Assemblée nationale", "senat": "Sénat"}

SESSIONS = ["2017-2018"]


class Lecture(Base):  # type: ignore
    __tablename__ = "lectures"

    chambre = Column(Text, primary_key=True)
    session = Column(Text, primary_key=True)
    num_texte = Column(Text, primary_key=True)

    @property
    def chambre_disp(self) -> str:
        return CHAMBRES[self.chambre]

    def __str__(self) -> str:
        return f"{self.chambre_disp}, session {self.session}, texte nº {self.num_texte}"

    def __lt__(self, other: Any) -> bool:
        if type(self) != type(other):
            return NotImplemented
        return (self.chambre, self.session, int(self.num_texte)) < (
            other.chambre,
            other.session,
            int(other.num_texte),
        )

    @classmethod
    def all(cls) -> List["Lecture"]:
        lectures: List["Lecture"] = DBSession.query(cls).order_by(
            cls.chambre, desc(cls.session), desc(cls.num_texte)
        ).all()
        return lectures

    @classmethod
    def get(cls, chambre: str, session: str, num_texte: str) -> "Lecture":
        res: "Lecture" = (
            DBSession.query(cls)
            .filter(
                cls.chambre == chambre,
                cls.session == session,
                cls.num_texte == num_texte,
            )
            .first()
        )
        return res

    @classmethod
    def exists(cls, chambre: str, session: str, num_texte: str) -> bool:
        res: bool = DBSession.query(
            DBSession.query(cls)
            .filter(
                cls.chambre == chambre,
                cls.session == session,
                cls.num_texte == num_texte,
            )
            .exists()
        ).scalar()
        return res

    @classmethod
    def create(cls, chambre: str, session: str, num_texte: str) -> "Lecture":
        lecture = cls(chambre=chambre, session=session, num_texte=num_texte)
        DBSession.add(lecture)
        return lecture
