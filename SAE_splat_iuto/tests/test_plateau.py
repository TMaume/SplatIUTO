import pytest
from bot_ia import plateau
  
plateau1=  "4;6\n"+\
        "#  b# \n"+\
        "  A## \n"+\
        "##A   \n"+\
        "  Aa##\n"+\
        "2\nA;1;1\nB;3;1\n"+\
        "0\n"

plateau2=  "20;16\n"+\
        "b   #AA##   #AA#\n"+\
        "b## #CABBB# #CA#\n"+\
        "#C EE ###  EE ##\n"+\
        "#   #AA##   #AA#\n"+\
        "#   #AA##   #AA#\n"+\
        "#   #AA##   #AA#\n"+\
        "#   #AA##   #AA#\n"+\
        "#   #AA##   #AA#\n"+\
        "#   #AA##   #AA#\n"+\
        "#   #AA##   #AA#\n"+\
        "#   #AA##   #AA#\n"+\
        "#cc #CA BB# #CA#\n"+\
        "#   EE###   EE##\n"+\
        "#   #AA##   #AA#\n"+\
        "#   #AA##   #AA#\n"+\
        "#   #AA##   #AA#\n"+\
        "#   #AA##   #AA#\n"+\
        "#   #AA##   #AA#\n"+\
        "#   #AA##   #AA#\n"+\
        "#   #AA##   #AA#\n"+\
        "5\nA;0;1\nB;18;1\nC;17;1\nD;10;13\nE;2;2\n"+\
        "3\n1;0;2\n3;18;5\n4;10;11\n"



def test_directions_possibles():
    p1=plateau.Plateau(plateau1)
    assert plateau.directions_possibles(p1,(0,1)) == {'S':' ','E':' '}
    assert plateau.directions_possibles(p1,(0,2)) == {'S':'A','O':' '}
    assert plateau.directions_possibles(p1,(1,2)) == {'N':' ','S':'A','O':' '}
    assert plateau.directions_possibles(p1,(2,5)) == {'N':' ','O':' '}


def test_joueurs_direction():
    p1=plateau.Plateau(plateau1)
    assert plateau.nb_joueurs_direction(p1, (0,1), 'N', 3) == 0
    assert plateau.nb_joueurs_direction(p1, (0,1), 'S', 3) == 1
    assert plateau.nb_joueurs_direction(p1, (0,1), 'O', 3) == 0
    assert plateau.nb_joueurs_direction(p1, (0,1), 'E', 3) == 0
    assert plateau.nb_joueurs_direction(p1, (3,2), 'N', 3) == 0
    assert plateau.nb_joueurs_direction(p1, (3,2), 'S', 3) == 0
    assert plateau.nb_joueurs_direction(p1, (3,2), 'O', 3) == 1
    assert plateau.nb_joueurs_direction(p1, (3,2), 'E', 3) == 0
    p2=plateau.Plateau(plateau2)
    assert plateau.nb_joueurs_direction(p2, (2,1), 'N', 10) == 0
    assert plateau.nb_joueurs_direction(p2, (2,1), 'S', 10) == 0
    assert plateau.nb_joueurs_direction(p2, (2,1), 'O', 10) == 0
    assert plateau.nb_joueurs_direction(p2, (2,1), 'E', 10) == 1

    assert plateau.nb_joueurs_direction(p2, (9,1), 'N', 10) == 0
    assert plateau.nb_joueurs_direction(p2, (9,1), 'S', 10) == 0
    assert plateau.nb_joueurs_direction(p2, (9,1), 'O', 10) == 0
    assert plateau.nb_joueurs_direction(p2, (9,1), 'E', 10) == 0
    
    assert plateau.nb_joueurs_direction(p2, (12,1), 'N', 10) == 0
    assert plateau.nb_joueurs_direction(p2, (12,1), 'S', 10) == 2
    assert plateau.nb_joueurs_direction(p2, (12,1), 'O', 10) == 0
    assert plateau.nb_joueurs_direction(p2, (12,1), 'E', 10) == 0

    assert plateau.nb_joueurs_direction(p2, (10,13), 'N', 10) == 1
    assert plateau.nb_joueurs_direction(p2, (10,13), 'S', 10) == 1
    assert plateau.nb_joueurs_direction(p2, (10,13), 'O', 10) == 1
    assert plateau.nb_joueurs_direction(p2, (10,13), 'E', 10) == 1

def test_surfaces_peintes():
    p1=plateau.Plateau(plateau1)
    assert plateau.surfaces_peintes(p1,2) == {'A':4,'B':1}
    p2=plateau.Plateau(plateau2)
    assert plateau.surfaces_peintes(p2,5) == {'A':68,'B': 7, 'C': 7, 'D': 0, 'E': 8}

def test_distances_objets_joueurs():
    p1=plateau.Plateau(plateau1)
    assert plateau.distances_objets_joueurs(p1,(1,2),5) == {1:{'A'},3:{'B'}}
    assert plateau.distances_objets_joueurs(p1,(1,5),5) == {}
    assert plateau.distances_objets_joueurs(p1,(1,5),10) == {6:{'A','B'}}
    
    p2=plateau.Plateau(plateau2)
    assert plateau.distances_objets_joueurs(p2,(8,9),20) == {4: {4}, 10: {'D'}, 14: {3}, 15: {'E'}, 17: {1, 'C'}, 18: {'A', 'B'}}
    assert plateau.distances_objets_joueurs(p2,(0,0),20) == {1: {'A'}, 2: {1}, 6: {'E'}}
    assert plateau.distances_objets_joueurs(p2,(17,1),10) == {0: {'C'}, 1: {'B'}}
