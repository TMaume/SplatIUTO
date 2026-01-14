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
import random

from bot_ia import case
from bot_ia import client
from bot_ia import const
from bot_ia import innondation
from bot_ia import joueur
from bot_ia import plateau


VIDE = ' '
RIEN = 'X'
DIRS_ORDRE = ("N", "E", "S", "O")


def distance_max_plateau(le_plateau):
    """Calcule une borne supérieure pour la distance de recherche sur le plateau.
    
    Args:
        le_plateau (dict): Le plateau de jeu.
        
    Returns:
        int: Le nombre total de cases du plateau.
    """
    return plateau.get_nb_lignes(le_plateau) * plateau.get_nb_colonnes(le_plateau)

def get_voisin_safe(le_plateau, pos, direction):
    """Récupère la couleur de la case voisine dans une direction donnée, si elle est accessible.

    Args:
        le_plateau (dict): Le plateau de jeu.
        pos (tuple[int, int]): La position actuelle (ligne, colonne).
        direction (str): La direction ('N', 'E', 'S', 'O').

    Returns:
        str | None: La couleur de la case voisine si elle existe et n'est pas un mur, sinon None.
    """
    d_lig, d_col = plateau.INC_DIRECTION[direction]
    pos_voisin = (pos[0] + d_lig, pos[1] + d_col)
    if plateau.est_sur_plateau(le_plateau, pos_voisin):
        c = plateau.get_case(le_plateau, pos_voisin)
        if not case.est_mur(c):
            return case.get_couleur(c)
    return None


def innondation_direction(resultat):
    """Extrait la première direction à prendre depuis le résultat d'une inondation.

    Args:
        resultat (dict): Le dictionnaire retourné par innondation.Innondation.

    Returns:
        str | None: La direction vers la cible la plus proche, ou None si aucun résultat.
    """
    if not resultat:
        return None
    cle_min = min(resultat, key=lambda k: k[0])
    direction = resultat[cle_min].get('Direction')
    return direction or None


def random_direction_from_voisins(voisins):
    """Choisit une direction disponible parmi les voisins de manière déterministe (ordre fixe).

    Args:
        voisins (dict): Dictionnaire {direction: couleur_case}.

    Returns:
        str: La direction choisie, ou 'X' si aucune direction n'est possible.
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
        le_plateau (dict): Le plateau de jeu.
        pos (tuple[int, int]): La position (ligne, colonne).

    Returns:
        str: La couleur de la case (ex: 'A', 'B', ' ').
    """
    return case.get_couleur(plateau.get_case(le_plateau, pos))


def a_voisin_de_couleur(voisins, couleur):
    """Vérifie si un des voisins immédiats est de la couleur spécifiée.

    Args:
        voisins (dict): Dictionnaire des voisins accessibles {direction: couleur}.
        couleur (str): La couleur recherchée.

    Returns:
        str | None: La direction du premier voisin trouvé de cette couleur, ou None.
    """
    for d in DIRS_ORDRE:
        if voisins.get(d) == couleur:
            return d
    return None


def direction_vers_couleur(le_plateau, pos, distance_max, couleur):
    """Cherche le chemin le plus court vers une case d'une certaine couleur.

    Args:
        le_plateau (dict): Le plateau de jeu.
        pos (tuple[int, int]): La position de départ.
        distance_max (int): La distance maximale de recherche.
        couleur (str): La couleur cible.

    Returns:
        str | None: La direction à prendre, ou None si introuvable.
    """
    res = innondation.Innondation(le_plateau, pos, distance_max, recherche='C', C_cherche=couleur, arret_premier=True)
    return innondation_direction(res)


def direction_vers_objet(le_plateau, pos, distance_max, objet):
    """Cherche le chemin le plus court vers un type d'objet donné.

    Args:
        le_plateau (dict): Le plateau de jeu.
        pos (tuple[int, int]): La position de départ.
        distance_max (int): La distance maximale de recherche.
        objet (int): L'identifiant de l'objet (ex: const.BIDON).

    Returns:
        str | None: La direction à prendre, ou None si introuvable.
    """
    res = innondation.Innondation(le_plateau, pos, distance_max, recherche='O', O_cherche=objet, arret_premier=True)
    return innondation_direction(res)


def direction_vers_securite_absolue(le_plateau, pos, distance_max, couleur):
    """Cherche une zone de recharge sûre (cluster) de manière exhaustive.
    
    Cette fonction scanne toutes les cases de notre couleur et sélectionne la plus proche
    qui possède elle-même un voisin de notre couleur. Cela garantit qu'on se dirige vers
    une zone où on pourra osciller ("bon ping-pong") sans risque.

    Args:
        le_plateau (dict): Le plateau de jeu.
        pos (tuple[int, int]): La position de départ.
        distance_max (int): La distance maximale de recherche.
        couleur (str): La couleur recherchée (celle du joueur).

    Returns:
        str | None: La direction vers cette zone, ou None (auquel cas on visera une case isolée).
    """
    res = innondation.Innondation(le_plateau, pos, distance_max, recherche='C', C_cherche=couleur, arret_premier=False)
    
    if not res:
        return None

    candidats_tries = sorted(res.keys(), key=lambda k: k[0])

    for dist, pos_candidat in candidats_tries:
        voisins_candidat = plateau.directions_possibles(le_plateau, pos_candidat)
        
        if a_voisin_de_couleur(voisins_candidat, couleur):
            return res[(dist, pos_candidat)].get('Direction')

    premier_candidat = candidats_tries[0]
    return res[premier_candidat].get('Direction')


def meilleure_direction_locale(voisins, ma_couleur):
    """Choisit la meilleure direction immédiate selon une heuristique simple.
    Ordre de préférence : Case vide > Ma couleur > Au hasard.

    Args:
        voisins (dict): Dictionnaire des voisins.
        ma_couleur (str): La couleur du joueur.

    Returns:
        str: La direction choisie.
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
    """Détermine s'il faut tirer sur une case voisine immédiate.

    Args:
        voisins (dict): Dictionnaire des voisins.
        ma_couleur (str): La couleur du joueur.

    Returns:
        str: La direction de tir, ou 'X' si inutile.
    """
    for d in DIRS_ORDRE:
        if d in voisins and voisins[d] != ma_couleur:
            return d
    return RIEN


def deplacement_peinture_zero(notre_IA, le_plateau, distance_max, reserve):
    """Gère la stratégie de survie lorsque la réserve de peinture est critique (0-2).
    
    Cherche en priorité à rejoindre ou rester dans un cluster sûr.

    Args:
        notre_IA (dict): Le joueur.
        le_plateau (dict): Le plateau.
        distance_max (int): Portée de recherche.
        reserve (int): Niveau de réserve actuel.

    Returns:
        tuple[str, str]: (Direction déplacement, Direction tir).
    """
    ma_couleur = joueur.get_couleur(notre_IA)
    ma_pos = joueur.get_pos(notre_IA)
    voisins = plateau.directions_possibles(le_plateau, ma_pos)

    if case_couleur(le_plateau, ma_pos) == ma_couleur:
        d_pair = a_voisin_de_couleur(voisins, ma_couleur)
        if d_pair:
            return d_pair, RIEN

    direction = direction_vers_securite_absolue(le_plateau, ma_pos, distance_max, ma_couleur)
    
    if direction:
        tir = direction if reserve > 0 and voisins.get(direction) != ma_couleur else RIEN
        return direction, tir

    direction = direction_vers_objet(le_plateau, ma_pos, distance_max_plateau(le_plateau), const.BIDON)
    if direction:
        tir = direction if reserve > 0 and voisins.get(direction) != ma_couleur else RIEN
        return direction, tir
    
    direction = meilleure_direction_locale(voisins, ma_couleur)
    tir = direction if reserve > 0 and voisins.get(direction) != ma_couleur else RIEN
    return direction, tir


def deplacement_peinture_negative(notre_IA, le_plateau, distance_max):
    """Gère la stratégie de pénalité (réserve négative).
    Objectif unique : trouver un bidon.

    Args:
        notre_IA (dict): Le joueur.
        le_plateau (dict): Le plateau.
        distance_max (int): Portée de recherche.

    Returns:
        tuple[str, str]: (Direction déplacement, Direction tir).
    """
    ma_pos = joueur.get_pos(notre_IA)
    direction = direction_vers_objet(le_plateau, ma_pos, distance_max_plateau(le_plateau), const.BIDON)
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
    """Cherche l'objet le plus proche.

    Args:
        notre_IA (dict): Le joueur.
        le_plateau (dict): Le plateau.
        distance_max (int): Portée.

    Returns:
        tuple[str, str] | None.
    """
    ma_pos = joueur.get_pos(notre_IA)
    ma_coul = joueur.get_couleur(notre_IA)
    
    resultat = innondation.Innondation(le_plateau, ma_pos, distance_max, recherche='O', arret_premier=True)
    direction = innondation_direction(resultat)
    if direction:
        dir_tir = RIEN
        couleur_voisin = get_voisin_safe(le_plateau, ma_pos, direction)
        if couleur_voisin is not None and couleur_voisin != ma_coul:
            dir_tir = direction
        return direction, dir_tir
    return None


def deplacement_vers_autre(notre_IA, le_plateau, distance_max):
    """Stratégie d'expansion : Vide > Ennemi > Couleur ami.

    Args:
        notre_IA (dict): Le joueur.
        le_plateau (dict): Le plateau.
        distance_max (int): Portée.

    Returns:
        tuple[str, str]: (Direction, Tir).
    """
    ma_pos = joueur.get_pos(notre_IA)
    ma_couleur = joueur.get_couleur(notre_IA)
    dirTir = RIEN
    
    voisins_possibles = plateau.directions_possibles(le_plateau, ma_pos)
    
    if not voisins_possibles:
        return RIEN, RIEN

    direction = direction_vers_couleur(le_plateau, ma_pos, distance_max, VIDE)
    
    if not direction:
        res_ennemi = innondation.Innondation(le_plateau, ma_pos, distance_max, recherche='A', C_cherche=ma_couleur, arret_premier=True)
        direction = innondation_direction(res_ennemi)
        
    if not direction:
        direction = direction_vers_couleur(le_plateau, ma_pos, distance_max, ma_couleur)

    if direction:
        d_lig, d_col = plateau.INC_DIRECTION[direction]
        pos_suivante = (ma_pos[0] + d_lig, ma_pos[1] + d_col)
        if plateau.est_sur_plateau(le_plateau, pos_suivante):
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
    """Cherche la meilleure direction pour toucher des ennemis."""
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
    """Cherche un mur à peindre avec le pistolet."""
    if joueur.get_objet(notre_IA) != const.PISTOLET:
        return None
    portee = 5
    ma_lig, ma_col = joueur.get_pos(notre_IA) 
    directions = plateau.INC_DIRECTION
    for sens, (d_lig, d_col) in directions.items():
        if sens == RIEN: continue
        for i in range(1, portee + 1):
            cible = (ma_lig + d_lig * i, ma_col + d_col * i)
            if not plateau.est_sur_plateau(le_plateau, cible): break
            la_case = plateau.get_case(le_plateau, cible) 
            if case.est_mur(la_case): return sens 
    return None


def mon_IA(ma_couleur, carac_jeu, le_plateau, les_joueurs):
    """Cerveau de l'IA.
    
    Logique des priorités :
    1. RECHARGE EXPRESS : Si on est sur notre couleur et qu'on a un voisin ami, on reste dessus jusqu'à 5 pts.
    2. RECHARGE URGENCE (Retour) : Si on n'est pas sur notre couleur, on rentre au cluster le plus sûr.
    3. SURVIE : Si réserve < 2, on cherche cluster ou bidon.
    4. ACTION : Si tout va bien, on peint, on cherche des objets, on attaque.
    """
    notre_IA = les_joueurs[ma_couleur]
    deplacement = RIEN
    tir = RIEN

    reserve = joueur.get_reserve(notre_IA)
    objet_tenu = joueur.get_objet(notre_IA)

    ma_pos = joueur.get_pos(notre_IA)
    voisins = plateau.directions_possibles(le_plateau, ma_pos)

    if case_couleur(le_plateau, ma_pos) == ma_couleur:
        d_allie = a_voisin_de_couleur(voisins, ma_couleur)
        
        if d_allie:
            if reserve < 5:
                return RIEN + d_allie

    if case_couleur(le_plateau, ma_pos) != ma_couleur:
        direction = direction_vers_securite_absolue(le_plateau, ma_pos, 50, ma_couleur)
        if direction:
            deplacement = direction
            tir = direction if reserve > 0 else RIEN
        else:
            deplacement = meilleure_direction_locale(voisins, ma_couleur)
            tir = tir_sur_case_non_ami(voisins, ma_couleur) if reserve > 0 else RIEN

    elif 0 <= reserve < 2:
        deplacement, tir = deplacement_peinture_zero(notre_IA, le_plateau, 50, reserve)
            
    elif reserve < 0:
        deplacement, tir = deplacement_peinture_negative(notre_IA, le_plateau, 50)
            
    else:
        tir_mur = tirer_sur_mur(notre_IA, le_plateau)
        if tir_mur:
            tir = tir_mur
            deplacement = meilleure_direction_locale(voisins, ma_couleur)
        elif objet_tenu == 0:
            res_obj = deplacement_vers_objet(notre_IA, le_plateau, 10)
            if res_obj:
                deplacement, tir = res_obj
            else:
                deplacement, tir = deplacement_vers_autre(notre_IA, le_plateau, 30)
        else:
             deplacement, tir = deplacement_vers_autre(notre_IA, le_plateau, 30)

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

