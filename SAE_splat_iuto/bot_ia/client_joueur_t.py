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

def evaluer_action(notre_IA, le_plateau, les_joueurs, dir_move, dir_shoot, carac_jeu, direction_suggeree=None):
    score = 0
    ma_pos = joueur.get_pos(notre_IA)
    ma_couleur = joueur.get_couleur(notre_IA)
    reserve = joueur.get_reserve(notre_IA)
    
    inc_move = plateau.INC_DIRECTION[dir_move]
    pos_arrivee = (ma_pos[0] + inc_move[0], ma_pos[1] + inc_move[1])
    
    if not plateau.est_sur_plateau(le_plateau, pos_arrivee):
        return -10000

    case_arrivee = plateau.get_case(le_plateau, pos_arrivee)
    
    if case.est_mur(case_arrivee):
        return -10000

    coul_arrivee = case.get_couleur(case_arrivee)
    
    if coul_arrivee == ma_couleur:
        score += carac_jeu["bonus_recharge"]
    elif coul_arrivee == ' ':
        score -= 1
    else:
        score -= carac_jeu["penalite"]
        if reserve < 5:
            score -= 100

    contenu_arrivee = case.get_objet(case_arrivee)
    if contenu_arrivee != 0:
        score += 50
        if contenu_arrivee == const.PISTOLET:
            score += 30

    if direction_suggeree and dir_move == direction_suggeree:
        score += 40

    cout_tir = 0
    gain_potentiel = 0
    
    if dir_shoot != 'X':
        inc_shoot = plateau.INC_DIRECTION[dir_shoot]
        pos_cible = (ma_pos[0] + inc_shoot[0], ma_pos[1] + inc_shoot[1])
        
        if plateau.est_sur_plateau(le_plateau, pos_cible):
            case_cible = plateau.get_case(le_plateau, pos_cible)
            
            if case.est_mur(case_cible) and joueur.get_objet(notre_IA) != const.PISTOLET:
                score -= 10
            else:
                coul_cible = case.get_couleur(case_cible)
                
                if coul_cible != ma_couleur and coul_cible != ' ':
                    cout_tir = 2
                else:
                    cout_tir = 1
                
                if coul_cible != ma_couleur:
                    gain_potentiel += 5
                
                for id_j, j in les_joueurs.items():
                    if joueur.get_pos(j) == pos_cible and id_j != ma_couleur:
                        if joueur.get_reserve(j) > 0:
                            gain_potentiel += carac_jeu["bonus_touche"] * 2

    if dir_shoot == dir_move and dir_shoot != 'X':
        score += 15
        cout_tir = 0

    if reserve - cout_tir < 0:
        score -= 500
    
    score += (gain_potentiel - cout_tir)
    
    return score

def choisir_meilleur_tir(notre_IA, le_plateau, les_joueurs, direction_move, carac_jeu):
    ma_pos = joueur.get_pos(notre_IA)
    ma_couleur = joueur.get_couleur(notre_IA)
    reserve = joueur.get_reserve(notre_IA)
    objet = joueur.get_objet(notre_IA)
    
    # --- REGLE 1 : MODE SURVIE (Pour éviter le bot à 1k) ---
    # Si on a moins de 5 unités, on INTERDIT tout tir qui n'est pas un "Tapis Rouge"
    if reserve < 5:
        if direction_move != 'X':
            return direction_move # On tire là où on marche pour gagner +2 net
        return 'X' # Sinon on ne tire pas

    meilleur_tir = 'X'
    meilleur_score_tir = -1
    possibilites_tir = list("NSEO")

    for d_tir in possibilites_tir:
        score = 0
        inc_tir = plateau.INC_DIRECTION[d_tir]
        pos_visée = (ma_pos[0] + inc_tir[0], ma_pos[1] + inc_tir[1])
        
        # Hors plateau ? Next.
        if not plateau.est_sur_plateau(le_plateau, pos_visée): continue
            
        case_visée = plateau.get_case(le_plateau, pos_visée)
        
        # --- REGLE 2 : UTILISATION INTELLIGENTE DES OBJETS ---
        # Si on a le PISTOLET, les murs valent de l'or (points sécurisés)
        if objet == const.PISTOLET and case.est_mur(case_visée):
            score += 2000 
            
        # --- REGLE 3 : CHASSE AUX ENNEMIS RICHES ---
        elif not case.est_mur(case_visée):
            ennemi_detecte = False
            for j in les_joueurs.values():
                if joueur.get_pos(j) == pos_visée and joueur.get_couleur(j) != ma_couleur:
                    ennemi_detecte = True
                    # On tire SEULEMENT si l'ennemi a de la peinture (Rentable)
                    if joueur.get_reserve(j) > 2: 
                        score += 1000 # Priorité absolue sur le vol
                    elif joueur.get_reserve(j) == 0:
                        score -= 50 # Gâchis de munitions sur un mec vide
            
            # --- REGLE 4 : PEINTURE DE ZONE (Rentabilité) ---
            if not ennemi_detecte:
                # On simule la ligne de peinture
                cases_vides_touchees = 0
                cases_ennemies_touchees = 0
                cout = 0
                portee = carac_jeu['distance_max'] if objet == const.PISTOLET else 5
                
                curr_pos = pos_visée
                for k in range(portee):
                    if not plateau.est_sur_plateau(le_plateau, curr_pos): break
                    c_case = plateau.get_case(le_plateau, curr_pos)
                    
                    if case.est_mur(c_case): break 
                    
                    coul_c = case.get_couleur(c_case)
                    if coul_c != ma_couleur:
                        if coul_c == ' ':
                            cases_vides_touchees += 1
                            cout += 1
                        else:
                            cases_ennemies_touchees += 1
                            cout += 2
                    else:
                        cout += 1 # Repeindre sa couleur coûte 1
                        
                    curr_pos = (curr_pos[0] + inc_tir[0], curr_pos[1] + inc_tir[1])
                
                gain_points = (cases_vides_touchees * 1) + (cases_ennemies_touchees * 1)
                
                # FORMULE MAGIQUE DU SCORE
                # On veut peindre beaucoup pour peu cher.
                if reserve > 15:
                    # On est riche : on vise le max de points brut
                    score += gain_points * 10 
                else:
                    # On est moyen (5-15) : on vise la rentabilité stricte
                    ratio = gain_points - cout
                    score += ratio * 20

        # Bonus Tapis Rouge (Toujours bon à prendre)
        if d_tir == direction_move:
            score += 50 # Gros bonus pour inciter à recharger en marchant

        if score > meilleur_score_tir:
            meilleur_score_tir = score
            meilleur_tir = d_tir
            
    # Sécurité finale : Si le meilleur tir n'est pas terrible et qu'on n'est pas riche
    if meilleur_score_tir <= 0:
        return 'X'
        
    return meilleur_tir
# -------------------------------------------------------------------------
#                            IA PRINCIPALE
# -------------------------------------------------------------------------

def mon_IA(ma_couleur, carac_jeu, le_plateau, les_joueurs):
    notre_IA = les_joueurs[ma_couleur]
    reserve = joueur.get_reserve(notre_IA)
    objet_tenu = joueur.get_objet(notre_IA)
    pos = joueur.get_pos(notre_IA)
    
    dir_move = 'X'
    
    # --- PHASE 1 : SURVIE (Inchangé, c'est vital) ---
    if reserve == 0:
        res = _deplacement_peinture_zero(notre_IA, le_plateau, 30)
        if res: return res[1] + res[0]
    elif reserve < 5: # On a monté le seuil de sécurité à 5 pour éviter le crash
        res = _deplacement_peinture_negative(notre_IA, le_plateau, 30)
        if res: return res[1] + res[0] # Priorité absolue à la recharge

    # --- PHASE 2 : SELECTION INTELLIGENTE DE LA CIBLE ---
    else:
        found_move = False
        
        # A. MODE "ARCHITECTE" : Si on a le PISTOLET, on cherche les MURS
        # C'est ce qui fait passer de 10k à 15k points.
        if objet_tenu == const.PISTOLET:
            # On cherche le mur non peint le plus proche (Mur = Case non franchissable)
            # Astuce : On utilise votre innondation pour trouver un mur
            # Note : Il faut adapter légèrement si votre inondation ne cherche que des cases traversables.
            # Sinon, on utilise une heuristique simple : aller vers les bords ou les obstacles.
            
            # Ici, on tente de trouver un mur à portée de tir
            res_mur = innondation.Innondation(le_plateau, pos, 20, recherche='C', C_cherche='%') # '%' souvent utilisé pour mur, vérifiez votre case.py
            # Si inondation ne gère pas les murs, on scanne simplement autour
            meilleur_mur_dir = None
            min_dist = 999
            
            # Scan manuel des murs proches si inondation échoue
            for d, inc in plateau.INC_DIRECTION.items():
                if d == 'X': continue
                curr = pos
                for k in range(1, 10): # Regarde à 10 cases
                    curr = (curr[0] + inc[0], curr[1] + inc[1])
                    if not plateau.est_sur_plateau(le_plateau, curr): break
                    c = plateau.get_case(le_plateau, curr)
                    if case.est_mur(c):
                        # Si le mur n'est pas à nous
                        if case.get_couleur(c) != ma_couleur:
                            meilleur_mur_dir = d
                            found_move = True
                        break
            
            if meilleur_mur_dir:
                dir_move = meilleur_mur_dir
                found_move = True

        # B. MODE "CHAROGNARD" : Si pas d'objet, on en veut un ABSOLUMENT
        if not found_move and objet_tenu == 0:
            res_obj = _deplacement_vers_objet(notre_IA, le_plateau, 50) # On cherche loin
            if res_obj:
                dir_move = res_obj[0]
                found_move = True
        
        # C. MODE "CONQUERANT" : Chercher la plus grosse zone à peindre
        # Au lieu de chercher juste du vide, on cherche aussi l'ennemi si on a de la peinture
        if not found_move:
            type_recherche = ' ' # Par défaut on cherche le vide
            
            # Si on est riche (>15), on attaque les zones ennemies (ça rapporte double)
            if reserve > 15:
                # Idéalement, il faudrait une fonction qui cherche la couleur majoritaire adverse
                # Pour simplifier, on alterne ou on cherche le vide si pas d'ennemi proche
                pass 

            res_zone = _deplacement_vers_vide_custom(notre_IA, le_plateau, 40)
            if res_zone:
                dir_move = res_zone[0]
            else:
                # Si tout est plein, on va vers l'ennemi le plus proche pour le peindre/voler
                # (Ajoutez ici une logique de traque si vous voulez)
                possibles = plateau.directions_possibles(le_plateau, pos)
                if possibles: dir_move = random.choice(list(possibles.keys()))

    # --- PHASE 3 : OPTIMISATION DU TIR (Votre Sniper) ---
    # On réutilise la fonction solide que je vous ai donnée avant
    dir_tir = choisir_meilleur_tir(notre_IA, le_plateau, les_joueurs, dir_move, carac_jeu)
    
    # Optimisation finale : Si on a le pistolet et qu'on va vers un mur, on tire SUR le mur
    if objet_tenu == const.PISTOLET and dir_move != 'X':
        # Vérif rapide si un mur est devant
        inc = plateau.INC_DIRECTION[dir_move]
        devant = (pos[0]+inc[0], pos[1]+inc[1])
        if plateau.est_sur_plateau(le_plateau, devant) and case.est_mur(plateau.get_case(le_plateau, devant)):
            dir_tir = dir_move # On tire sur le mur qu'on colle

    return dir_tir + dir_move

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
