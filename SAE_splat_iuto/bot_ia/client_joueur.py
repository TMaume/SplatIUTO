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
    # priorité 3 : aller chercher un bonus si on en a pas
    # priorité 4 : se déplacer sur une case non peinte ou de notre couleur
    # priorité 5 : si l'on a un bouclier actif aller en direction des adversaires pour les toucher
    # priorité 6 : rester a distance des autres joueurs
    # priorité 7 : si on a un pistolet tirer sur les murs
    # priorité 8 : peindre dans une zone avec le moins de peinture enemie et moins de notre peinture
    
    for joueur in les_joueurs:
        if joueur["couleur"] == ma_couleur:
            notre_IA = joueur

                

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

            resultat = innondation.Innondation(le_plateau, pos_voisin, distance_max - 1, recherche='C', valeur_cherche=ma_couleur)
            
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


    def deplacement_peinture_negative(notre_IA, le_plateau, distance_max):
        ma_couleur = joueur.get_couleur(notre_IA)
        ma_pos = joueur.get_pos(notre_IA)
        
        voisins_possibles = plateau.directions_possibles(le_plateau, ma_pos)
        
        if not voisins_possibles:
            return random.choice("NSEO")

        meilleure_direction = None
        min_distance_trouvee = distance_max + 1

        for direction in voisins_possibles:

            inc = plateau.INC_DIRECTION[direction]
            pos_voisin = (ma_pos[0] + inc[0], ma_pos[1] + inc[1])

            resultat = innondation.Innondation(le_plateau, pos_voisin, distance_max - 1, recherche='O', valeur_cherche=const.BIDON)
            
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
    

    # def a_etoile(depart, cible, le_plateau):
        
    #     def get_direction(liste,pos):
    #         directions = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "O": (0, -1)}
    #         liste_finale = []
    #         for car in liste:
    #             liste_finale.append((pos[0]+directions[car][0],pos[1]+directions[car][1]))
    #         return liste_finale
            
    #     def heuristique(a,b):
    #         return abs(a[0]-b[0])+abs(a[1]-b[1])
            
    #     liste_case_a_explorer = [depart]
    #     liste_case_deja_explorer = dict()

    #     cout_chemin = {depart:0}

    #     while liste_case_a_explorer:
    #         actuel = min(liste_case_a_explorer, key=lambda x: cout_chemin[x] + heuristique(x,cible))

    #         if actuel == cible:
    #             return liste_case_deja_explorer

    #         liste_case_a_explorer.remove(actuel)

    #         for voisin in get_direction(plateau.directions_possibles(le_plateau,actuel).keys(), actuel):
    #             tentative = cout_chemin[actuel] + 1
    #             if voisin not in cout_chemin or tentative < cout_chemin[voisin]:
    #                 liste_case_deja_explorer[voisin] = actuel
    #                 cout_chemin[voisin] = tentative
    #                 liste_case_a_explorer.append(voisin)
    #     return None

    # def premiere_direction(notre_IA, cible, plateau): # fonction pour se deplacer vers un point donné
    #     depart = joueur.get_pos(notre_IA)
    #     directions = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "O": (0, -1)}
    #     liste_pos = a_etoile(depart, cible, plateau)
    #     if liste_pos is None:
    #         return random.choice("NSEO")

    #     noeud = cible
    #     while liste_pos[noeud] != depart:
    #         noeud = liste_pos[noeud]

    #     deplacement_x = noeud[0] - depart[0]
    #     deplacement_y = noeud[1] - depart[1]

    #     for dir, (valeur_x, valeur_y) in directions.items():
    #         if (deplacement_x, deplacement_y) == (valeur_x, valeur_y):
    #             return dir

    

    
    
    # Programme principal
    
    #deplacement
    if joueur.get_reserve(notre_IA) == 0: # aller se recharger quand on a plus de peinture
        deplacement_peinture_zero(notre_IA, Distance_max)
    elif joueur.get_reserve(notre_IA) < 0: # si notre reserve de peinture est negative aller chercher un bideon
        deplacement_peinture_negative(no)
    dir_tir = direction_tir_ennemi(notre_IA, le_plateau, les_joueurs, carac_jeu)


    # IA complètement aléatoire
    # return random.choice("XNSOE")+random.choice("NSEO")

def direction_tir_ennemi(moi, le_plateau, les_joueurs, carac_jeu):

    portee = const.PORTEE_PEINTURE # 
    if joueur.get_objet(moi) == const.PISTOLET: # 
        portee = 5 
    ma_lig, ma_col = joueur.get_pos(moi) # 

    positions_ennemis = set()
    for adv in les_joueurs.values():
        if joueur.get_couleur(adv) != joueur.get_couleur(moi):
            positions_ennemis.add(joueur.get_pos(adv))
    directions = plateau.INC_DIRECTION 

    for sens, (d_lig, d_col) in directions.items():
        if sens == 'X': continue 

        for i in range(1, portee + 1):
            cible = (ma_lig + d_lig * i, ma_col + d_col * i)

            if not plateau.est_sur_plateau(le_plateau, cible):
                break 
            
            la_case = plateau.get_case(le_plateau, cible) 

            if case.est_mur(la_case): 

                break 
            if cible in positions_ennemis:
                return sens 
                
    return None






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
