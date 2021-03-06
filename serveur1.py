#!/usr/bin/python
# -*- coding: utf-8 -*-

import os.path
current_dir       = os.path.dirname(os.path.abspath(__file__))
current_ipaddress = '127.0.0.1'
current_port      = 8080

import cherrypy, shelve, os.path, datetime, types

class PerleCursor(object):
    """
    Classe servant à parcourir les perles enregistrées
    """
    def __init__(self, perleList):
        """
        Constructeur
        @param perleList une liste de perles
        """
        self.list = perleList

    def getDataLines(self, columns, table=None):
        """
        Effectue une requête dans la base de données et renvoie un itérable
        contenant les données demandées
        @param columns identifiants de colonnes
        @param table identifiant de tableau (inutile ici)
        """
        result=[]
        for perle in self.list:
            l=[]
            for c in columns:
                if len(c) == 2 and isinstance(c[0], types.FunctionType):
                    # on doit appliquer la fonction c[0] aux arguments
                    # pointés par c[1]
                    args=[]
                    for argName in c[1]:
                        if isinstance(argName, str):
                            val=getattr(perle, argName, None)
                            args.append(val)
                        else:
                            args.append(argName)
                    l.append(c[0](*args))
                else:
                    val=getattr(perle, c, None)
                    l.append(val)
            result.append(l)
        return result

class TableData(object):
    """
    Une classe pour spécifier des données pouvant former des corps de tableaux
    c'est à dire avec une séquence de colonnes ayant des propriétés précises.
    """
    def __init__(self, columns, formats, names, layouts):
        """
        Constructeur
        @param columns séquence d'identifiants de colonnes
        @param formats séquence de chaînes de formats pour les colonnes
        @param names noms lisibles de chaque colonne
        @param layouts séquence de descriptions d'affichage (par ex. en CSS)
        """
        self.columns= columns
        self.formats=formats
        self.names=names
        self.layouts=layouts
        return


class TableFormat(object):
    """
    Une classe pour représenter des données en tableau, avec une séparation
    des contenus et de la forme sous laquelle on les affiche.
    On peut faire des classes dérivées de celle-ci pour fabriquer des
    tableaux avec des propriétés particulières.
    """
    def __init__(self, tname, tclasse, tdata, header=True):
        """
        Constructeur
        @param tname nom du tableau (identifiant, si on préfère)
        @param tclasse description de l'affichage général du tableau 
        (classe CSS par exemple)
        @param tdata un objet TableData spécifiant la structure des données
        du corps du tableau
        @param header vrai (par défaut) si on veut une ligne de titres en tête
        du tableau
        """
        ## nom de la table dans une BDD
        self.tname=tname
        ## description d'affichage (classe CSS) à appliquer au tableau
        self.tclasse=tclasse
        ## identifiants de colonnes de la table dans la BDD
        self.tdata=tdata
        ## booléen : présence/absence de titres pour l'affichage du tableau
        self.header=header
        return

    def entete(self):
        """
        Fabrique une ligne de titres
        @return une ligne de titres de colonnes avec les bonnes classes CSS
        """
        result= u"<tr>"
        for cn in zip(self.tdata.layouts, self.tdata.names):
            result += u"<th class='%s'>%s</th>" % cn
        result+= u"</tr>"
        return result

    def tbody(self,c):
        """
        Fabrique le corps du tableau
        @param c un curseur de BDD
        @return une suite de lignes pour un tableau HTML
        """
        result=""
        for ligne in c.getDataLines(self.tdata.columns, self.tname):
            result+= u"<tr>"
            for li,fo,cl in zip(ligne, self.tdata.formats, self.tdata.layouts):
                if "%" in fo:
                    fstring=u"<td class='%%s'>%s</td>" % fo
                    result += fstring % (cl,li)
                else:
                    # fo n'est pas un format mais un objet en javascript
                    result +="<td>%s</td>" %li
            result+= u"</tr>\n"
        return result

    def table(self,c):
        """
        Fabrique le tableau HTML
        @param c un curseur de BDD déjà initialisé
        @return tableau HTML
        """
        result = u"<table>\n"
        if self.header:
            result += self.entete()
        result += self.tbody(c)
        result += "</table>\n"
        return result

class Vote(object):
    """
    Une classe pour définir un vote, pour une perle de Bableur
    """
    def __init__(self, stamp, saveur='ordinaire'):
        """
        Constructeur
        @param stamp un timbre à date de perle
        @param saveur la qualité particulière du vote
        """
        self.timeStamp=stamp
        self.saveur=saveur

    def __str__(self):
        """
        @return une chaîne représentant un vote
        """
        return "Vote %s, %s" %(self.saveur, self.timeStamp)
    def __repr__(self):
        """
        @return une chaîne "système" représentant un vote
        """
        return self.__str__()

class Perle(object):
    """
    Une classe repré&sentant une perle intéressante à montrer, issue de Bableur
    """
    def __init__(self, orig, trad, lang):
        """
        Constructeur
        @param orig la phrase originale
        @param trad sa traduction
        @param lang la chaîne de langues utilisées pour la traduction
        """
        self.orig=orig
        self.trad=trad
        self.lang=lang
        self.timeStamp=datetime.datetime.now()

def delButton(timeStamp):
    """
    @param timeStamp une date identifiant un enregistrement à supprimer
    @return du code HTML pour un bouton d'effacement
    """
    return "<a href='?delperle=%s'><img src='del.png' alt=\"supprimer l'enregistrement\" title=\"supprimer l'enregistrement\" /></a>" %timeStamp

def voteButton(timeStamp):
    """
    @param timeStamp une date identifiant un enregistrement
    @return du code HTML pour un bouton de vote
    """
    return "<a href='?voteperle=%s'><img src='vote.png' alt=\"Voter pour l'enregistrement\" title=\"Voter pour l'enregistrement\" /></a>" %timeStamp

def nbVotes(timeStamp, votes):
    """
    @param timeStamp une date identifiant un enregistrement
    @param votes une liste d'objets Vote
    @return du code HTML pour un nombre de votes concernant cet enregistrement
    """
    pour=[vote for vote in votes if str(vote.timeStamp)==str(timeStamp)]
    return len(pour)
    
class PerleServer(object):
    """
    Une classe pour servir les perles de traduction de Bableur, et pour
    permettre de voter pour celles-ci. Cette classe permet l'implémentation
    d'une page web unique (index) pour le serveur Cherrypy
    """
    def __init__(self, dbName):
        """
        Constructeur de la classe PerleServer. Crée une base de
        données si celle-ci n'existe pas, sinon rouvre la base de données
        existante.
        @param dbName le nom du fichier de base de données
        """
        ## nom de la base de données utilisée
        self.dbName=dbName
        if os.path.exists(dbName):
            # on ne recrée pas une base de données préexistante
            return
        ## création de la base de données à l'aide du module "shelve"
        d = shelve.open(self.dbName)
        d["perles"]=[] # crée une liste de perles vide
        d["votes"]=[]  # crée une liste de votes vide
        d.close()

    def headerHtml(self, title=u"Serveur de perles basé sur CherryPy"):
        """
        Définit les en-têtes de pages HTML, qui incluent l'activation
        de la bibliothèque jQuery, des indications de style, et un
        script pour les boîtes de dialogues modales.
        @param title le titre de la page ; 
        par défaut : "Serveur de perles basé sur CherryPy"
        @return le contenu du nœud <head> pour les pages HTML
        """
        return u"""\
<head>
  <title>%s</title>
  <link rel="icon" href="/perle.ico" type="image/x-icon" />
  <link rel="shotcut icon" href="/perle.ico" />
  <link rel="stylesheet" type="text/css" href="style.css"/>
  <link rel="stylesheet" href="jquery-ui/themes/base/jquery.ui.all.css"/>
  <script type="text/javascript" src="jquery-ui/jquery-1.9.1.js"></script>
  <script type="text/javascript" src="jquery-ui/ui/jquery.ui.core.js"></script>
  <script type="text/javascript" src="jquery-ui/ui/jquery.ui.widget.js"></script>

  <script type="text/javascript" src="jquery-ui/ui/jquery.ui.mouse.js"></script>
  <script type="text/javascript" src="jquery-ui/ui/jquery.ui.draggable.js"></script>
  <script type="text/javascript" src="jquery-ui/ui/jquery.ui.position.js"></script>
  <script type="text/javascript" src="jquery-ui/ui/jquery.ui.resizable.js"></script>
  <script type="text/javascript" src="jquery-ui/ui/jquery.ui.button.js"></script>
  <script type="text/javascript" src="jquery-ui/ui/jquery.ui.dialog.js"></script>
  <script type="text/javascript">
    //// s'il y a un dialogue modal dans la page, il est affiché.
    $(function() {
      $( "#dialog-modal" ).dialog({
        width: 500,
        modal: true
      });
    });
  </script>
</head>
"""  % title

    def modalDialog(self, title, contents):
        """
        affiche une boîte de dialogue modale
        @param title le titre de la boîte
        @param contents le contenu de la boîte
        """
        return u"""\
<div id="dialog-modal" title="%s">
    %s
</div>
""" %(title, contents)
      
    def index(self, phrase1=None, phrase2=None, langues=None, 
              delperle=None, voteperle=None, addvote=None,
              *args, **kw):
        """
        Implémentation du service en une seule page (index). Les arguments
        arrivent par un méthode GET.
        @param phrase1 phrase avant traduction
        @param phrase2 phrase après traduction
        @param langues une chaîne de langues pour la traduction
        @param delperle un timbre à date de perle à supprimer
        @param voteperle un timbre à date de perle pour un vote
        @param addvote un timbre à date de perle pour finaliser un vote
        @param *args liste des arguments non nommés de la requête
        (pas utilisée dans ce contexte)
        @param **kw dictionnaire des arguments nommés de la requête
        (sert à éviter un blocage au cas où des paramètres inattendus sont
        reçus lors d'une requête)
        """
        d = shelve.open(self.dbName)
        perles=d["perles"]
        votes=d["votes"]
        ##########################################
        # En-tête HTML
        ##########################################
        result=u"<html>\n"+self.headerHtml()+u"<body>\n"
        ##########################################
        # traitement d'une requête d'ajout dans la base de données
        ##########################################
        if (phrase1 and phrase2 and langues):
            perles.append(Perle(phrase1, phrase2,langues ))
            d["perles"]=perles
            comment=u"Ajout de « %s  ...»" %phrase1[:25]
            result+= self.modalDialog(u"Modification de la base de données", comment)
        ##########################################
        # traitement d'une requête d'effacement de la base de données
        ##########################################
        elif (delperle):
            toDel=[perle for perle in perles if str(perle.timeStamp)==delperle]
            comment=u""
            for perle in toDel:
                perles.remove(perle)
                d["perles"]=perles
                comment+=u"« %s ... », %s" %(perle.orig[:25], perle.timeStamp)
            result+= self.modalDialog(u"Suppression effectuée", comment)
            ## retrait des votes inutiles
            toDel=[vote for vote in votes if str(vote.timeStamp)==str(delperle)]
            for v in toDel:
                votes.remove(v)
                d["votes"]=votes
        ##########################################
        # traitement d'une requête de vote
        ##########################################
        elif (voteperle):
            sel=[perle for perle in perles if str(perle.timeStamp)==voteperle]
            if len(sel) > 0:
                perle=sel[0]
                comment=u"""
phrase d'origine : %s<br/>
phrase traduite : %s<br/>
<center><input type='button' value='je vote pour !' onclick='javascript: document.location.href ="?addvote=%s"' /></center>
""" %(perle.orig, perle.trad, perle.timeStamp)
                result+= self.modalDialog(u"Vote pour une perle", comment)
        ##########################################
        # prise en compte d'un vote exprimé
        ##########################################
        elif (addvote):
            sel=[perle for perle in perles if str(perle.timeStamp)==addvote]
            if len(sel) > 0:
                perle=sel[0]
                votes.append(Vote(addvote))
                d["votes"]=votes
                comment=u"""
phrase d'origine : %s<br/>
phrase traduite : %s<br/>
<b>Le vote a été pris en compte.</b>
""" %(perle.orig, perle.trad)
                result+= self.modalDialog(u"Vote pour une perle", comment)
        ##########################################
        # traitement par défaut : on affiche le contenu de la BDD
        ##########################################
        result+= u"<h1>La base de données contient %d perles :</h1>" %len(d["perles"])
        ##########################################
        # tableau des perles existantes
        ##########################################
        td= TableData(((nbVotes,("timeStamp", votes)),
                       "orig", "trad", "lang", "timeStamp",
                       (delButton,("timeStamp",)),
                       (voteButton,("timeStamp",)),
                       ),
                      ("special", "%s",  "%s",   "%s",   "%s", "special", "special"),
                      (u"Popularité", u"Phrase de départ",u"Phrase d'arrivée",u"Chaîne de langues",u"Date d'enregistrement", u"Suppr.", u"Vote"),
                      ("popularite","p1","p2","lang","date","button","button")
                      )
        tf= TableFormat("perles", "perleTable", td)
        result += tf.table(PerleCursor(d["perles"]))
        ##########################################
        # fin du traitement par défaut
        ##########################################
        result += "</body>"
        d.close()
        return result


    index.exposed = True




if __name__=='__main__':
    cherrypy.quickstart(PerleServer('example1.db'), config="serveur0.conf")
