def test_get_dossiers():
    from zam_repondeur.data import get_data

    dossiers = get_data("dossiers")

    assert "DLR5L15N36030" in dossiers


def test_get_organes():
    from zam_repondeur.data import get_data

    organes = get_data("organes")

    assert "PO717460" in organes
