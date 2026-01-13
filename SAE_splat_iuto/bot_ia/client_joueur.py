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

def mon_IA(ma_couleur,carac_jeu, le_plateau, les_joueurs):
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

    #### priorité 0 : si notre peinture est a 0 aller marcher sur notre peinture  (peinture_zero())
    #### priorité 1 : si notre peinture est negative aller chercher un bidon sans prendre en compte les autres priorités mise a part la 1 et la 2
    #### priorité 2 : si un joueur adverse est à portée de tir, le viser
    #### priorité 3 : aller chercher un bonus si on en a pas
    #### priorité 4 : se déplacer sur une case non peinte ou de notre couleur
    # priorité 5 : si l'on a un bouclier actif aller en direction des adversaires pour les toucher
    # priorité 6 : rester a distance des autres joueurs
    #### priorité 7 : si on a un pistolet tirer sur les murs
    # priorité 8 : peindre dans une zone avec le moins de peinture enemie et moins de notre peinture
    
    

                
        #------- Peintures a zéro -------#
    def deplacement_peinture_zero(notre_IA, le_plateau, distance_max):
        """
        Utilise Innondation pour trouver la peinture du joueur la plus proche
        et renvoie la direction pour s'en rapprocher.
        """

        ma_couleur = joueur.get_couleur(notre_IA)
        ma_pos = joueur.get_pos(notre_IA)
        
        voisins_possibles = plateau.directions_possibles(le_plateau, ma_pos)
        
        if not voisins_possibles:
            return random.choice("NSEO")

        meilleure_direction = None
        min_distance_trouvee = distance_max + 1
        

        for direction in voisins_possibles:
            if voisins_possibles[direction] == ma_couleur:
                return direction
            
            inc = plateau.INC_DIRECTION[direction]
            pos_voisin = (ma_pos[0] + inc[0], ma_pos[1] + inc[1])

            resultat = innondation.Innondation(le_plateau, pos_voisin, distance_max - 1, recherche='C', C_cherche=ma_couleur)
            
            if resultat:
                dist_min_scan = min(cle[0] for cle in resultat.keys())
                
                if dist_min_scan < min_distance_trouvee:
                    min_distance_trouvee = dist_min_scan
                    meilleure_direction = direction
        

        if meilleure_direction:
            return meilleure_direction
        
        choix_vides = [directionCase for directionCase, couleurCase in voisins_possibles.items() if couleurCase == ' ']
        if choix_vides:     
            return random.choice(choix_vides)   
            
        return random.choice(list(voisins_possibles.keys()))

        #------- Peintures négatives -------#
    def deplacement_peinture_negative(notre_IA, le_plateau, distance_max):
        ma_pos = joueur.get_pos(notre_IA)
        
        voisins_possibles = plateau.directions_possibles(le_plateau, ma_pos)
        
        if not voisins_possibles:
            return random.choice("NSEO")

        meilleure_direction = None
        min_distance_trouvee = distance_max + 1

        for direction in voisins_possibles:

            inc = plateau.INC_DIRECTION[direction]
            pos_voisin = (ma_pos[0] + inc[0], ma_pos[1] + inc[1])

            resultat = innondation.Innondation(le_plateau, pos_voisin, distance_max - 1, recherche='O', O_cherche=const.BIDON)
            
            if resultat:

                dist_min_scan = min(cle[0] for cle in resultat.keys())
                
                if dist_min_scan < min_distance_trouvee:
                    min_distance_trouvee = dist_min_scan
                    meilleure_direction = direction
        

        if meilleure_direction:
            return meilleure_direction

        choix_safe = [directionCase for directionCase, couleurCase in voisins_possibles.items() if couleurCase == ' ']
        
        if choix_safe:     
            return random.choice(choix_safe)   
            
        return random.choice(list(voisins_possibles.keys()))
    
        #------- Déplacement vers objet non défini -------#
    def deplacement_vers_objet(notre_IA, le_plateau, distance_max):
        """
        utilise Innondation pour trouver l'objet le plus proche
        et renvoie la direction pour s'en rapprocher.   
        """
        ma_pos = joueur.get_pos(notre_IA)
        dirTir = 'X'
        
        voisins_possibles = plateau.directions_possibles(le_plateau, ma_pos)
        
        if not voisins_possibles:
            return random.choice("NSEO")

        meilleure_direction = None
        min_distance_trouvee = distance_max + 1

        for direction in voisins_possibles:

            inc = plateau.INC_DIRECTION[direction]
            pos_voisin = (ma_pos[0] + inc[0], ma_pos[1] + inc[1])

            resultat = innondation.Innondation(le_plateau, pos_voisin, distance_max - 1, recherche='O')
            
            if resultat:

                dist_min_scan = min(cle[0] for cle in resultat.keys())
                
                if dist_min_scan < min_distance_trouvee:
                    min_distance_trouvee = dist_min_scan
                    meilleure_direction = direction
                    if dist_min_scan['couleur'] != ma_couleur:
                        dirTir = direction

        if meilleure_direction:
            return meilleure_direction, dirTir
        
    def deplacement_vers_vide(notre_IA, le_plateau, distance_max):
        """
        utilise Innondation pour trouver l'objet le plus proche
        et renvoie la direction pour s'en rapprocher.   
        """
        ma_pos = joueur.get_pos(notre_IA)
        dirTir = 'X'
        
        voisins_possibles = plateau.directions_possibles(le_plateau, ma_pos)
        
        if not voisins_possibles:
            return random.choice("NSEO")

        meilleure_direction = None
        min_distance_trouvee = distance_max + 1

        for direction in voisins_possibles:

            inc = plateau.INC_DIRECTION[direction]
            pos_voisin = (ma_pos[0] + inc[0], ma_pos[1] + inc[1])

            resultat = innondation.Innondation(le_plateau, pos_voisin, distance_max - 1, recherche='C', C_cherche=' ')
            
            if resultat:

                dist_min_scan = min(cle[0] for cle in resultat.keys())
                
                if dist_min_scan < min_distance_trouvee:
                    min_distance_trouvee = dist_min_scan
                    meilleure_direction = direction
                    if dist_min_scan['couleur'] != ma_couleur:
                        dirTir = direction

        if meilleure_direction:
            return meilleure_direction, dirTir
        
        #------- Tir sur ennemi avec const.PORTEE_PEINTURES -------#
    def direction_tir_ennemi(notre_IA, le_plateau, les_joueurs, carac_jeu):
        return max(plateau.INC_DIRECTION, 
                   key=lambda dir: plateau.nb_joueurs_direction(le_plateau, 
                                                                notre_IA['position'],
                                                                dir, 
                                                                const.PORTEE_PEINTURE))

        #------- Tir sur mur avec const.PISTOLET pour peindre le mur -------#
    def tirer_sur_mur(notre_IA, le_plateau, carac_jeu):
        if joueur.get_objet(notre_IA) == const.PISTOLET:
            portee = 5

        ma_lig, ma_col = joueur.get_pos(notre_IA) 
        directions = plateau.INC_DIRECTION 

        for sens, (d_lig, d_col) in directions.items():
            if sens == 'X': continue 

            for i in range(1, portee + 1):
                cible = (ma_lig + d_lig * i, ma_col + d_col * i)
                if plateau.est_sur_plateau(le_plateau, cible): 
                    la_case = plateau.get_case(le_plateau, cible) 

                if case.est_mur(la_case): 
                    return sens 
                    
        return None
    
    def attaquer_bouclier(notre_IA, le_plateau, les_joueurs):

        ma_pos = joueur.get_pos(notre_IA)
        ma_couleur = joueur.get_couleur(notre_IA)
        portee = const.PORTEE_PEINTURE 
        direction = plateau.INC_DIRECTION

        ennemis_proches = innondation.Innondation(le_plateau, ma_pos, portee, recherche='J')

        
        return None

    # Programme principal
    for joueur in les_joueurs:
        if joueur["couleur"] == ma_couleur:
            notre_IA = joueur
    
    #deplacement
    
    if joueur.get_reserve(notre_IA) == 0: # aller se recharger quand on a plus de peinture
        deplacement = deplacement_peinture_zero(notre_IA, plateau, 7)
    elif joueur.get_reserve(notre_IA) < 0: # si notre reserve de peinture est negative aller chercher un bideon
        deplacement = deplacement_peinture_negative(notre_IA)
    elif joueur.get_objet(notre_IA) == 0: # si on a pas d'objet 
        deplacement = deplacement_vers_objet(notre_IA, plateau, 7)


    
    ennemie_a_proximite = 0
    for dir in ["N", ""]
    dir_tir = direction_tir_ennemi(notre_IA, le_plateau, les_joueurs, carac_jeu)
    if joueur.get_objet(notre_IA) == const.BOUCLIER and joueur.get_reserve() > 5:
        attaquer_bouclier(notre_IA, plateau, les_joueurs)


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
