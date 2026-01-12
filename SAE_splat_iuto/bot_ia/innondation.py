def creer_file():
    """Crée une file vide"""
    return []

def enfiler(file, element):
    """Ajoute un élément à la fin de la file"""
    file.append(element)

def defiler(file):
    """Retire et retourne le premier élément de la file"""
    return file.pop(0)

def file_vide(file):
    """Vérifie si la file est vide"""
    return len(file) == 0


def est_case_vide(case_obj):
    """Vérifie si une case est vide (libre et sans objet)"""
    return case_obj.est_libre() and case_obj.get_objet() == 0

def a_objet(case_obj, num_objet):
    """Vérifie si une case contient un objet spécifique"""
    return case_obj.get_objet() == num_objet

def est_objectif_atteint(case_obj, position, pos_depart, cherche_case_vide, num_objet):
    """Vérifie si on a trouvé ce qu'on cherche"""
    if position == pos_depart:
        return False
    
    if cherche_case_vide:
        return est_case_vide(case_obj)
    else:
        return a_objet(case_obj, num_objet)



def calculer_position_voisine(position, direction):
    """Calcule la position d'un voisin selon une direction"""
    ligne, col = position
    delta_ligne, delta_col = INC_DIRECTION[direction]
    return (ligne + delta_ligne, col + delta_col)

def ajouter_voisin_a_explorer(nouvelle_pos, position_actuelle, visites, parents, file):
    """Ajoute un voisin non visité à la file d'exploration"""
    if nouvelle_pos not in visites:
        # Marquer comme visité
        visites.add(nouvelle_pos)
        # Enregistrer le parent
        parents[nouvelle_pos] = position_actuelle
        # Ajouter à la file
        enfiler(file, nouvelle_pos)

def explorer_voisins(plateau, position_actuelle, visites, parents, file):
    """Explore tous les voisins valides d'une position"""
    voisins = directions_possibles(plateau, position_actuelle)
    
    for direction in voisins.keys():
        nouvelle_pos = calculer_position_voisine(position_actuelle, direction)
        ajouter_voisin_a_explorer(nouvelle_pos, position_actuelle, visites, parents, file)


# ============= RECONSTRUCTION DU CHEMIN =============

def reconstruire_chemin(parents, depart, arrivee):
    """Reconstruit le chemin en remontant les parents"""
    chemin = []
    position = arrivee
    
    # Remonter de l'arrivée vers le départ
    while position is not None:
        chemin.append(position)
        position = parents[position]
    
    # Inverser pour avoir départ → arrivée
    chemin.reverse()
    return chemin


# ============= INITIALISATION =============

def initialiser_recherche(pos_depart):
    """Initialise les structures pour la recherche BFS"""
    file = creer_file()
    enfiler(file, pos_depart)
    
    visites = set()
    visites.add(pos_depart)
    
    parents = {}
    parents[pos_depart] = None
    
    return file, visites, parents


# ============= ALGORITHME PRINCIPAL =============

def trouver_chemin_bfs(plateau, pos_depart, cherche_case_vide=True, num_objet=None):
    """Trouve le plus court chemin par inondation (BFS)
    
    Args:
        plateau: le plateau de jeu
        pos_depart: position (ligne, colonne) de départ
        cherche_case_vide: True pour chercher une case vide
        num_objet: numéro de l'objet à chercher (si cherche_case_vide=False)
    
    Returns:
        list: le chemin, None si pas trouvé
    """
    # Initialisation
    file, visites, parents = initialiser_recherche(pos_depart)
    
    # Boucle principale
    while not file_vide(file):
        # Prendre la prochaine case à explorer
        position_actuelle = defiler(file)
        case_actuelle = get_case(plateau, position_actuelle)
        
        # Vérifier si c'est l'objectif
        if est_objectif_atteint(case_actuelle, position_actuelle, pos_depart, 
                                 cherche_case_vide, num_objet):
            return reconstruire_chemin(parents, pos_depart, position_actuelle)
        
        # Explorer les voisins
        explorer_voisins(plateau, position_actuelle, visites, parents, file)
    
    # Aucun chemin trouvé
    return None
