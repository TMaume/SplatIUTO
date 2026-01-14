from bot_ia import const
from bot_ia import plateau
from bot_ia import case
from collections import deque

def Innondation(le_plateau, pos, distance_max, recherche=None, C_cherche=None, O_cherche=None, arret_premier=True):
    """
    Args:
        le_plateau (dict): L'état actuel du plateau.
        pos (tuple): Position de départ (x, y).
        distance_max (int): Portée du scan.
        recherche (str): 'J' (Joueurs), 'O' (Objets), 'C' (Couleur), None (Tout).
        C_cherche (str): Si spécifié, ne retient que cette couleur.
        O_cherche (int): Si spécifié, ne retient que cet objet.
        arret_premier (bool): Si True, s'arrête dès la première trouvaille. 
                              Si False, scanne tout le rayon (indispensable pour votre stratégie).
    Returns:
        dict: {(distance, pos): {'Objet': ..., 'Couleur': ..., 'Direction': ...}}
    """
    dico_distances = {}
    
    if not plateau.est_sur_plateau(le_plateau, pos):
        return dico_distances
    
    visitee = {pos}
    queue = deque([(pos, 0, None)])
    recherche_found = False
    
    nb_lignes = le_plateau["nb_lignes"]
    nb_cols = le_plateau["nb_colonnes"]
    valeurs = le_plateau["les_valeurs"]

    cherche_tout = recherche is None
    cherche_j = cherche_tout or ('J' in recherche)
    cherche_o = cherche_tout or ('O' in recherche)
    cherche_c = cherche_tout or ('C' in recherche)
    
    while queue:
        if arret_premier and recherche_found:
            break

        pos_actuelle, distance, premiere_direction = queue.popleft()

        if distance > distance_max:
            continue

        idx_actuelle = pos_actuelle[0] * nb_cols + pos_actuelle[1]
        la_case = valeurs[idx_actuelle]
        infos_case = {}
        
        trouve_ici = False

        if cherche_j:
            joueurs_case = case.get_joueurs(la_case)
            if joueurs_case:
                infos_case['Joueur'] = joueurs_case
                if recherche == 'J': trouve_ici = True

        if cherche_o:
            objet = case.get_objet(la_case)
            if objet != const.AUCUN and (O_cherche is None or objet == O_cherche):
                infos_case['Objet'] = objet
                if recherche == 'O': trouve_ici = True

        if cherche_c:
            coul = case.get_couleur(la_case)
            if C_cherche is None:
                if coul != ' ':
                    infos_case['Couleur'] = coul
                    if recherche == 'C': trouve_ici = True
            else:
                if coul == C_cherche:
                    infos_case['Couleur'] = coul
                    if recherche == 'C': trouve_ici = True

        if recherche == 'A':
            coul = case.get_couleur(la_case)
            if coul != C_cherche:
                infos_case['Couleur'] = coul
                trouve_ici = True

        if trouve_ici:
            recherche_found = True

        if infos_case and distance > 0:
            infos_case['Direction'] = premiere_direction
            dico_distances[(distance, pos_actuelle)] = infos_case

        if distance >= distance_max:
            continue
        
        if arret_premier and recherche_found:
            continue

        for dir_nom, (d_lig, d_col) in plateau.INC_DIRECTION.items():
            if dir_nom == 'X': continue

            voisin_pos = (pos_actuelle[0] + d_lig, pos_actuelle[1] + d_col)
            
            if not (0 <= voisin_pos[0] < nb_lignes and 0 <= voisin_pos[1] < nb_cols):
                continue

            idx_voisin = voisin_pos[0] * nb_cols + voisin_pos[1]
            case_voisin = valeurs[idx_voisin]
            
            if case_voisin["mur"]: continue
            if voisin_pos in visitee: continue

            visitee.add(voisin_pos)
            next_dir = dir_nom if distance == 0 else premiere_direction
            queue.append((voisin_pos, distance + 1, next_dir))
                        
    return dico_distances