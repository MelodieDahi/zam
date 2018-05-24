def test_num_int():
    from zam_aspirateur.amendements.models import Amendement
    amendement = Amendement(
        article="Article 1",
        alinea="",
        num="230 rect.",
        auteur="M. Dupont",
    )
    assert amendement.num_int == 230
