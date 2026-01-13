from bot_ia import client
from bot_ia import const
from bot_ia import plateau
from bot_ia import case
from bot_ia import joueur

def Innondation(le_plateau, pos, distance_max, recherche=None):
    """Fonction de l'innondation qui prend en considération un objet en recherche.
    Args:
        le_plateau (Plateau): Le plateau de jeu.
        pos (tuple): La position de départ (x, y).
        distance_max (int): La distance maximale à parcourir.
        recherche (str, optional): Type de recherche ('J', 'O', 'C', None). Defaults to None.
    Returns:
        dict: {(distance, (x,y)): {'Objet': ..., 'Joueur': ...}}
    """

    # Nouvelle structure de clé : (distance, position)
    dico_distances = dict()
    
    # Vérifier si la position de départ est sur le plateau
    if not plateau.est_sur_plateau(le_plateau, pos):
        return dico_distances
    
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
            la_case = plateau.get_case(le_plateau, pos_actuelle)
            
            # Dictionnaire temporaire pour stocker ce qu'on trouve sur CETTE case
            infos_case = {}

            # --- CAS 1 : Recherche de JOUEURS ---
            if recherche == 'J': 
                joueurs = case.get_joueurs(la_case)
                if len(joueurs) > 0:
                    infos_case['Joueur'] = joueurs # On stocke l'ensemble des joueurs
                    rechercheFound = True # On arrête car on as trouvé notre object

            # --- CAS 2 : Recherche d'OBJETS ---
            elif recherche == 'O': 
                objet = case.get_objet(la_case)
                if objet != const.AUCUN:
                    infos_case['Objet'] = objet
                    rechercheFound = True

            # --- CAS 3 : Recherche de COULEUR ---
            elif recherche == 'C':
                couleur = case.get_couleur(la_case)
                if couleur != ' ':
                    infos_case['Couleur'] = couleur
                    rechercheFound = True

            # --- CAS 4 : Recherche TOUT ---
            else:
                objet = case.get_objet(la_case)
                joueurs = case.get_joueurs(la_case)
                couleur = case.get_couleur(la_case)
            
                if objet != const.AUCUN:
                    infos_case['Objet'] = objet
                
                if len(joueurs) > 0:
                    infos_case['Joueur'] = joueurs
                    
                if couleur != ' ':
                    infos_case['Couleur'] = couleur

            if infos_case:
                dico_distances[(distance, pos_actuelle)] = infos_case


            # --- Gestion des voisins ---
            if distance < distance_max:
                for dir_nom in plateau.directions_possibles(le_plateau, pos_actuelle):
                    inc = plateau.INC_DIRECTION[dir_nom]
                    voisin_pos = (pos_actuelle[0] + inc[0], pos_actuelle[1] + inc[1])
                    
                    if voisin_pos not in visitee:
                        visitee.add(voisin_pos)
                        queue.append((voisin_pos, distance + 1))
                        
    return dico_distances