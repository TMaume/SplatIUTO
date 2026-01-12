# coding: utf-8

import sys
import argparse

import socket
import threading
import time
import random
import queue

from serveur import jeu
from serveur import client



JOUEUR = 1
AFFICHEUR = 2
TOUS = 3

NB_JOUEURS = 4

TEMPO=0.3

class Table_Clients(object):
    def __init__(self, nb_joueurs_max, nb_afficheur_max=5):
        self.nb_joueurs_max = nb_joueurs_max
        self.nb_afficheur_max = nb_afficheur_max
        self.nb_joueurs = 0
        self.nb_actifs = 0
        self.joueurs = []
        self.afficheurs = []
        self.reponses = {}
        self.nb_reponses = 0
        self.verrou_ajout = threading.RLock()
        self.verrou_reponses = threading.Lock()
        self.nouvelle_iteration = threading.Event()
        self.reponses_ok = threading.Event()
        self.le_jeu = None

    def ajouter_joueur(self, joueur):
        self.verrou_ajout.acquire()
        if len(self.joueurs) == self.nb_joueurs_max:
            joueur.envoyer_refus()
            joueur.clientsocket.fermer()
            self.verrou_ajout.release()
            return -1
        self.joueurs.append(joueur)
        self.le_jeu.inscrire_joueur(joueur.nom)
        res = chr(ord('A')+self.nb_joueurs)
        self.nb_joueurs += 1
        self.nb_actifs += 1
        self.verrou_ajout.release()
        self.envoyer_jeu(AFFICHEUR)
        return res

    def enlever_client(self, client):
        self.verrou_ajout.acquire()
        if client.type_client == JOUEUR:
            ind = self.joueurs.index(client)
            if ind != -1:
                client.clientsocket.fermer()
                self.nb_joueurs -= 1
                self.nb_actifs -= 1
                #self.joueurs.pop(ind)
                print("Joueur", client.id, "déconnecté")
        elif client.type_client == AFFICHEUR:
            ind = self.afficheurs.index(client)
            if ind != -1:
                client.clientsocket.fermer()
                self.afficheurs.pop(ind)
                print("Afficheur", client.id, "déconnecté")
        self.verrou_ajout.release()

    def ajouter_afficheur(self, afficheur):
        self.verrou_ajout.acquire()
        if len(self.afficheurs) == self.nb_afficheur_max:
            afficheur.envoyer_refus()
            afficheur.clientsocket.fermer()
            self.verrou_ajout.release()
            return -1
        self.afficheurs.append(afficheur)
        res = len(self.afficheurs)
        self.verrou_ajout.release()
        self.envoyer_jeu(AFFICHEUR)
        return res

    def envoyer_jeu(self, dest=TOUS):
        self.verrou_ajout.acquire()
        jeu_temp = self.le_jeu
        jeu_str = jeu_temp.jeu_2_str()
        if dest == JOUEUR or dest == TOUS:
            for joueur in self.joueurs:
                joueur.envoyer_jeu(jeu_str)
        if dest == AFFICHEUR or dest == TOUS:
            for afficheur in self.afficheurs:
                afficheur.envoyer_jeu(jeu_str)    
        self.verrou_ajout.release()

    def envoyer_quit(self):
        self.verrou_ajout.acquire()
        for joueur in self.joueurs:
            joueur.envoyer_quit()
        for afficheur in self.afficheurs:
                afficheur.envoyer_quit()
        self.verrou_ajout.release()

    def envoyer_message(self, msg, dest=TOUS):
        self.verrou_ajout.acquire()
        if dest == JOUEUR or dest == TOUS:
            for joueur in self.joueurs:
                joueur.envoyer_message(msg)
        if dest == AFFICHEUR or dest == TOUS:
            for afficheur in self.afficheurs:
                afficheur.envoyer_message(msg)
        self.verrou_ajout.release()

    def commencer_nouvelle_iteration(self):
        self.nouvelle_iteration.set()

    def ajouter_reponse(self, id_joueur, msg):
        self.verrou_reponses.acquire()
        self.nouvelle_iteration.clear()
        self.reponses[id_joueur] = msg
        self.nb_reponses += 1
        if self.nb_reponses >= self.nb_actifs:
            self.reponses_ok.set()
        self.verrou_reponses.release()

    def recolter_reponses(self):
        self.reponses_ok.wait()
        self.reponses_ok.clear()
        self.verrou_reponses.acquire()
        res = self.reponses.copy()
        self.reponses = {}
        self.nb_reponses = 0
        self.verrou_reponses.release()
        return res

    def attendre_nouvelle_iteration(self):
        self.nouvelle_iteration.wait()

    def liberer_ressources(self):
        for joueur in self.joueurs:
            joueur.clientsocket.fermer()
        for afficheur in self.afficheurs:
            afficheur.clientsocket.fermer()


class JeuThread(threading.Thread):

    def __init__(self, ecouteur, table_clients, duree, nom_partie='score.csv', map='/home/limet/AP/splat_iuto/source/cartes/carte.txt'):
        super().__init__()
        self.ecouteur=ecouteur
        self.table_clients = table_clients
        self.nom_partie = nom_partie
        table_clients.le_jeu = jeu.Jeu(map,duree)
        self.interactif=False
        self.file_commandes=queue.Queue()

    def traiter_commande_clavier(self,coul,commandes):
        try:
            rep = self.file_commandes.get(block=self.interactif)
            msg="le joueur "+self.table_clients.le_jeu.les_joueurs[coul].nom
            if len(commandes)!=2:
                " a donné un commande incorrecte. "
            else:
                if commandes[0]=='X':
                    msg+=" n'a pas peint. "
                else:
                    msg+=" a peint vers "
                    if commandes[0]=="N":
                        msg+="le nord. "
                    elif commandes[0]=="S":
                        msg+="le sud. "
                    elif commandes[0]=="O":
                        msg+="l'ouest. "
                    elif commandes[0]=="E":
                        msg+="l'est. "
                    else:
                        msg+="l'inconnu. "
                msg+=" Il a demandé à se déplacer vers "
                if commandes[1]=="N":
                    msg+="le nord."
                elif commandes[1]=="S":
                    msg+="le sud."
                elif commandes[1]=="O":
                    msg+="l'ouest."
                elif commandes[1]=="E":
                    msg+="l'est."
                else:
                    msg+="l'inconnu."
            print(msg)
            self.interactif=True
            if rep=="R":
                self.interactif=False
        except queue.Empty:
            rep =''


    def run(self):
        # pb ici de coordination entre le start et les inscriptions
        print("On attend")
        while True:
            input()
            if self.table_clients.nb_joueurs==NB_JOUEURS:
                break
            print("Tous les joueurs ne sont pas inscrits\nOn attend")
        print("C'est parti!!!")
        lecteur_commande=Interaction(self.file_commandes)
        lecteur_commande.start()
        self.table_clients.envoyer_jeu()
        cpt = 0
        rep=''
        self.table_clients.commencer_nouvelle_iteration()
        while rep != 'Q':

            recup = self.table_clients.recolter_reponses()

            if recup != None:
                # L'ordre d'exécution des actions des joueurs est aléatoire
                ordre_jeu=list(recup.keys())
                random.shuffle(ordre_jeu)
                for id_joueur in ordre_jeu:
                    actions=recup[id_joueur]
                    coul=id_joueur
                    self.table_clients.le_jeu.executer_actions(coul,actions)
                    self.table_clients.le_jeu.maj_surface()
                    self.table_clients.le_jeu.les_joueurs[coul].maj_points()
                    self.traiter_commande_clavier(coul,actions)
                    self.table_clients.envoyer_jeu(AFFICHEUR)

                self.table_clients.le_jeu.fin_tour()
                if table_clients.le_jeu.est_fini():
                    self.table_clients.envoyer_jeu(AFFICHEUR)
                    break
                self.table_clients.envoyer_jeu()
                self.table_clients.commencer_nouvelle_iteration()
                time.sleep(TEMPO)
                cpt += 1
        self.table_clients.envoyer_quit()
        self.table_clients.liberer_ressources()
        table_clients.le_jeu.sauver_score(self.nom_partie)
        self.ecouteur.arreter()
        print("C'est fini")


class ClientThread(threading.Thread):

    def __init__(self, ip, port, clientsocket, table_clients):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.clientsocket = client.ClientCyber()
        self.clientsocket.set_socket(clientsocket)
        self.table_clients = table_clients
        self.actif=True

    def maj_info_client(self, type_client, nom):
        self.nom = nom
        self.id = -1
        if type_client == "joueur":
            self.type_client = JOUEUR
        elif type_client == "afficheur":
            self.type_client = AFFICHEUR
        else:
            print("[-] Type de client inconnu")
            return False
        res = False
        if self.type_client == JOUEUR:
            self.id = table_clients.ajouter_joueur(self)
            if self.id != -1:
                print("[+] Nouveau joueur [%s] pour %s %s" %
                      (self.nom, self.ip, self.port, ))
                res = True
            else:
                print("[-] Trop de joueurs déjà enregistrés")
        elif self.type_client == AFFICHEUR:
            self.id = table_clients.ajouter_afficheur(self)
            if self.id != -1:
                print("[+] Nouvel afficheur [%s] pour %s %s" %
                      (self.nom, self.ip, self.port, ))      
                res = True
            else:
                print("[-] Trop d'afficheurs déjà enregistrés")
        return res

    def lire_commande(self):
        if not self.actif:
            self.table_clients.ajouter_reponse(self.id, "")
            return True
        try:
            la_commande = self.clientsocket.recevoir_commande_client()
        except Exception as ex:
            print(ex)
            print(self.id, "semble déconnecté")
            self.table_clients.ajouter_reponse(self.id, "")
            return True
        self.table_clients.ajouter_reponse(self.id, la_commande)
        return True

    def envoyer_quit(self):
        try:
            self.clientsocket.envoyer_quit()
        except:
            print(self.id,"est deconnecté") 
            self.table_clients.enlever_client(self)

    def envoyer_refus(self):
        try:
            self.clientsocket.envoyer_refus()
        except:
            print(self.id,"est deconnecté")    

    def envoyer_jeu(self,jeu_str):
        if not self.actif:
            return
        try:
            self.clientsocket.envoyer_jeu(jeu_str,self.id)
        except:
            print(self.id,"est deconnecté")
            self.table_clients.enlever_client(self)

    def envoyer_message(self, message):
        if not self.actif:
            return
        try:
            self.clientsocket.envoi(message)
        except:
            print(self.id, "est déconnecté")
            self.table_clients.enlever_client(self)

    def run(self):
        print("Connexion de %s %s" % (self.ip, self.port, ))
        
        type_cli, nom_cli = self.clientsocket.recevoir_enregistrement()
        if self.maj_info_client(type_cli, nom_cli):
            if self.type_client == JOUEUR:
                continuer = True
                while continuer:
                    self.table_clients.attendre_nouvelle_iteration()
                    continuer = self.lire_commande()
                print("Client déconnecté...")

class Ecouteur(threading.Thread):
    def __init__(self,serveur,port,table_clients):
        threading.Thread.__init__(self)
        self.ip=serveur
        self.port=port
        self.table_clients=table_clients
        self.ok=True

    def arreter(self):
        self.ok=False
    
    def run(self):
        tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tcpsock.bind((self.ip, self.port))
        while self.ok:
            tcpsock.listen(10)
            print("En écoute...")
            (clientsocket, (ip, port)) = tcpsock.accept()
            newthread = ClientThread(self.ip, self.port, clientsocket, self.table_clients)
            newthread.start()

class Interaction(threading.Thread):
    def __init__(self,file_commandes):
        threading.Thread.__init__(self)
        self.file_commandes=file_commandes

    def run(self):
        while True:
            cmd = input()
            if len(cmd)>0:
                self.file_commandes.put(cmd[0])

if __name__ == '__main__':
    print("Bienvenue dans le jeu de Splat'IUT'O")
    parser = argparse.ArgumentParser()
    parser.add_argument("--serveur", dest="serveur", help="serveur de jeu", type=str, default='localhost')
    parser.add_argument("--port", dest="port", help="port de connexion", type=int, default=1111)
    parser.add_argument("--nom_partie", dest="nom_partie", help="nom de la partie", type=str, default='score.csv')
    parser.add_argument("--duree", dest="duree", help="nombre de tours de la partie", type=int, default=200)
    parser.add_argument("--map", dest="map", help="fichier contenant la map", type=str, default='./cartes/carte.txt')
    
    args = parser.parse_args()
    
    table_clients = Table_Clients(6, 5)
    ecouteur=Ecouteur(args.serveur,args.port,table_clients)
    ecouteur.start()
    le_jeu = JeuThread(ecouteur,table_clients,args.duree,args.nom_partie,args.map)
    le_jeu.start()
