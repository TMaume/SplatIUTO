# coding: utf-8
"""
Projet Splat'IUT'O

Licence pédagogique — usage académique uniquement                                                    
Copyright (c) 2026 Limet Sébastien / IUT'O, Université d'Orléans

Ce code est fourni exclusivement dans un cadre pédagogique.
Les étudiants sont autorisés à l’utiliser et le modifier uniquement
pour les besoins du projet évalué dans le cadre de la SAE1.02 du BUT Informatique d'Orléans.

Toute diffusion, publication ou réutilisation en dehors de ce cadre,
notamment sur des plateformes publiques, est interdite sans
autorisation écrite préalable de l’auteur.

Tous droits réservés.

Module contenant l'implémentation de l'IA et le programme principal du joueur
"""

import argparse

from bot_ia import case
from bot_ia import client
from bot_ia import const
from bot_ia import innondation
from bot_ia import joueur
from bot_ia import plateau


VIDE = ' '
RIEN = 'X'

DIRS_ORDRE = ("N", "E", "S", "O")

def get_voisin_safe(le_plateau, pos, direction):
    """Récupère la couleur de la case voisine, si elle est accessible.

    Args:
        le_plateau (dict): plateau de jeu.
        pos (tuple[int, int]): position (ligne, colonne).
        direction (str): direction parmi 'N', 'E', 'S', 'O'.

    Returns:
        str | None: couleur de la case voisine, ou None si hors plateau / mur.
    """
    d_lig, d_col = plateau.INC_DIRECTION[direction]
    pos_voisin = (pos[0] + d_lig, pos[1] + d_col)
    if plateau.est_sur_plateau(le_plateau, pos_voisin):
        c = plateau.get_case(le_plateau, pos_voisin)
        if not case.est_mur(c):
            return case.get_couleur(c)
    return None


def innondation_direction(resultat):
    """Extrait la première direction depuis un résultat d'inondation.

    Args:
        resultat (dict): dictionnaire retourné par innondation.Innondation.

    Returns:
        str | None: direction ('N'/'E'/'S'/'O') vers la cible la plus proche, sinon None.
    """
    if not resultat:
        return None
    cle_min = min(resultat, key=lambda k: k[0])
    direction = resultat[cle_min].get('Direction')
    return direction or None


def random_direction_from_voisins(voisins):
    """Choisit une direction déterministe parmi les voisins disponibles.

    Args:
        voisins (dict): dict {direction: couleur_case_arrivee}.

    Returns:
        str: direction choisie, ou 'X' si aucune direction.
    """
    if not voisins:
        return RIEN
    for d in DIRS_ORDRE:
        if d in voisins:
            return d
    return next(iter(voisins), RIEN)


def case_couleur(le_plateau, pos):
    """Retourne la couleur de la case à une position donnée.

    Args:
        le_plateau (dict): plateau de jeu.
        pos (tuple[int, int]): position (ligne, colonne).

    Returns:
        str: couleur de la case.
    """
    return case.get_couleur(plateau.get_case(le_plateau, pos))


def a_voisin_de_couleur(voisins, couleur):
    """Indique s'il existe un voisin immédiat d'une couleur donnée.

    Args:
        voisins (dict): dict {direction: couleur_case_arrivee}.
        couleur (str): couleur recherchée.

    Returns:
        str | None: direction vers un voisin de cette couleur, sinon None.
    """
    for d in DIRS_ORDRE:
        if voisins.get(d) == couleur:
            return d
    return None


def direction_vers_couleur(le_plateau, pos, distance_max, couleur):
    """Cherche une direction menant à une couleur cible dans un rayon.

    Args:
        le_plateau (dict): plateau de jeu.
        pos (tuple[int, int]): position de départ.
        distance_max (int): portée de recherche.
        couleur (str): couleur cible (peut être ' ').

    Returns:
        str | None: direction initiale, sinon None.
    """
    res = innondation.Innondation(le_plateau, pos, distance_max, recherche='C', C_cherche=couleur)
    return innondation_direction(res)


def direction_vers_objet(le_plateau, pos, distance_max, objet):
    """Cherche une direction menant à un objet cible dans un rayon.

    Args:
        le_plateau (dict): plateau de jeu.
        pos (tuple[int, int]): position de départ.
        distance_max (int): portée de recherche.
        objet (int): identifiant de l'objet cible.

    Returns:
        str | None: direction initiale, sinon None.
    """
    res = innondation.Innondation(le_plateau, pos, distance_max, recherche='O', O_cherche=objet)
    return innondation_direction(res)


def direction_vers_zone_deux_cases(le_plateau, pos, distance_max, couleur):
    """Cherche une zone de 2 cases adjacentes de la même couleur.

    Args:
        le_plateau (dict): plateau de jeu.
        pos (tuple[int, int]): position de départ.
        distance_max (int): portée de recherche.
        couleur (str): couleur recherchée.

    Returns:
        str | None: direction initiale vers une cible appartenant à une paire, sinon None.
    """
    res = innondation.Innondation(le_plateau, pos, distance_max, recherche='C', C_cherche=couleur)
    if not res:
        return None

    for dist, pos_cible in sorted(res.keys(), key=lambda k: (k[0], k[1][0], k[1][1])):
        voisins_cible = plateau.directions_possibles(le_plateau, pos_cible)
        if a_voisin_de_couleur(voisins_cible, couleur):
            return res[(dist, pos_cible)].get('Direction') or None
    return None


def meilleure_direction_locale(voisins, ma_couleur):
    """Choisit localement une direction stable (vide -> couleur -> autre).

    Args:
        voisins (dict): dict {direction: couleur_case_arrivee}.
        ma_couleur (str): couleur du joueur.

    Returns:
        str: direction choisie, ou 'X'.
    """
    if not voisins:
        return RIEN
    for d in DIRS_ORDRE:
        if voisins.get(d) == VIDE:
            return d
    for d in DIRS_ORDRE:
        if voisins.get(d) == ma_couleur:
            return d
    return random_direction_from_voisins(voisins)


def tir_sur_case_non_ami(voisins, ma_couleur):
    """Choisit une direction de tir locale sur une case non alliée.

    Args:
        voisins (dict): dict {direction: couleur_case_arrivee}.
        ma_couleur (str): couleur du joueur.

    Returns:
        str: direction de tir, ou 'X' si aucune cible locale.
    """
    for d in DIRS_ORDRE:
        if d in voisins and voisins[d] != ma_couleur:
            return d
    return RIEN

def deplacement_peinture_zero(notre_IA, le_plateau, distance_max, reserve):
    """Gère le déplacement lorsque la réserve est très faible (recharge/retour).

    Args:
        notre_IA (dict): joueur.
        le_plateau (dict): plateau.
        distance_max (int): portée de recherche.
        reserve (int): réserve actuelle.

    Returns:
        tuple[str, str]: (direction_deplacement, direction_tir).
    """
    ma_couleur = joueur.get_couleur(notre_IA)
    ma_pos = joueur.get_pos(notre_IA)
    voisins = plateau.directions_possibles(le_plateau, ma_pos)

    if case_couleur(le_plateau, ma_pos) == ma_couleur:
        d_pair = a_voisin_de_couleur(voisins, ma_couleur)
        if d_pair:
            return d_pair, RIEN

    direction = direction_vers_zone_deux_cases(le_plateau, ma_pos, distance_max, ma_couleur)
    if direction:
        tir = direction if reserve > 0 and voisins.get(direction) != ma_couleur else RIEN
        return direction, tir

    direction = direction_vers_objet(le_plateau, ma_pos, distance_max, const.BIDON)
    if direction:
        tir = direction if reserve > 0 and voisins.get(direction) != ma_couleur else RIEN
        return direction, tir

    direction = direction_vers_couleur(le_plateau, ma_pos, distance_max, ma_couleur)
    if direction:
        tir = direction if reserve > 0 and voisins.get(direction) != ma_couleur else RIEN
        return direction, tir

    direction = meilleure_direction_locale(voisins, ma_couleur)
    tir = direction if reserve > 0 and voisins.get(direction) != ma_couleur else RIEN
    return direction, tir

def deplacement_peinture_negative(notre_IA, le_plateau, distance_max):
    """Cherche un bidon lorsque la réserve est négative.

    Args:
        notre_IA (dict): joueur.
        le_plateau (dict): plateau.
        distance_max (int): portée de recherche.

    Returns:
        tuple[str, str]: (direction_deplacement, direction_tir).
    """
    ma_pos = joueur.get_pos(notre_IA)
    direction = direction_vers_objet(le_plateau, ma_pos, distance_max, const.BIDON)
    if direction:
        return direction, RIEN
    
    voisins = plateau.directions_possibles(le_plateau, ma_pos)
    ma_couleur = joueur.get_couleur(notre_IA)
    direction = meilleure_direction_locale(voisins, ma_couleur)
    tir = RIEN
    if direction != RIEN and voisins.get(direction) != ma_couleur:
        tir = direction
    return direction, tir

def deplacement_vers_objet(notre_IA, le_plateau, distance_max):
    """Se déplace vers l'objet le plus proche et ajuste le tir si besoin.

    Args:
        notre_IA (dict): joueur.
        le_plateau (dict): plateau.
        distance_max (int): portée de recherche.

    Returns:
        tuple[str, str] | None: (direction_deplacement, direction_tir) ou None.
    """
    ma_pos = joueur.get_pos(notre_IA)
    ma_coul = joueur.get_couleur(notre_IA)
    
    resultat = innondation.Innondation(le_plateau, ma_pos, distance_max, recherche='O')
    direction = innondation_direction(resultat)
    if direction:
        dir_tir = RIEN
        couleur_voisin = get_voisin_safe(le_plateau, ma_pos, direction)
        if couleur_voisin is not None and couleur_voisin != ma_coul:
            dir_tir = direction
        return direction, dir_tir
    return None


def deplacement_vers_autre(notre_IA, le_plateau, distance_max):
    """Se déplace pour continuer à peindre: vide -> ennemi -> notre couleur.

    Args:
        notre_IA (dict): joueur.
        le_plateau (dict): plateau.
        distance_max (int): portée de recherche.

    Returns:
        tuple[str, str]: (direction_deplacement, direction_tir).
    """
    ma_pos = joueur.get_pos(notre_IA)
    ma_couleur = joueur.get_couleur(notre_IA)
    dirTir = RIEN
    
    voisins_possibles = plateau.directions_possibles(le_plateau, ma_pos)
    
    if not voisins_possibles:
        return RIEN, RIEN

    direction = direction_vers_couleur(le_plateau, ma_pos, distance_max, VIDE)
    if not direction:
        res_ennemi = innondation.Innondation(le_plateau, ma_pos, distance_max, recherche='A', C_cherche=ma_couleur)
        direction = innondation_direction(res_ennemi)
    if not direction:
        direction = direction_vers_couleur(le_plateau, ma_pos, distance_max, ma_couleur)

    if direction:
        d_lig, d_col = plateau.INC_DIRECTION[direction]
        pos_suivante = (ma_pos[0] + d_lig, ma_pos[1] + d_col)
        couleur_case_visee = case.get_couleur(plateau.get_case(le_plateau, pos_suivante))
        if couleur_case_visee != ma_couleur:
            dirTir = direction
        return direction, dirTir
    
    direction = meilleure_direction_locale(voisins_possibles, ma_couleur)
    tir = RIEN
    if direction != RIEN and voisins_possibles.get(direction) != ma_couleur:
        tir = direction
    return direction, tir


def direction_tir_ennemi(notre_IA, le_plateau):
    """Choisit la meilleure direction de tir vers des ennemis à portée.

    Args:
        notre_IA (dict): joueur.
        le_plateau (dict): plateau.

    Returns:
        str: direction de tir, ou 'X' si aucune cible.
    """
    ma_pos = joueur.get_pos(notre_IA)
    meilleure_dir = RIEN
    max_ennemis = 0
    
    for direction in "NESO":
        nb = plateau.nb_joueurs_direction(le_plateau, ma_pos, direction, const.PORTEE_PEINTURE)
        if nb > max_ennemis:
            max_ennemis = nb
            meilleure_dir = direction
            
    return meilleure_dir


def tirer_sur_mur(notre_IA, le_plateau):
    """Détecte un mur à portée pour le pistolet et retourne une direction.

    Args:
        notre_IA (dict): joueur.
        le_plateau (dict): plateau.

    Returns:
        str | None: direction à tirer, ou None si aucun mur (ou pas de pistolet).
    """
    if joueur.get_objet(notre_IA) != const.PISTOLET:
        return None

    portee = 5
    ma_lig, ma_col = joueur.get_pos(notre_IA) 
    directions = plateau.INC_DIRECTION

    for sens, (d_lig, d_col) in directions.items():
        if sens == RIEN:
            continue

        for i in range(1, portee + 1):
            cible = (ma_lig + d_lig * i, ma_col + d_col * i)
            if not plateau.est_sur_plateau(le_plateau, cible):
                break
                
            la_case = plateau.get_case(le_plateau, cible) 
            if case.est_mur(la_case): 
                return sens 
                
    return None

def mon_IA(ma_couleur, carac_jeu, le_plateau, les_joueurs):
    """ Cette fonction permet de calculer les deux actions du joueur de couleur ma_couleur
        en fonction de l'état du jeu décrit par les paramètres. 
        Le premier caractère est parmi XSNOE X indique pas de peinture et les autres
        caractères indique la direction où peindre (Nord, Sud, Est ou Ouest)
        Le deuxième caractère est parmi SNOE indiquant la direction où se déplacer.

    Args:
        ma_couleur (str): un caractère en majuscule indiquant la couleur du joueur
        carac_jeu (dict)): un dictionnaire donnant les valeurs des caractéristiques du jeu:
             duree_actuelle, duree_totale, reserve_initiale, duree_obj, penalite, bonus_touche,
             bonus_recharge, bonus_objet et distance_max,
        le_plateau (dict): l'état du plateau actuel sous la forme décrite dans plateau.py
        les_joueurs (list[joueur]): la liste des joueurs avec leurs caractéristiques utilisant l'API
         joueur.py

    Returns:
        str: une chaine de deux caractères en majuscules indiquant la direction de peinture
            et la direction de déplacement
    """
    
    notre_IA = les_joueurs[ma_couleur]
    deplacement = RIEN
    tir = RIEN

    reserve = joueur.get_reserve(notre_IA)
    objet_tenu = joueur.get_objet(notre_IA)

    ma_pos = joueur.get_pos(notre_IA)
    voisins = plateau.directions_possibles(le_plateau, ma_pos)

    if case_couleur(le_plateau, ma_pos) != ma_couleur:
        direction = direction_vers_couleur(le_plateau, ma_pos, 28, ma_couleur)
        if direction:
            deplacement = direction
            tir = direction if reserve > 0 else RIEN
        else:
            deplacement = meilleure_direction_locale(voisins, ma_couleur)
            tir = tir_sur_case_non_ami(voisins, ma_couleur) if reserve > 0 else RIEN

    elif 0 <= reserve < 2:
        deplacement, tir = deplacement_peinture_zero(notre_IA, le_plateau, 28, reserve)
            
    elif reserve < 0:
        deplacement, tir = deplacement_peinture_negative(notre_IA, le_plateau, 28)
            
    else:
        tir_mur = tirer_sur_mur(notre_IA, le_plateau)
        if tir_mur:
            tir = tir_mur
            deplacement = meilleure_direction_locale(voisins, ma_couleur)
        
        elif objet_tenu == 0:
            res_obj = deplacement_vers_objet(notre_IA, le_plateau, 5)
            if res_obj:
                deplacement, tir = res_obj
            else:
                deplacement, tir = deplacement_vers_autre(notre_IA, le_plateau, 28)
        
        else:
             deplacement, tir = deplacement_vers_autre(notre_IA, le_plateau, 28)

        if tir == RIEN:
            tir_ennemi = direction_tir_ennemi(notre_IA, le_plateau)
            if tir_ennemi != RIEN:
                tir = tir_ennemi
            else:
                tir = tir_sur_case_non_ami(voisins, ma_couleur)

    return tir + deplacement




if __name__ == "__main__":
    noms_caracteristiques = [
        "duree_actuelle",
        "duree_totale",
        "reserve_initiale",
        "duree_obj",
        "penalite",
        "bonus_touche",
        "bonus_recharge",
        "bonus_objet",
        "distance_max",
    ]
    parser = argparse.ArgumentParser()
    parser.add_argument("--equipe", dest="nom_equipe", help="nom de l'équipe", type=str, default='Non fournie')
    parser.add_argument("--serveur", dest="serveur", help="serveur de jeu", type=str, default='localhost')
    parser.add_argument("--port", dest="port", help="port de connexion", type=int, default=1111)
    
    args = parser.parse_args()
    le_client = client.ClientCyber()
    le_client.creer_socket(args.serveur, args.port)
    le_client.enregistrement(args.nom_equipe, "joueur")
    ok = True
    while ok:
        ok, id_joueur, le_jeu = le_client.prochaine_commande()
        if ok:
            val_carac_jeu, etat_plateau, les_joueurs = le_jeu.split("--------------------\n")

            joueurs = {}
            for ligne in les_joueurs.strip().splitlines():
                le_joueur = joueur.joueur_from_str(ligne)
                joueurs[joueur.get_couleur(le_joueur)] = le_joueur

            le_plateau = plateau.Plateau(etat_plateau)
            val_carac = val_carac_jeu.split(";")
            carac_jeu = {k: int(v) for k, v in zip(noms_caracteristiques, val_carac)}

            actions_joueur = mon_IA(id_joueur, carac_jeu, le_plateau, joueurs)
            le_client.envoyer_commande_client(actions_joueur)
    le_client.afficher_msg("terminé")

