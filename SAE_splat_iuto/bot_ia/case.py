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

Module de gestion des cases
"""
from bot_ia import const


def Case(mur=False, couleur=' ', objet=const.AUCUN, joueurs_presents=None):
    """Permet de créer une case du plateau

    Args:
        mur (bool, optional): un booléen indiquant si la case est un mur ou un couloir.
                Defaults to False.
        couleur (str, optional): un caractère indiquant la couleur de la peinture.
                c'est un identifiant de joueur). Defaults to ' '.
        objet (int, optional): un numero indiquant l'objet qui se trouve sur la case.
                const.AUCUN indique qu'il n'y a pas d'objet sur la case. Defaults to const.AUCUN.
        joueurs_presents (set, optional): un ensemble indiquant la liste des joueurs
                se trouvant sur la case. Defaults to None.

    Returns:
        dict: un dictionnaire représentant une case du plateau
    """
    res = {"mur": mur, "couleur": couleur, "objet": objet}
    if joueurs_presents is None:
        res["joueurs_presents"] = set()
    else:
        res["joueurs_presents"] = joueurs_presents
    return res


def est_mur(case):
    """indique si la case est un mur ou non

    Args:
        case (dict): la case considérée

    Returns:
        bool: True si la case est un mur et False sinon
    """
    return case["mur"]


def get_couleur(case):
    """retourne la couleur de la case sous la forme d'un caractère représentant
            l'idenfiant du joueur qui a peint cette case. La chaine vide indique
            qu'il n'y a pas de peinture sur la case.

    Args:
        case (dict): la case considérée


    Returns:
        str: l'identifiant du joueur qui a peint la case ou la chaine vide
    """
    return case["couleur"]


def get_objet(case):
    """retourne l'identifiant de l'objet qui se trouve sur la case. const.AUCUN indique l'absence d'objet.

    Args:
        case (dict): la case considérée

    Returns:
        int: l'identifiant de l'objet qui se trouve sur la case.
    """
    return case["objet"]


def get_joueurs(case):
    """retourne l'ensemble des joueurs qui sont sur la case

    Args:
        case (dict): la case considérée

    Returns:
        set: l'ensemble des identifiants de joueurs présents su la case.
    """
    return case["joueurs_presents"]


def get_nb_joueurs(case):
    """retourne le nombre de joueurs présents sur la case

    Args:
        case (dict): la case considérée

    Returns:
        int: le nombre de joueurs présents sur la case.
    """
    return len(case["joueurs_presents"])


def peindre(case, couleur, simul=False):
    """Affecte la couleur passée en paramètre à la case et retourne la liste des
        joueurs présents sur la carte.

    Args:
        case (dict): la case considérée. On considère que cette case n'est pas un mur.
        couleur (str): l'identifiant du joueur qui a peint la case. on considère que
                cette chaine ne sera pas vide.

    Returns:
        set: l'ensemble des identifiants des joueurs présents sur la carte
    """
    if not simul:
        case["couleur"] = couleur
    return case["joueurs_presents"]


def laver(case):
    """Enlève la peinture qui était enventuellement sur la case

    Args:
        case (dict): la case considérée. On considère que cette case n'est pas un mur.
    """
    case["couleur"] = " "


def poser_objet(case, objet):
    """Pose un objet sur la case. Si un objet était déjà présent ce dernier disparait

    Args:
        case (dict): la case considérée
        objet (int): identifiant d'objet. const.AUCUN indiquant que plus aucun objet se
                trouve sur la case.
    """
    case["objet"] = objet


def prendre_objet(case):
    """Enlève l'objet qui se trouve sur la case et retourne l'identifiant de cet objet.
        Si aucun objet se trouve sur la case la fonction retourne const.UCUN.

    Args:
        case (dict): la case considérée

    Returns:
        int: l'identifiant de l'objet que si trouve sur la case.
    """
    res = case["objet"]
    case["objet"] = const.AUCUN
    return res


def poser_joueur(case, joueur):
    """Pose un nouveau joueur sur la case

    Args:
        case (dict): la case considérée
        joueur (str): identifiant du joueur à ajouter sur la case
    """
    case["joueurs_presents"].add(joueur)


def prendre_joueur(case, joueur):
    """Enlève le joueur dont l'identifiant est passé en paramètre de la case.
        La fonction retourne True si le joueur était bien sur la case et False sinon.

    Args:
        case (dict): la case considérée
        joueur (str): l'identifiant du joueur à enlever

    Returns:
        bool: True si le joueur était bien sur la case et False sinon.
    """
    if joueur in case["joueurs_presents"]:
        case["joueurs_presents"].remove(joueur)
        return True
    return False
