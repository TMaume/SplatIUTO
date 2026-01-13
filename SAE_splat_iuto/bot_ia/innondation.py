# import argparse
# import random

from bot_ia  import client
from bot_ia  import const
from bot_ia  import plateau
from bot_ia  import case
from bot_ia  import joueur


def Innondation(plateau, pos, distance_max):
    """calcul les distances entre la position pos est les différents objets et
        joueurs du plateau en se limitant à la distance max.

    Args:
        plateau (dict): le plateau considéré
        pos (tuple): une paire d'entiers indiquant la postion de calcul des distances
        distance_max (int): un entier indiquant la distance limite de la recherche
    Returns:
        dict: un dictionnaire dont les clés sont des distances et les valeurs sont des ensembles
            contenant à la fois des objets et des joueurs. Attention le dictionnaire ne doit contenir
            des entrées uniquement pour les distances où il y a effectivement au moins un objet ou un joueur
    """ 
    # Type de dico voulu: {4: {4}, 10: {'D'}, 14: {3}, 15: {'E'}, 17: {1, 'C'}, 18: {'A', 'B'}}
    dico_distances = dict()
    
    # Vérifier si la position de départ est sur le plateau
    if not plateau.est_sur_plateau(plateau, pos):
        return dico_distances
    
    # Utiliser une approche BFS (Breadth-First Search) pour contourner les murs
    visitee = set()
    queue = [(pos, 0)]  # (position, distance)
    visitee.add(pos)
    index = 0
    
    while index < len(queue):
        pos_actuelle, distance = queue[index]
        index += 1
        
        # Si on ne dépasse pas la distance max
        if distance <= distance_max:
            # Récupérer la case actuelle
            la_case = plateau.get_case(plateau, pos_actuelle)
            
            # Enregistrer les joueurs et objets
            objet = case.get_objet(la_case)
            joueurs = case.get_joueurs(la_case)
            
            if objet != const.AUCUN or len(joueurs) > 0:
                if distance not in dico_distances:
                    dico_distances[distance] = dict

                if objet != const.AUCUN:
                    dico_distances[distance]['Objet'] = (objet)

                for joueur in joueurs:
                    dico_distances[distance]['Joueur'] = {joueur}
                dico_distances[distance]['Pos'] = pos_actuelle

            if distance < distance_max:
                for dir_nom in plateau.directions_possibles(plateau, pos_actuelle):
                    voisin_pos = (pos_actuelle[0] + plateau.INC_DIRECTION[dir_nom][0],
                                  pos_actuelle[1] + plateau.INC_DIRECTION[dir_nom][1])
                    if voisin_pos not in visitee:
                        visitee.add(voisin_pos)
                        queue.append((voisin_pos, distance + 1))
    return dico_distances