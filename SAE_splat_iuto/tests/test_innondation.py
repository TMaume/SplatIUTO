from bot_ia import innondation
from bot_ia import plateau


plateau1 = (
    "4;6\n"
    "#  b# \n"
    "  A## \n"
    "##A   \n"
    "  Aa##\n"
    "2\nA;1;1\nB;3;1\n"
    "0\n"
)


def test_innondation_cible_couleur_vide():
    p1 = plateau.Plateau(plateau1)
    # Depuis une case peinte, on doit pouvoir trouver une case vide (' ')
    res = innondation.Innondation(p1, (1, 2), 10, recherche='C', C_cherche=' ')
    assert isinstance(res, dict)
    assert res  # non vide
    # Les entrées doivent indiquer une direction N/E/S/O
    directions = {info.get('Direction') for info in res.values()}
    assert directions.intersection({'N', 'E', 'S', 'O'})


def test_innondation_recherche_none_ne_plante_pas():
    p1 = plateau.Plateau(plateau1)
    res = innondation.Innondation(p1, (0, 1), 3, recherche=None)
    assert isinstance(res, dict)
