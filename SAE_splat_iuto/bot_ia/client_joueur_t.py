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

from bot_ia  import client
from bot_ia  import const
from bot_ia  import plateau
from bot_ia  import case
from bot_ia  import joueur
from bot_ia  import innondation

# -------------------------------------------------------------------------
#                         FONCTIONS UTILITAIRES
# -------------------------------------------------------------------------

def _get_voisin_safe(le_plateau, pos, direction):
    """Renvoie la couleur du voisin dans la direction donnée, ou None si impossible"""
    inc = plateau.INC_DIRECTION[direction]
    pos_voisin = (pos[0] + inc[0], pos[1] + inc[1])
    if plateau.est_sur_plateau(le_plateau, pos_voisin):
        c = plateau.get_case(le_plateau, pos_voisin)
        if not case.est_mur(c):
            return case.get_couleur(c)
    return None

def _deplacement_peinture_zero(notre_IA, le_plateau, distance_max):
    """Cherche la case de notre couleur la plus proche et y va."""
    ma_couleur = joueur.get_couleur(notre_IA)
    ma_pos = joueur.get_pos(notre_IA)
    resultat = innondation.Innondation(le_plateau, ma_pos, distance_max, recherche='C', C_cherche=ma_couleur)
    
    if resultat:
        cle_min = min(resultat.keys(), key=lambda k: k[0])
        info = resultat[cle_min]
        if 'Direction' in info and info['Direction']:
            return info['Direction'], 'X'
            
    voisins = plateau.directions_possibles(le_plateau, ma_pos)
    choix_vides = [d for d, c in voisins.items() if c == ' ']
    if choix_vides: return random.choice(choix_vides), 'X'
    if voisins: return random.choice(list(voisins.keys())), 'X'
    return 'X', 'X'

def _deplacement_peinture_negative(notre_IA, le_plateau, distance_max):
    """Cherche un bidon pour recharger."""
    ma_pos = joueur.get_pos(notre_IA)
    resultat = innondation.Innondation(le_plateau, ma_pos, distance_max, recherche='O', O_cherche=const.BIDON)
    
    if resultat:
        cle_min = min(resultat.keys(), key=lambda k: k[0])
        info = resultat[cle_min]
        if 'Direction' in info and info['Direction']:
            return info['Direction'], 'X'
    
    # Si pas de bidon, on bouge au hasard
    vals = list(plateau.directions_possibles(le_plateau, ma_pos).keys())
    if vals: return random.choice(vals), 'X'
    return 'X', 'X'

def _deplacement_vers_objet(notre_IA, le_plateau, distance_max):
    """Cherche l'objet le plus proche."""
    ma_pos = joueur.get_pos(notre_IA)
    ma_coul = joueur.get_couleur(notre_IA)
    
    resultat = innondation.Innondation(le_plateau, ma_pos, distance_max, recherche='O')
    
    if resultat:
        cle_min = min(resultat.keys(), key=lambda k: k[0])
        info = resultat[cle_min]
        
        if 'Direction' in info and info['Direction']:
            best_dir = info['Direction']
            dirTir = 'X'
            # On tire si on va sur une case ennemie
            couleur_voisin = _get_voisin_safe(le_plateau, ma_pos, best_dir)
            if couleur_voisin is not None and couleur_voisin != ma_coul:
                dirTir = best_dir
            return best_dir, dirTir
    return None


def _deplacement_vers_vide_custom(notre_IA, le_plateau, distance_max):
    """
    Cherche à s'orienter vers une zone vide (non peinte).
    Retourne (direction_deplacement, direction_tir)
    """
    ma_pos = joueur.get_pos(notre_IA)
    ma_couleur = joueur.get_couleur(notre_IA) # Correction: variable manquante
    dirTir = 'X'
    
    voisins_possibles = plateau.directions_possibles(le_plateau, ma_pos)
    
    if not voisins_possibles:
        # Bloqué ? On tente un mouvement au hasard
        return random.choice("NSEO"), 'X'

    meilleure_direction = None
    min_distance_trouvee = distance_max + 1

    # On simule un départ depuis chaque voisin pour voir lequel est le plus proche du vide
    for direction in voisins_possibles:
        inc = plateau.INC_DIRECTION[direction]
        pos_voisin = (ma_pos[0] + inc[0], ma_pos[1] + inc[1])

        # On lance l'inondation depuis le voisin
        resultat = innondation.Innondation(le_plateau, pos_voisin, distance_max - 1, recherche='C', C_cherche=' ')
        
        if resultat:
            # On cherche la distance minimale dans les résultats
            dist_min_scan = min(cle[0] for cle in resultat.keys())
            
            if dist_min_scan < min_distance_trouvee:
                min_distance_trouvee = dist_min_scan
                meilleure_direction = direction
                
                # Correction logique tir : si la case immédiate n'est pas à nous, on la peint
                couleur_case_visée = plateau.get_case(le_plateau, pos_voisin).get_couleur()
                if couleur_case_visée != ma_couleur:
                    dirTir = direction

    if meilleure_direction:
        return meilleure_direction, dirTir
    
    # Si rien trouvé, on prend une direction possible au hasard
    return random.choice(list(voisins_possibles.keys())), 'X'


def _direction_tir_ennemi(notre_IA, le_plateau):
    """
    Renvoie la direction où il y a le plus d'ennemis à portée.
    Renvoie 'X' si personne.
    """
    ma_pos = joueur.get_pos(notre_IA)
    # On utilise la fonction du plateau qui compte les joueurs
    # Attention: nb_joueurs_direction renvoie un nombre, on cherche le max
    
    meilleure_dir = 'X'
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

    portee = 5 # Portée améliorée du pistolet ou standard
    ma_lig, ma_col = joueur.get_pos(notre_IA) 
    directions = plateau.INC_DIRECTION 

    for sens, (d_lig, d_col) in directions.items():
        if sens == 'X': continue 

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
    deplacement = 'X'
    tir = 'X'

    reserve = joueur.get_reserve(notre_IA)
    objet_tenu = joueur.get_objet(notre_IA)

    # 1. URGENCE : Plus de peinture ?
    if 0 <= reserve <= 5: 
        res = _deplacement_peinture_zero(notre_IA, le_plateau, 25)
        if res: deplacement, tir = res
            
    # 2. PENALITE : Réserve négative ?
    elif reserve < 0: 
        res = _deplacement_peinture_negative(notre_IA, le_plateau, 25)
        if res: deplacement, tir = res
            
    # 3. COMBAT / STRATEGIE OBJET
    else:
        # A. Si on a le PISTOLET, on regarde si on peut peindre un mur (stratégie spécifique)
        tir_mur = _tirer_sur_mur(notre_IA, le_plateau)
        if tir_mur:
            tir = tir_mur
            # On essaie de bouger quand même
            vals = list(plateau.directions_possibles(le_plateau, joueur.get_pos(notre_IA)).keys())
            if vals: deplacement = random.choice(vals)
        
        # B. Sinon, on cherche d'abord un objet si on n'en a pas
        elif objet_tenu == 0:
            res_obj = _deplacement_vers_objet(notre_IA, le_plateau, 28)
            if res_obj:
                deplacement, tir = res_obj
            else:
                # Pas d'objet proche, on cherche le vide avec votre fonction custom
                deplacement, tir = _deplacement_vers_vide_custom(notre_IA, le_plateau, 28)
        
        # C. On a un objet (autre que pistolet utilisé) ou pas d'objet trouvé
        else:
             # On se déplace vers le vide
             deplacement, tir = _deplacement_vers_vide_custom(notre_IA, le_plateau, 28)

        # D. SURCHARGE TIR : Si on n'a pas prévu de tirer pour peindre le sol ('X'), 
        # on regarde si on peut tirer sur un ennemi
        if tir == 'X':
            tir_ennemi = _direction_tir_ennemi(notre_IA, le_plateau)
            if tir_ennemi != 'X':
                tir = tir_ennemi

    # 4. RETOUR AU SERVEUR (TIR + DEPLACEMENT)
    return tir + deplacement
    # IA complètement aléatoire
    # return random.choice("XNSOE")+random.choice("NSEO")





if __name__=="__main__":
    noms_caracteristiques=["duree_actuelle","duree_totale","reserve_initiale","duree_obj","penalite","bonus_touche",
            "bonus_recharge","bonus_objet","distance_max"]
    parser = argparse.ArgumentParser()  
    parser.add_argument("--equipe", dest="nom_equipe", help="nom de l'équipe", type=str, default='Non fournie')
    parser.add_argument("--serveur", dest="serveur", help="serveur de jeu", type=str, default='localhost')
    parser.add_argument("--port", dest="port", help="port de connexion", type=int, default=1111)
    
    args = parser.parse_args()
    le_client=client.ClientCyber()
    le_client.creer_socket(args.serveur,args.port)
    le_client.enregistrement(args.nom_equipe,"joueur")
    ok=True
    while ok:
        ok,id_joueur,le_jeu=le_client.prochaine_commande()
        if ok:
            val_carac_jeu,etat_plateau,les_joueurs=le_jeu.split("--------------------\n")
            joueurs={}
            for ligne in les_joueurs[:-1].split('\n'):
                lejoueur=joueur.joueur_from_str(ligne)
                joueurs[joueur.get_couleur(lejoueur)]=lejoueur
            le_plateau=plateau.Plateau(etat_plateau)
            val_carac=val_carac_jeu.split(";")
            carac_jeu={}
            for i in range(len(noms_caracteristiques)):
                carac_jeu[noms_caracteristiques[i]]=int(val_carac[i])
    
            actions_joueur=mon_IA(id_joueur,carac_jeu,le_plateau,joueurs)
            le_client.envoyer_commande_client(actions_joueur)
            # le_client.afficher_msg("sa reponse  envoyée "+str(id_joueur)+args.nom_equipe)
    le_client.afficher_msg("terminé")
