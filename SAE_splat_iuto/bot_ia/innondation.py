from bot_ia import client
from bot_ia import const
from bot_ia import plateau
from bot_ia import case
from bot_ia import joueur

def Innondation(le_plateau, pos, distance_max, recherche=None, valeur_cherche=None):
        """
        Args:
            le_plateau (dict): L'état actuel du plateau.
            pos (tuple): Position de départ (x, y).
            distance_max (int): Portée du scan.
            recherche (str): 'J' (Joueurs), 'O' (Objets), 'C' (Couleur), None (Tout).
            valeur_cherche (any): Si spécifié, ne retient que les éléments égaux à cette valeur
                                  (ex: ne garder que la couleur 'A').
        Returns:
            dict: {(distance, pos): {'Objet': ..., 'Couleur': ...}}
        """
        dico_distances = dict()
        
        if not plateau.est_sur_plateau(le_plateau, pos):
            return dico_distances
        
        visitee = set()
        queue = [(pos, 0)]
        visitee.add(pos)
        index = 0
        rechercheFound = False
        
        while index < len(queue) and not rechercheFound:
            pos_actuelle, distance = queue[index]
            index += 1

            if distance <= distance_max:
                la_case = plateau.get_case(le_plateau, pos_actuelle)
                infos_case = {}

        
                if recherche == 'J' or recherche is None:
                    joueurs_case = case.get_joueurs(la_case)
                    if joueurs_case:

                        infos_case['Joueur'] = joueurs_case
                        if recherche == 'J': rechercheFound = True

                
                if recherche == 'O' or recherche is None:
                    objet = case.get_objet(la_case)
                    if objet != const.AUCUN:
                        if valeur_cherche is None or objet == valeur_cherche:
                            infos_case['Objet'] = objet
                            if recherche == 'O': rechercheFound = True

              
                if recherche == 'C' or recherche is None:
                    coul = case.get_couleur(la_case)
                    if coul != ' ':
                    
                        if valeur_cherche is None or coul == valeur_cherche:
                            infos_case['Couleur'] = coul
                            if recherche == 'C': rechercheFound = True

                if infos_case:

                    if distance > 0: 
                        dico_distances[(distance, pos_actuelle)] = infos_case

                if distance < distance_max and not rechercheFound:
                    for dir_nom in plateau.directions_possibles(le_plateau, pos_actuelle):
                        inc = plateau.INC_DIRECTION[dir_nom]
                        voisin_pos = (pos_actuelle[0] + inc[0], pos_actuelle[1] + inc[1])
                        
                        if voisin_pos not in visitee:
                            visitee.add(voisin_pos)
                            queue.append((voisin_pos, distance + 1))
                            
        return dico_distances

def pathfinding():
    pass