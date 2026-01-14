from bot_ia import client
from bot_ia import const
from bot_ia import plateau
from bot_ia import case
from bot_ia import joueur

def Innondation(le_plateau, pos, distance_max, recherche=None, C_cherche=None, O_cherche=None):
    """
    Args:
        le_plateau (dict): L'état actuel du plateau.
        pos (tuple): Position de départ (x, y).
        distance_max (int): Portée du scan.
        recherche (str): 'J' (Joueurs), 'O' (Objets), 'C' (Couleur), None (Tout).
        C_cherche (str): Si spécifié, ne retient que cette couleur.
        O_cherche (int): Si spécifié, ne retient que cet objet.
    Returns:
        dict: {(distance, pos): {'Objet': ..., 'Couleur': ..., 'Direction': ...}}
        'Direction' indique la première direction à prendre pour atteindre cette cible depuis le départ.
    """
    dico_distances = dict()
    
    if not plateau.est_sur_plateau(le_plateau, pos):
        return dico_distances
    
    visitee = set()
    # file d'attente : (position, distance, premiere_direction)
    # premiere_direction est la direction prise au tout premier pas (N, S, E, O)
    queue = [(pos, 0, None)]
    visitee.add(pos)
    index = 0
    rechercheFound = False
    
    # Pré-calcul des dimensions pour éviter les appels répétés
    nb_lignes = le_plateau["nb_lignes"]
    nb_cols = le_plateau["nb_colonnes"]
    valeurs = le_plateau["les_valeurs"]
    
    while index < len(queue) and not rechercheFound:
        pos_actuelle, distance, premiere_direction = queue[index]
        index += 1

        if distance <= distance_max:
            # Accès direct optimisé (si possible) ou via getter
            la_case = plateau.get_case(le_plateau, pos_actuelle)
            infos_case = {}

            # --- ANALYSE DE LA CASE ---
            if 'J' in recherche or recherche is None:
                joueurs_case = case.get_joueurs(la_case)
                if joueurs_case:
                    infos_case['Joueur'] = joueurs_case
                    if 'J' == recherche: rechercheFound = True

            if 'O' in recherche or recherche is None:
                objet = case.get_objet(la_case)
                if objet != const.AUCUN:
                    if O_cherche is None or objet == O_cherche:
                        infos_case['Objet'] = objet
                        if 'O' == recherche: rechercheFound = True
          
            if 'C' in recherche or recherche is None:
                coul = case.get_couleur(la_case)
                if coul != ' ' or ' ' in recherche:
                    if C_cherche is None or coul == C_cherche:
                        infos_case['Couleur'] = coul
                        if 'C' == recherche: rechercheFound = True
            if 'A' == recherche:
                coul = case.get_couleur(la_case)
                if coul != C_cherche:
                    infos_case['Couleur'] = coul
                    rechercheFound = True
            # Si on a trouvé quelque chose d'intéressant
            if infos_case:
                if distance > 0: 
                    # On ajoute l'info cruciale : par quelle direction commencer pour aller ici ?
                    infos_case['Direction'] = premiere_direction
                    dico_distances[(distance, pos_actuelle)] = infos_case

            # --- EXPANSION DES VOISINS ---
            if distance < distance_max and not rechercheFound:
                # Optimisation: itération directe sur les incréments sans créer de dictionnaire intermédiaire
                for dir_nom, inc in plateau.INC_DIRECTION.items():
                    if dir_nom == 'X': continue
                    
                    voisin_pos = (pos_actuelle[0] + inc[0], pos_actuelle[1] + inc[1])
                    
                    # Vérification manuelle (plus rapide que plateau.est_sur_plateau + get_case + est_mur)
                    if 0 <= voisin_pos[0] < nb_lignes and 0 <= voisin_pos[1] < nb_cols:
                        idx = voisin_pos[0] * nb_cols + voisin_pos[1]
                        case_voisin = valeurs[idx]
                        
                        if not case_voisin["mur"]: # Accès direct au dict case
                            if voisin_pos not in visitee:
                                visitee.add(voisin_pos)
                                # Si distance est 0, c'est le premier pas, on définit la direction
                                next_dir = dir_nom if distance == 0 else premiere_direction
                                queue.append((voisin_pos, distance + 1, next_dir))
                        
    return dico_distances