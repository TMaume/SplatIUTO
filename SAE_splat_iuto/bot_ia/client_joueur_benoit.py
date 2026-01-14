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

OBJECTIF=None

def recup_chemin(le_plateau, depart, destination):
    """Renvoie le plus court chemin entre depart et destination

    Args:
        le_plateau (dict): le plateau de jeu
        depart (tuple): un tuple de deux entiers de la forme (no_ligne, no_colonne) 
        destination (tuple): un tuple de deux entiers de la forme (no_ligne, no_colonne) 

    Returns:
        list: Une liste de positions entre destination et depart
        qui représente le chemin le plus court entre les deux positions, ou None si impossible
    """
    # Vérifier si les positions sont sur le plateau
    hauteur = plateau.get_nb_lignes(le_plateau)
    largeur = plateau.get_nb_colonnes(le_plateau)
    if not (0 <= depart[0] < hauteur and 0 <= depart[1] < largeur) or not (0 <= destination[0] < hauteur and 0 <= destination[1] < largeur):
        return None  
    
    # 1. REMPLISSAGE DES DISTANCES (On garde TOUT)
    distances = {depart: 0}
    a_explorer = [depart]
    
    while a_explorer:
        case_actuelle = a_explorer.pop(0)
        if case_actuelle == destination:
            break
            
        dist_actuelle = distances[case_actuelle]
        for direction in plateau.directions_possibles(le_plateau, case_actuelle):
            r, c = case_actuelle
            if direction == 'N': voisine = (r-1, c)
            elif direction == 'S': voisine = (r+1, c)
            elif direction == 'E': voisine = (r, c+1)
            elif direction == 'O': voisine = (r, c-1)
            
            if voisine not in distances:
                distances[voisine] = dist_actuelle + 1
                a_explorer.append(voisine)

    if destination not in distances:
        return None

    # 2. RECONSTRUCTION (On choisit UN SEUL chemin parmi les possibles)
    chemin = [destination]
    while chemin[-1] != depart:
        case_actuelle = chemin[-1]
        dist_cible = distances[case_actuelle] - 1 # On cherche la distance n-1
        
        for direction in plateau.directions_possibles(le_plateau, case_actuelle):
            r, c = case_actuelle
            if direction == 'N': voisine = (r-1, c)
            elif direction == 'S': voisine = (r+1, c)
            elif direction == 'E': voisine = (r, c+1)
            elif direction == 'O': voisine = (r, c-1)
            
            # Dès qu'on trouve UNE case qui convient, on la prend et on 'break'
            if voisine in distances and distances[voisine] == dist_cible:
                chemin.append(voisine)
                break # Le break garantit qu'on ne prend qu'une seule case
                
    chemin.reverse()
    return chemin

def recup_chemin_important(ma_couleur, notre_pos, le_plateau):
    """recupère en dictionnaire les chemins les plus courts vers chaque joueur ennemie et chaque objet

    Args:
        ma_couleur (str): la couleur du joueur
        notre_pos (tuple): la position du joueur
        le_plateau (dict): le plateau de jeu

    Returns:
        tuple: Un tuple contenant deux dictionnaires :
        - chemin_adversaires : un dictionnaire des chemins vers les adversaires
        - chemin_objets : un dictionnaire des chemins vers les objets
    """
    chemin_adversaires=dict()
    chemin_objets=dict()
    for joueur in les_joueurs:
        if joueur["couleur"] != ma_couleur:
            chemin_adversaires[joueur["nom"]]=recup_chemin(le_plateau,notre_pos,joueur["position"])
    for ligne in range(plateau.get_nb_lignes(le_plateau)):
        for colonne in range(plateau.get_nb_colonnes(le_plateau)):
            type_objet=case.get_objet(plateau.get_case(le_plateau,(ligne,colonne)))
            if type_objet != const.AUCUN:
                chemin_objets[type_objet]=recup_chemin(le_plateau,notre_pos,(ligne,colonne))
    return chemin_adversaires, chemin_objets

def nos_cases(le_plateau, ma_couleur):
    """

    Args:
        le_plateau (dict): le plateau de jeu
        ma_couleur (str): la couleur du joueur

    Returns:
        list: la liste des cases appartenant au joueur
    """
    liste_cases = []
    for ligne in range(plateau.get_nb_lignes(le_plateau)):
        for colonne in range(plateau.get_nb_colonnes(le_plateau)):
            la_case=plateau.get_case(le_plateau,(ligne,colonne))
            if case.get_couleur(la_case)==ma_couleur:
                liste_cases.append((ligne,colonne))
    return liste_cases

def est_sur_plateau(position,le_plateau):
    """Vérifie si une position est sur le plateau.

    Args:
        position (tuple): un tuple de deux entiers de la forme (no_ligne, no_colonne)
        plateau (dict): le plateau de jeu

    Returns:
        bool: True si la position est sur le plateau, False sinon
    """
    nb_lignes = plateau.get_nb_lignes(le_plateau)
    nb_colonnes = plateau.get_nb_colonnes(le_plateau)
    return 0 <= position[0] < nb_lignes and 0 <= position[1] < nb_colonnes

def choisir_direction_prioritaire(directions_possibles, ma_couleur, notre_pos):
    """
    Choisit la meilleure direction selon une logique fixe :
    1. Case non peinte (priorité absolue pour gagner du terrain)
    2. Case adverse (pour voler des points)
    3. Case objet (pour obtenir des bonus)
    4. Case déjà à nous (si pas d'autre choix)
    """
    ordre_prefere = ['N', 'S', 'E', 'O']
    
    #Chercher d'abord à aller sur une case vide (' ')
    for d in ordre_prefere:
        if d in directions_possibles and directions_possibles[d] == ' ':
            return d
            
    #Sinon, aller sur une case ennemie (couleur différente de la nôtre)
    for d in ordre_prefere:
        if d in directions_possibles and directions_possibles[d] != ma_couleur:
            return d
    #Ensuite, une case avec un objet
    for d in ordre_prefere:
        if d in directions_possibles:
            la_case = plateau.get_case(le_plateau, (notre_pos[0] + (d == 'S') - (d == 'N'), notre_pos[1] + (d == 'E') - (d == 'O')))
            if case.get_objet(la_case) != const.AUCUN:
                return d
    #En dernier recours, une case à nous
    for d in ordre_prefere:
        if d in directions_possibles:
            return d
            
    return 'N' # Sécurité

def direction_vers_case_blanche(le_plateau, notre_pos):
    """Cherche la case blanche la plus proche et renvoie la direction pour y aller."""
    distance_min = 999
    meilleure_direction = None
    
    # On parcourt le plateau pour trouver les cases blanches
    for l in range(plateau.get_nb_lignes(le_plateau)):
        for c in range(plateau.get_nb_colonnes(le_plateau)):
            la_case = plateau.get_case(le_plateau, (l, c))
            
            # Si la case est blanche (vide)
            if case.get_couleur(la_case) == ' ': 
                chemin = recup_chemin(le_plateau, notre_pos, (l, c))
                if chemin and 1 < len(chemin) < distance_min:
                    distance_min = len(chemin)
                    prochaine_case = chemin[1]
                    
                    # Traduction en direction déterministe
                    if prochaine_case[0] < notre_pos[0]:
                        meilleure_direction = 'N'
                    elif prochaine_case[0] > notre_pos[0]:
                        meilleure_direction = 'S'
                    elif prochaine_case[1] < notre_pos[1]:
                        meilleure_direction = 'O'
                    elif prochaine_case[1] > notre_pos[1]:
                        meilleure_direction = 'E'
    return meilleure_direction

def ennemi_en_face(le_plateau, notre_pos, ma_couleur, portee):
    """check si un enemie est proche, si oui on l'attaque

    Args:
        le_plateau (dict): le plateau de jeu
        notre_pos (tuple): la position du joueur
        ma_couleur (str): la couleur du joueur
        portee (int): la portée de recherche/ du tire

    Returns:
        str: direction de tire vers l'ennemi s'il y en a un, None sinon
    """
    for direction in ['N', 'S', 'E', 'O']:
        nb = plateau.nb_joueurs_direction(le_plateau, notre_pos, direction, portee)#regarde dans la direction si il y a un joueur ennemi a porté
        if nb > 0:#calcul si la porté est suffisante
            inc = plateau.INC_DIRECTION[direction]
            pos = notre_pos
            for case_proche in range(portee): #pour chaque case dans la direction et a notre porté
                pos = (pos[0] + inc[0], pos[1] + inc[1])
                if not est_sur_plateau(pos, le_plateau):
                    break
                la_case = plateau.get_case(le_plateau, pos)
                for case_enemie in case.get_joueurs(la_case):
                    if case_enemie != ma_couleur:
                        return direction#tirer dans cette direction/ sur l'ennemie
    return None#si pas d'enemie proche

def meilleure_direction_mur(le_plateau, notre_pos, portee):
    """cherche la direction vers laquelle aller pour touché un maximum de mur

    Args:
        le_plateau (dict): le plateau de jeu
        notre_pos (tuple): la position du joueur
        portee (int): la portée de recherche

    Returns:
        str: la direction pouvant toucher le plus de murs dans la portée
    """
    meilleure_direction = None
    max_murs = 0    
    for direction in ['N','S','E','O']:
        cpt=plateau.INC_DIRECTION[direction]#recup la direction a tester
        pos=notre_pos
        nb_murs=0
        # Vérifier les cases dans la portée donnée vers la direction
        for case_proche in range(portee):
            pos = (pos[0] + cpt[0], pos[1] + cpt[1])#calcul de la position de la case proche vers la direction testée
            if not est_sur_plateau(pos, le_plateau):
                break
            la_case = plateau.get_case(le_plateau, pos)
            if case.est_mur(la_case):
                nb_murs += 1
            else:
                break
        if nb_murs > max_murs:
            max_murs = nb_murs
            meilleure_direction = direction
    
    return meilleure_direction#direction pouvant touché le plus de mur

def direction_bombe(le_plateau, notre_pos):
    """choisit selon la proximité des murs ou d'un enemi sur qui faire exploser la bombe

    Args:
        le_plateau (dict): le plateau de jeu
        notre_pos (tuple): la position du joueur
        ma_couleur (str): la couleur du joueur

    Returns:
        str: la direction pour faire exploser la bombe
    """
    for direction in ['N','S','E','O']:
        nb=plateau.nb_joueurs_direction(le_plateau, notre_pos, direction, 3)
        if nb > 0:#si l'enemi est proche, faire exploser sur lui
            return direction
    return meilleure_direction_mur(le_plateau,notre_pos,3)#sinon faire peter sur un mur proche

def calcul_direction(notre_pos, prochaine_case):
    """Calcule la direction entre notre position et la prochaine case

    Args:
        notre_pos (tuple): la position du joueur
        prochaine_case (tuple): la position de la prochaine case

    Returns:
        str: la direction entre les deux positions
    """
    if prochaine_case[0] < notre_pos[0]:
        return 'N'
    elif prochaine_case[0] > notre_pos[0]:
        return 'S'
    elif prochaine_case[1] < notre_pos[1]:
        return 'O'
    elif prochaine_case[1] > notre_pos[1]:
        return 'E'
    return None

def direction_vers_recharge(le_plateau, notre_pos, ma_couleur):
    """Cherche la case alliée la plus proche pour recharger la peinture ou le bidon si il est plus proche
    Args:
        le_plateau (dict): le plateau de jeu
        notre_pos (tuple): la position du joueur
        ma_couleur (str): la couleur du joueur
    Returns:
        str: la direction pour aller recharger la peinture
    """
    mes_positions = nos_cases(le_plateau, ma_couleur)
    meilleure_direction = None
    distance_min = plateau.get_nb_lignes(le_plateau)
    
    for pos_alliee in mes_positions:#pour chaque case alliée, chercher le plus court chemin
        chemin = recup_chemin(le_plateau, notre_pos, pos_alliee)
        if chemin and 1 < len(chemin) < distance_min:
            distance_min = len(chemin)
            prochaine_case = chemin[1]
            if prochaine_case[0] < notre_pos[0]:
                meilleure_direction = 'N'
            elif prochaine_case[0] > notre_pos[0]:
                meilleure_direction = 'S'
            elif prochaine_case[1] < notre_pos[1]:
                meilleure_direction = 'O'
            elif prochaine_case[1] > notre_pos[1]:
                meilleure_direction = 'E'
            if distance_min == 2:
                return meilleure_direction
    return meilleure_direction#direction pour aller recharger la peinture

def direction_vers_case_ennemies(le_plateau, notre_pos,ma_couleur):
    """Cherche la case blanche la plus proche et renvoie la direction pour y aller."""
    distance_min = 999
    meilleure_direction = None
    
    # On parcourt le plateau pour trouver les cases blanches
    for l in range(plateau.get_nb_lignes(le_plateau)):
        for c in range(plateau.get_nb_colonnes(le_plateau)):
            la_case = plateau.get_case(le_plateau, (l, c))
            couleur_case = case.get_couleur(la_case)
            if couleur_case != ' ' and couleur_case != ma_couleur:
                chemin = recup_chemin(le_plateau, notre_pos, (l, c))
                if chemin and 1 < len(chemin) < distance_min:
                    distance_min = len(chemin)
                    prochaine_case = chemin[1]
                    
                    # Traduction en direction déterministe
                    if prochaine_case[0] < notre_pos[0]:
                        meilleure_direction = 'N'
                    elif prochaine_case[0] > notre_pos[0]:
                        meilleure_direction = 'S'
                    elif prochaine_case[1] < notre_pos[1]:
                        meilleure_direction = 'O'
                    elif prochaine_case[1] > notre_pos[1]:
                        meilleure_direction = 'E'
    return meilleure_direction

def mon_IA(ma_couleur, stats_jeu, le_plateau, les_joueurs):
    """ Cette fonction permet de calculer les deux actions du joueur de couleur ma_couleur
        en fonction de l'état du jeu décrit par les paramètres. 
        Le premier caractère est parmi XSNOE X indique pas de peinture et les autres
        caractères indique la direction où peindre (Nord, Sud, Est ou Ouest)
        Le deuxième caractère est parmi SNOE indiquant la direction où se déplacer.

    Args:
        ma_couleur (str): un caractère en majuscule indiquant la couleur du joueur
        stats_jeu (dict)): un dictionnaire donnant les valeurs des caractéristiques du jeu:
             duree_actuelle, duree_totale, reserve_initiale, duree_obj, penalite, bonus_touche,
             bonus_recharge, bonus_objet et distance_max,
        le_plateau (dict): l'état du plateau actuel sous la forme décrite dans plateau.py
        les_joueurs (list[joueur]): la liste des joueurs avec leurs caractéristiques utilisant l'API
         joueur.py

    Returns:
        str: une chaine de deux caractères en majuscules indiquant la direction de peinture
            et la direction de déplacement
    """
    """
    Fonctionnement de l'IA :
    1-si la reserve de peinture est faible, on va vers un bidon ou une case alliée pour recharger sachant que l'on priorise le bidon a la case
    2-si l'on a assez de peinture, on peint dans la direction vers laquelle on va
    3-si on a un objet et assez de peinture, on l'utilise :
        -pistolet : on se colle a un mur (en prenant en compte le fait de peindre le plus de surface murale) et on tire dans la direction du mur
        -bombe : on fait exploser la bombe a coté d'un joueur ou d'un mur suivant la distance entre les 2
        -bouclier : on le conserve le plus longtemps possible
    4-si un ennemi est a porté de notre tire de peinture, on tire dans sa direction en priorisant le tir plutot que le déplacement
    5-si pas d'objet, on cherche la case blanche la plus proche et on se dirige vers elle
    6-si pas de case blanche, on cherche une case de couleur ennemie et on se dirige vers elle, cela va donc tiré sur les cases ennemies car l'on peint dans la direction de notre déplacement
    8-si pas de case blanche ou ennemie, on cherche l'ennemie le plus proche et on se dirige vers lui, cela va donc tiré sur lui car l'on peint dans la direction de notre déplacement
    
    """
    
    perso = les_joueurs[ma_couleur]#recup les données de notre joueur
    notre_pos = joueur.get_pos(perso)#recup la position du joueur
    reserve = joueur.get_reserve(perso)#recup la reserve de peinture du joueur
    objet = joueur.get_objet(perso)#recup l'objet du joueur
    direction_tir = 'X'
    direction_deplacement=None
    debug=""

#si la reserve de peinture est faible, aller vers une case de notre couleur
# Si la réserve est critique (<5) ou qu'on est en train de recharger (<15)
    if reserve < 10:
        debug="recharge"
        direction_tir = 'X' # On ne tire pas pendant la recharge
        #on utilise le chemin le plus court
        direction_deplacement = direction_vers_recharge(le_plateau, notre_pos, ma_couleur)
        return direction_tir+direction_deplacement

#gestion d'utilisation des objets
    if objet == const.PISTOLET and reserve > 5:
        debug = "pistolet"
        direction_mur = meilleure_direction_mur(le_plateau, notre_pos, const.PORTEE_PEINTURE)
        if direction_mur:
            direction_tir = direction_mur
        else:
            direction_tir = 'X'

    elif objet == const.BOMBE:#si c'est une bombe, faire exploser a coté d'un joueur ou d'un mur suivant distance
        debug="bombe"
        direction_bomb = direction_bombe(le_plateau, notre_pos)
        direction_tir = direction_bomb

    elif objet == const.BOUCLIER:#si c'est un bouclier, le conserver le plus longtemps
        debug="bouclier"
        direction_tir = 'X'

#si un ennemi est a porté de notre tire de peinture
    direction_ennemi = ennemi_en_face(le_plateau,notre_pos,ma_couleur,const.PORTEE_PEINTURE)#check la direction de l'ennemie
    if direction_ennemi and reserve > 5: #si on a assez de réserve, on tire dans la direction / sur le joueur pour potentiellemnent bloquer sa reserve
        debug="ennemi en face"
        direction_tir = direction_ennemi
    
#Si pas d'objet, chercher la case blanche la plus proche
    if direction_deplacement==None:
        direction_deplacement = direction_vers_case_blanche(le_plateau, notre_pos)
        debug="case blanche"
            
    #Si toujours rien (tout est déjà peint), utiliser les directions possibles
    if direction_deplacement==None:
        direction_deplacement=direction_vers_case_ennemies(le_plateau,notre_pos,ma_couleur)
        debug="case colorié"
    inc = plateau.INC_DIRECTION[direction_deplacement]
    pos_suivante = (notre_pos[0] + inc[0], notre_pos[1] + inc[1])

    # On vérifie si la case suivante est sur le plateau
    if est_sur_plateau(pos_suivante, le_plateau):
        case_suivante = plateau.get_case(le_plateau, pos_suivante)
    # Si la case n'est pas déjà à nous et qu'on a de la peinture, on tire
    if case.get_couleur(case_suivante) != ma_couleur and reserve > 0:
        direction_tir = direction_deplacement
    else:
        direction_tir = 'X'


# On vérifie la couleur de la case dans la direction choisie
    possibles = plateau.directions_possibles(le_plateau, notre_pos)
    if direction_tir=="X":
        if direction_deplacement in possibles and possibles[direction_deplacement] != ma_couleur and reserve > 5:
            direction_tir = direction_deplacement
        else:
            direction_tir = 'X'
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("\nDirection tir :", direction_tir+"\n"+"Direction déplacement :", direction_deplacement+"\n"+"Debug :", debug+"\n"+"Reserve peinture :", reserve)

    return direction_tir + direction_deplacement

    
    # IA complètement aléatoire
    #return random.choice("XNSOE")+random.choice("NSEO")

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
