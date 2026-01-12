from bot_ia import const
from bot_ia import joueur

chaine1="A;15;28;150;0;0;12;25;le peintre"
chaine2="B;-8;12;-147;1;3;6;4;iut'o"
chaine3="C;14;0;5230;2;1;23;1;splash"
chaine4="D;15;0;230;2;1;23;1;splash"

def test_joueur():
    le_joueur=joueur.Joueur('A',"test1",10,5,150,(12,47),1,3)
    assert joueur.get_couleur(le_joueur) == 'A'
    assert joueur.get_nom(le_joueur) == 'test1'
    assert joueur.get_reserve(le_joueur) == 10
    assert joueur.get_surface(le_joueur) == 5 
    assert joueur.get_points(le_joueur) == 150
    assert joueur.get_pos(le_joueur) == (12,47)
    assert joueur.get_objet(le_joueur) == 1
    assert joueur.get_duree(le_joueur) == 3

    le_joueur=joueur.Joueur('B',"test2",-8,45,587,(7,22),0,0)
    assert joueur.get_couleur(le_joueur) == 'B'
    assert joueur.get_nom(le_joueur) == 'test2'
    assert joueur.get_reserve(le_joueur) == -8
    assert joueur.get_surface(le_joueur) == 45
    assert joueur.get_points(le_joueur) == 587
    assert joueur.get_pos(le_joueur) == (7,22)
    assert joueur.get_objet(le_joueur) == 0
    assert joueur.get_duree(le_joueur) == 0

def test_joueur_from_str():
    le_joueur=joueur.joueur_from_str(chaine1)
    assert joueur.get_couleur(le_joueur) == 'A'
    assert joueur.get_nom(le_joueur) == 'le peintre'
    assert joueur.get_reserve(le_joueur) == 15
    assert joueur.get_surface(le_joueur) == 28
    assert joueur.get_points(le_joueur) == 150
    assert joueur.get_pos(le_joueur) == (12,25)
    assert joueur.get_objet(le_joueur) == 0
    assert joueur.get_duree(le_joueur) == 0

    le_joueur=joueur.joueur_from_str(chaine2)
    assert joueur.get_couleur(le_joueur) == 'B'
    assert joueur.get_nom(le_joueur) == "iut'o"
    assert joueur.get_reserve(le_joueur) == -8
    assert joueur.get_surface(le_joueur) == 12
    assert joueur.get_points(le_joueur) == -147
    assert joueur.get_pos(le_joueur) == (6,4)
    assert joueur.get_objet(le_joueur) == 1
    assert joueur.get_duree(le_joueur) == 3

    le_joueur=joueur.joueur_from_str(chaine3)
    assert joueur.get_couleur(le_joueur) == 'C'
    assert joueur.get_nom(le_joueur) == "splash"
    assert joueur.get_reserve(le_joueur) == 14
    assert joueur.get_surface(le_joueur) == 0
    assert joueur.get_points(le_joueur) == 5230
    assert joueur.get_pos(le_joueur) == (23,1)
    assert joueur.get_objet(le_joueur) == 2
    assert joueur.get_duree(le_joueur) == 1

def test_modifier_reserve():
    le_joueur=joueur.joueur_from_str(chaine1)
    assert joueur.modifie_reserve(le_joueur,10) == const.CAPACITE_RESERVOIR
    assert joueur.get_reserve(le_joueur) == const.CAPACITE_RESERVOIR

    le_joueur=joueur.joueur_from_str(chaine2)
    assert joueur.modifie_reserve(le_joueur,10) == 2
    assert joueur.get_reserve(le_joueur) == 2

    le_joueur=joueur.joueur_from_str(chaine3)
    assert joueur.modifie_reserve(le_joueur,-20) == -6
    assert joueur.get_reserve(le_joueur) == -6

def test_ajouter_objet():
    le_joueur=joueur.joueur_from_str(chaine1)
    joueur.ajouter_objet(le_joueur,const.BOMBE)
    assert joueur.get_objet(le_joueur) == const.BOMBE
    assert joueur.get_duree(le_joueur) == const.DUREE_VIE_OBJET
    assert joueur.get_reserve(le_joueur) == 15
    
    le_joueur=joueur.joueur_from_str(chaine2)
    joueur.ajouter_objet(le_joueur,const.BIDON)
    assert joueur.get_objet(le_joueur) == 1
    assert joueur.get_duree(le_joueur) == 3
    assert joueur.get_reserve(le_joueur) == 0
    
    le_joueur=joueur.joueur_from_str(chaine3)
    joueur.ajouter_objet(le_joueur,const.BIDON)
    assert joueur.get_objet(le_joueur) == 2
    assert joueur.get_duree(le_joueur) == 1
    assert joueur.get_reserve(le_joueur) == 14

    le_joueur=joueur.joueur_from_str(chaine3)
    joueur.ajouter_objet(le_joueur,const.BOUCLIER)
    assert joueur.get_objet(le_joueur) == const.BOUCLIER
    assert joueur.get_duree(le_joueur)== const.DUREE_VIE_OBJET
    assert joueur.get_reserve(le_joueur) == 14

def test_maj_duree():
    le_joueur=joueur.joueur_from_str(chaine1)
    joueur.maj_duree(le_joueur)
    assert joueur.get_objet(le_joueur) == const.AUCUN
    assert joueur.get_duree(le_joueur) == 0
    
    le_joueur=joueur.joueur_from_str(chaine2)
    joueur.maj_duree(le_joueur)
    assert joueur.get_objet(le_joueur) == 1
    assert joueur.get_duree(le_joueur) == 2

    le_joueur=joueur.joueur_from_str(chaine3)
    joueur.maj_duree(le_joueur)
    assert joueur.get_objet(le_joueur) == const.AUCUN
    assert joueur.get_duree(le_joueur) == 0

def test_classement_joueurs():
    j1=joueur.joueur_from_str(chaine1)
    j2=joueur.joueur_from_str(chaine2)
    j3=joueur.joueur_from_str(chaine3)
    j4=joueur.joueur_from_str(chaine4)
    
    liste_joueurs=[j1,j2,j3,j4]
    assert joueur.classement_joueurs(liste_joueurs,"points") == [j3,j4,j1,j2]
    liste_joueurs=[j1,j2,j3,j4]
    assert joueur.classement_joueurs(liste_joueurs,"surface") == [j1,j2,j4,j3]
    liste_joueurs=[j4,j3,j2,j1]
    assert joueur.classement_joueurs(liste_joueurs,"points") == [j3,j4,j1,j2]
    liste_joueurs=[j4,j3,j2,j1]
    assert joueur.classement_joueurs(liste_joueurs,"surface") == [j1,j2,j4,j3]
