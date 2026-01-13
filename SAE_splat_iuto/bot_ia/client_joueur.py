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
    
    # Appel optimisé : 1 seul scan depuis notre position
    resultat = innondation.Innondation(le_plateau, ma_pos, distance_max, recherche='C', C_cherche=ma_couleur)
    
    if resultat:
        # Trouver la cible la plus proche
        cle_min = min(resultat.keys(), key=lambda k: k[0])
        info = resultat[cle_min]
        # Innondation nous donne maintenant la direction de départ !
        if 'Direction' in info and info['Direction']:
            return info['Direction'], 'X'
            
    # Fallback : mouvement aléatoire vers une case vide si possible
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

    voisins = plateau.directions_possibles(le_plateau, ma_pos)
    choix_safe = [d for d, c in voisins.items() if c == ' ']
    if choix_safe: return random.choice(choix_safe), 'X'
    if voisins: return random.choice(list(voisins.keys())), 'X'
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
            
            # Logique de tir : si la case où je vais n'est pas à moi, je peins
            couleur_voisin = _get_voisin_safe(le_plateau, ma_pos, best_dir)
            if couleur_voisin is not None and couleur_voisin != ma_coul:
                dirTir = best_dir
            else:
                # Sinon tir opportuniste
                dirTir = max(plateau.INC_DIRECTION, key=lambda d: plateau.nb_joueurs_direction(le_plateau, ma_pos, d, const.PORTEE_PEINTURE))
                
            return best_dir, dirTir

    # Fallback
    voisins = list(plateau.directions_possibles(le_plateau, ma_pos).keys())
    if voisins: return random.choice(voisins), 'X'
    return 'X', 'X'

def _deplacement_vers_vide(notre_IA, le_plateau, distance_max):
    """Cherche une case non peinte."""
    ma_pos = joueur.get_pos(notre_IA)
    ma_coul = joueur.get_couleur(notre_IA)
    
    resultat = innondation.Innondation(le_plateau, ma_pos, distance_max, recherche='C', C_cherche=' ')
    
    if resultat:
        cle_min = min(resultat.keys(), key=lambda k: k[0])
        info = resultat[cle_min]
        
        if 'Direction' in info and info['Direction']:
            best_dir = info['Direction']
            dirTir = 'X'
            
            # Si le chemin est bloqué par une couleur adverse, on tire
            couleur_voisin = _get_voisin_safe(le_plateau, ma_pos, best_dir)
            if couleur_voisin is not None and couleur_voisin != ma_coul:
                dirTir = best_dir
                
            return best_dir, dirTir
            
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
    deplacement = 'X'
    tir = 'X'

    reserve = joueur.get_reserve(notre_IA)
    objet_tenu = joueur.get_objet(notre_IA)

    # Choix de l'action
    if reserve == 0: 
        deplacement, tir = _deplacement_peinture_zero(notre_IA, le_plateau, 5)
    elif reserve < 0: 
        deplacement, tir = _deplacement_peinture_negative(notre_IA, le_plateau, 5)
    elif objet_tenu == 0:  
        result = _deplacement_vers_objet(notre_IA, le_plateau, 5)
        if result: 
             deplacement, tir = result
        else:
             # Si pas d'objet, on cherche du vide
             result_vide = _deplacement_vers_vide(notre_IA, le_plateau, 5)
             if result_vide:
                 deplacement, tir = result_vide
             else:
                 vals = list(plateau.directions_possibles(le_plateau, joueur.get_pos(notre_IA)).keys())
                 if vals: deplacement = random.choice(vals)
    else:
        # On a un objet et de la réserve
        vals = list(plateau.directions_possibles(le_plateau, joueur.get_pos(notre_IA)).keys())
        if vals: deplacement = random.choice(vals)
        
    return deplacement, tir

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
