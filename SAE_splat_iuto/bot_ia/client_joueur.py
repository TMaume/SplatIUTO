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

# -------------------------------------------------------------------------
#                         FONCTIONS UTILITAIRES
# -------------------------------------------------------------------------

def _get_voisin_safe(le_plateau, pos, direction):
    """Renvoie la couleur du voisin dans la direction donnée, ou None si impossible"""
    d_lig, d_col = plateau.INC_DIRECTION[direction]
    pos_voisin = (pos[0] + d_lig, pos[1] + d_col)
    if plateau.est_sur_plateau(le_plateau, pos_voisin):
        c = plateau.get_case(le_plateau, pos_voisin)
        if not case.est_mur(c):
            return case.get_couleur(c)
    return None


def _innondation_direction(resultat):
    """Extrait la direction du résultat d'Innondation (ou None)."""
    if not resultat:
        return None
    cle_min = min(resultat, key=lambda k: k[0])
    direction = resultat[cle_min].get('Direction')
    return direction or None


def _random_direction_from_voisins(voisins):
    """Retourne une direction déterministe parmi les clés d'un dict, ou 'X' si vide."""
    if not voisins:
        return RIEN
    for d in DIRS_ORDRE:
        if d in voisins:
            return d
    # Fallback (ordre des clés si dictionnaire inattendu)
    return next(iter(voisins), RIEN)


def _direction_vers_couleur(le_plateau, pos, distance_max, couleur):
    """Retourne une direction vers la couleur cible (ou None)."""
    res = innondation.Innondation(le_plateau, pos, distance_max, recherche='C', C_cherche=couleur)
    return _innondation_direction(res)


def _direction_vers_objet(le_plateau, pos, distance_max, objet):
    """Retourne une direction vers l'objet cible (ou None)."""
    res = innondation.Innondation(le_plateau, pos, distance_max, recherche='O', O_cherche=objet)
    return _innondation_direction(res)


def _meilleure_direction_locale(voisins, ma_couleur):
    """Choix local robuste: vide -> ma couleur -> autre -> 'X'."""
    if not voisins:
        return RIEN
    # 1) Aller vers le vide
    for d in DIRS_ORDRE:
        if voisins.get(d) == VIDE:
            return d
    # 2) Revenir sur notre couleur
    for d in DIRS_ORDRE:
        if voisins.get(d) == ma_couleur:
            return d
    # 3) Sinon, première direction valide
    return _random_direction_from_voisins(voisins)


def _tir_local_sur_case_non_ami(voisins, ma_couleur):
    """Si un voisin immédiat est vide/ennemi, peindre dans cette direction."""
    for d in DIRS_ORDRE:
        if d in voisins and voisins[d] != ma_couleur:
            return d
    return RIEN

def _deplacement_peinture_zero(notre_IA, le_plateau, distance_max):
    """Cherche la case de notre couleur la plus proche et y va."""
    ma_couleur = joueur.get_couleur(notre_IA)
    ma_pos = joueur.get_pos(notre_IA)
    direction = _direction_vers_couleur(le_plateau, ma_pos, distance_max, ma_couleur)
    if direction:
        return direction, RIEN
            
    voisins = plateau.directions_possibles(le_plateau, ma_pos)
    direction = _meilleure_direction_locale(voisins, ma_couleur)
    tir = RIEN
    if direction != RIEN and voisins.get(direction) != ma_couleur:
        tir = direction
    return direction, tir

def _deplacement_peinture_negative(notre_IA, le_plateau, distance_max):
    """Cherche un bidon pour recharger."""
    ma_pos = joueur.get_pos(notre_IA)
    direction = _direction_vers_objet(le_plateau, ma_pos, distance_max, const.BIDON)
    if direction:
        return direction, RIEN
    
    # Si pas de bidon, on se stabilise: vide -> notre couleur -> autre
    voisins = plateau.directions_possibles(le_plateau, ma_pos)
    ma_couleur = joueur.get_couleur(notre_IA)
    direction = _meilleure_direction_locale(voisins, ma_couleur)
    tir = RIEN
    if direction != RIEN and voisins.get(direction) != ma_couleur:
        tir = direction
    return direction, tir

def _deplacement_vers_objet(notre_IA, le_plateau, distance_max):
    """Cherche l'objet le plus proche."""
    ma_pos = joueur.get_pos(notre_IA)
    ma_coul = joueur.get_couleur(notre_IA)
    
    resultat = innondation.Innondation(le_plateau, ma_pos, distance_max, recherche='O')
    direction = _innondation_direction(resultat)
    if direction:
        dir_tir = RIEN
        # On tire si on va sur une case ennemie
        couleur_voisin = _get_voisin_safe(le_plateau, ma_pos, direction)
        if couleur_voisin is not None and couleur_voisin != ma_coul:
            dir_tir = direction
        return direction, dir_tir
    return None


def _deplacement_vers_vide_custom(notre_IA, le_plateau, distance_max):
    """
    Cherche à s'orienter vers une zone vide (non peinte).
    Retourne (direction_deplacement, direction_tir)
    """
    ma_pos = joueur.get_pos(notre_IA)
    ma_couleur = joueur.get_couleur(notre_IA)
    dirTir = RIEN
    
    voisins_possibles = plateau.directions_possibles(le_plateau, ma_pos)
    
    if not voisins_possibles:
        # Bloqué
        return RIEN, RIEN

    # Priorité 1: rejoindre du vide
    direction = _direction_vers_couleur(le_plateau, ma_pos, distance_max, VIDE)
    if not direction:
        # Priorité 2: se remettre sur notre couleur (évite la "panique" hors zone)
        direction = _direction_vers_couleur(le_plateau, ma_pos, distance_max, ma_couleur)

    if direction:
        d_lig, d_col = plateau.INC_DIRECTION[direction]
        pos_suivante = (ma_pos[0] + d_lig, ma_pos[1] + d_col)
        couleur_case_visee = case.get_couleur(plateau.get_case(le_plateau, pos_suivante))
        if couleur_case_visee != ma_couleur:
            dirTir = direction
        return direction, dirTir
    
    # Si rien trouvé (rare), choix local robuste
    direction = _meilleure_direction_locale(voisins_possibles, ma_couleur)
    tir = RIEN
    if direction != RIEN and voisins_possibles.get(direction) != ma_couleur:
        tir = direction
    return direction, tir


def _direction_tir_ennemi(notre_IA, le_plateau):
    """
    Renvoie la direction où il y a le plus d'ennemis à portée.
    Renvoie 'X' si personne.
    """
    ma_pos = joueur.get_pos(notre_IA)
    # On utilise la fonction du plateau qui compte les joueurs
    # Attention: nb_joueurs_direction renvoie un nombre, on cherche le max
    
    meilleure_dir = RIEN
    max_ennemis = 0
    
    for direction in "NESO":
        # nb_joueurs_direction semble exister dans plateau.py d'après votre code
        nb = plateau.nb_joueurs_direction(le_plateau, ma_pos, direction, const.PORTEE_PEINTURE)
        if nb > max_ennemis:
            max_ennemis = nb
            meilleure_dir = direction
            
    return meilleure_dir


def _tirer_sur_mur(notre_IA, le_plateau):
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
    # On ne fait ça que si on a le pistolet (seul objet qui perce/peint les murs efficacement)
    if joueur.get_objet(notre_IA) != const.PISTOLET:
        return None

    portee = 5  # Portée améliorée du pistolet ou standard
    ma_lig, ma_col = joueur.get_pos(notre_IA) 
    directions = plateau.INC_DIRECTION

    for sens, (d_lig, d_col) in directions.items():
        if sens == RIEN:
            continue

        # On regarde dans la direction
        for i in range(1, portee + 1):
            cible = (ma_lig + d_lig * i, ma_col + d_col * i)
            if not plateau.est_sur_plateau(le_plateau, cible):
                break
                
            la_case = plateau.get_case(le_plateau, cible) 
            # Si c'est un mur, c'est une cible valide pour le pistolet
            if case.est_mur(la_case): 
                return sens 
                
    return None

# -------------------------------------------------------------------------
#                            IA PRINCIPALE
# -------------------------------------------------------------------------

def mon_IA(ma_couleur, carac_jeu, le_plateau, les_joueurs):
    """
    Logique principale de l'IA
    """
    notre_IA = les_joueurs[ma_couleur]
    deplacement = RIEN
    tir = RIEN

    reserve = joueur.get_reserve(notre_IA)
    objet_tenu = joueur.get_objet(notre_IA)

    ma_pos = joueur.get_pos(notre_IA)
    voisins = plateau.directions_possibles(le_plateau, ma_pos)

    # 0. Stabilisation immédiate: si on n'est pas sur notre couleur, on essaie d'y revenir
    if case.get_couleur(plateau.get_case(le_plateau, ma_pos)) != ma_couleur:
        direction = _direction_vers_couleur(le_plateau, ma_pos, 25, ma_couleur)
        if direction:
            deplacement = direction
            tir = direction  # on repeint en avançant
        else:
            deplacement = _meilleure_direction_locale(voisins, ma_couleur)
            tir = _tir_local_sur_case_non_ami(voisins, ma_couleur)

    # 1. URGENCE : Plus de peinture ?
    elif 0 <= reserve < 2:
        deplacement, tir = _deplacement_peinture_zero(notre_IA, le_plateau, 25)
            
    # 2. PENALITE : Réserve négative ?
    elif reserve < 0:
        deplacement, tir = _deplacement_peinture_negative(notre_IA, le_plateau, 25)
            
    # 3. COMBAT / STRATEGIE OBJET
    else:
        # A. Si on a le PISTOLET, on regarde si on peut peindre un mur (stratégie spécifique)
        tir_mur = _tirer_sur_mur(notre_IA, le_plateau)
        if tir_mur:
            tir = tir_mur
            # On essaie de bouger quand même
            deplacement = _meilleure_direction_locale(voisins, ma_couleur)
        
        # B. Sinon, on cherche d'abord un objet si on n'en a pas
        elif objet_tenu == 0:
            res_obj = _deplacement_vers_objet(notre_IA, le_plateau, 28)
            if res_obj:
                deplacement, tir = res_obj
            else:
                # Pas d'objet proche: on prend le contrôle du terrain
                deplacement, tir = _deplacement_vers_vide_custom(notre_IA, le_plateau, 28)
        
        # C. On a un objet (autre que pistolet utilisé) ou pas d'objet trouvé
        else:
             # On se déplace vers le vide
             deplacement, tir = _deplacement_vers_vide_custom(notre_IA, le_plateau, 28)

        # D. SURCHARGE TIR : Si on n'a pas prévu de tirer pour peindre le sol ('X'), 
        # on regarde si on peut tirer sur un ennemi
        if tir == RIEN:
            tir_ennemi = _direction_tir_ennemi(notre_IA, le_plateau)
            if tir_ennemi != RIEN:
                tir = tir_ennemi
            else:
                # Sinon, peindre localement une case non-ami (vide/ennemie)
                tir = _tir_local_sur_case_non_ami(voisins, ma_couleur)

    # 4. RETOUR AU SERVEUR (TIR + DEPLACEMENT)
    return tir + deplacement
    # IA complètement aléatoire
    # return random.choice("XNSOE")+random.choice("NSEO")




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
            # le_client.afficher_msg("sa reponse  envoyée "+str(id_joueur)+args.nom_equipe)
    le_client.afficher_msg("terminé")

