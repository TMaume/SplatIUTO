# import argparse
# import random

from bot_ia  import client
from bot_ia  import const
from bot_ia  import plateau
from bot_ia  import case
from bot_ia  import joueur


def Innondation(plateau, pos, distance_max, recherche=None):
    """Fonction de l'innondation qui prend en considération les murs.
    """

    # Type de dico voulu: {4: {objet: 4, pos : (x, y) Joueur : 'A' }}
    dico_distances = dict()
    
    # Vérifier si la position de départ est sur le plateau
    if not plateau.est_sur_plateau(plateau, pos):
        return dico_distances
    
    # Utiliser une approche BFS (Breadth-First Search) pour contourner les murs
    visitee = set()
    queue = [(pos, 0)]  # (position, distance)
    visitee.add(pos)
    index = 0
    rechercheFound = False
    
    while index < len(queue) and not rechercheFound:
        pos_actuelle, distance = queue[index]
        index += 1

        # Si on ne dépasse pas la distance max
        if distance <= distance_max:
            # Récupérer la case actuelle
            la_case = plateau.get_case(plateau, pos_actuelle)
            
            # Enregistrer les joueurs et objets
            if recherche == 'J': #Recherche uniquement les joueurs
                joueurs = case.get_joueurs(la_case)

                if len(joueur) > 0:
                    if distance not in dico_distances:
                        dico_distances[distance] = dict()
                    
                    for joueur in joueurs:
                        dico_distances[distance]['Joueur'] = {joueur}
                    dico_distances[distance]['Pos'] = pos_actuelle
                    print(dico_distances[distance])


            elif recherche == 'O': #Recherche uniquement les objets
                objet = case.get_objet(la_case)
                
                if objet != const.AUCUN:
                    if distance not in dico_distances:
                        dico_distances[distance] = dict()

                    if objet != const.AUCUN:
                        dico_distances[distance]['Objet'] = objet
            
            elif recherche == 'C':
                couleur = case.get_couleur(la_case)
                if couleur != ' ':
                    if distance not in dico_distances:
                        dico_distances[distance] = dict()
                    if couleur != ' ':
                        dico_distances[distance]['Couleur'] =  couleur

            else:
                objet = case.get_objet(la_case)
                joueurs = case.get_joueurs(la_case)
                couleur = case.get_couleur(la_case)
            
                if objet != const.AUCUN or len(joueurs) > 0 or couleur != ' ':
                    if distance not in dico_distances:
                        dico_distances[distance] = dict()

                    if objet != const.AUCUN:
                        dico_distances[distance]['Objet'] = objet

                    for joueur in joueurs:
                        dico_distances[distance]['Joueur'] = {joueur}
                        
                    if couleur != ' ':
                        dico_distances[distance]['Couleur'] =  couleur
                        
                    dico_distances[distance]['Pos'] = pos_actuelle


            if distance < distance_max:
                for dir_nom in plateau.directions_possibles(plateau, pos_actuelle):
                    voisin_pos = (pos_actuelle[0] + plateau.INC_DIRECTION[dir_nom][0],
                                  pos_actuelle[1] + plateau.INC_DIRECTION[dir_nom][1])
                    if voisin_pos not in visitee:
                        visitee.add(voisin_pos)
                        queue.append((voisin_pos, distance + 1))
    return dico_distances