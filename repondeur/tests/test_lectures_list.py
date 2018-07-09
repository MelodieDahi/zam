import pytest
import transaction


def test_get_list_empty(app):

    resp = app.get("/lectures/")

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    assert "Aucune lecture pour l’instant." in resp.text


@pytest.fixture
def dummy_lecture_commission(app):
    from zam_repondeur.models import DBSession, Lecture

    with transaction.manager:
        lecture = Lecture(
            chambre="an",
            session="15",
            num_texte=269,
            titre="Titre lecture",
            organe="PO420120",
        )
        DBSession.add(lecture)

    return lecture


def test_get_list_not_empty(app, dummy_lecture, dummy_lecture_commission):

    resp = app.get("/lectures/")

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    links = resp.parser.css("td a")
    assert [link.text() for link in links] == [
        "Assemblée nationale, 15e législature, Commission des affaires sociales, texte nº 269",  # noqa
        "Assemblée nationale, 15e législature, Séance publique, texte nº 269",
    ]
    assert links[0].attributes["href"] != links[1].attributes["href"]


def test_get_list_reverse_datetime_order(app, dummy_lecture):
    from zam_repondeur.models import DBSession, Lecture

    with transaction.manager:
        lecture = Lecture.get(
            chambre=dummy_lecture[0],
            session=dummy_lecture[1],
            num_texte=dummy_lecture[2],
        )
        title = str(lecture)
        lecture2 = Lecture.create(
            chambre=dummy_lecture[0],
            session=dummy_lecture[1],
            num_texte=dummy_lecture[2] + 1,
            titre="Titre lecture 2",
        )
        title2 = str(lecture2)
        DBSession.add(lecture2)

    resp = app.get("/lectures/")

    assert resp.status_code == 200
    assert resp.content_type == "text/html"
    assert title in resp.text
    assert title2 in resp.text
    assert resp.parser.css("tbody a")[0].text() == title2
    assert resp.parser.css("tbody a")[1].text() == title
