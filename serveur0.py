#!/usr/bin/python
# -*- coding: utf-8 -*-

import os.path
current_dir       = os.path.dirname(os.path.abspath(__file__))
current_ipaddress = '127.0.0.1'
current_port      = 8080

import cherrypy, sqlite3, os.path
from datetime import datetime

class TableFormat(object):
    """
    Une classe pour préciser un format de tables à afficher en HTML,
    lié à une requête de base de données.
    On peut faire des classes dérivées de celle-ci pour fabriquer des
    tableaux avec des propriétés particulières.
    """
    def __init__(self, tname, tclasse, columns, formats, names, classes, header=True):
        """
        Constructeur
        @param tname nom de la table dans la BDD
        @param tclasse classe CSS pour le tableau
        @param columns un tuple de colonnes de bases de données
        @param formats un tuple de chaînes de format pour les données
        @param names noms des contenus des colonnes pour faire des titres
        @param classes classes CSS pour les colonnes
        @param header vrai (par défaut) si on veut une ligne de titres
        """
        ## nom de la table dans la BDD
        self.tname=tname
        ## classe CSS à appliquer au tableau
        self.tclasse=tclasse
        ## noms de colonnes de la table dans la BDD
        self.columns=columns
        ## chaînes de formats applicables pour afficher ces colonnes
        self.formats=formats
        ## titres compréhensibles par des humains pour les colonnes
        self.names=names
        ## classes CSS à appliquer aux données de ces colonnes
        self.classes=classes
        ## booléen : présence/absence de titres pour l'affichage des colonnes
        self.header=header
        return

    def entete(self):
        """
        Fabrique une ligne de titres
        @return une ligne de titres de colonnes avec les bonnes classes CSS
        """
        result= u"<tr>"
        for cn in zip(self.classes, self.names):
            result += u"<th class='%s'>%s</th>" % cn
        result+= u"</tr>"
        return result

    def tbody(self,c):
        """
        Fabrique le corps du tableau
        @param c un curseur de BDD déjà initialisé
        @return une suite de lignes pour un tableau HTML
        """
        result=""
        request="SELECT " + ", ".join(self.columns) + " FROM "+ self.tname
        for ligne in c.execute(request):
            result+= u"<tr>"
            for li,fo,cl in zip(ligne, self.formats, self.classes):
                fstring=u"<td class='%%s'>%s</td>" % fo
                result += fstring % (cl,li)
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
        conn = sqlite3.connect(dbName)
        c = conn.cursor()
        # Création de la table "perles"
        c.execute('''CREATE TABLE perles
             (orig TEXT, trad TEXT, lang TEXT, datecreated DATE, id INTEGER PRIMARY KEY ASC)''')
        # Création de la table "votes"
        c.execute("""CREATE TABLE votes
              (perleId INTEGER, pseudo TEXT, datevote DATE, id INTEGER PRIMARY KEY ASC)""")
        conn.commit()
        conn.close()

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
      
    def index(self, phrase1=None, phrase2=None, langues=None, *args, **kw):
        """
        Implémentation du service en une seule page (index). Les arguments
        arrivent par un méthode GET.
        @param phrase1 phrase avant traduction
        @param phrase2 phrase après traduction
        @param langues une chaîne de langues pour la traduction
        @param *args liste des arguments non nommés de la requête
        (pas utilisée dans ce contexte)
        @param **kw dictionnaire des arguments nommés de la requête
        (sert à éviter un blocage au cas où des paramètres inattendus sont
        reçus lors d'une requête)
        """
        conn = sqlite3.connect(self.dbName)
        c = conn.cursor()
        ##########################################
        # En-tête HTML
        ##########################################
        result=u"<html>\n"+self.headerHtml()+u"<body>\n"
        ##########################################
        # traitement d'une requête d'ajout dans la base de données
        ##########################################
        if (phrase1 and phrase2 and langues):
            d=u"%s" %datetime.now()
            c.execute("""INSERT INTO perles 
                      (orig, trad, lang, datecreated)
                      VALUES (?,?,?,?)""",
                      (phrase1, phrase2, langues, d))
            conn.commit()
            result+= self.modalDialog(u"Modification de la base de données",
                                      [phrase1, phrase2, langues, d])
        ##########################################
        # traitement par défaut : on affiche le contenu de la BDD
        ##########################################
        c.execute("SELECT count(*) FROM perles")
        # self.conn.commit()
        compte = c.fetchone()[0]
        result+= u"<h1>La base de données contient %d perles :</h1>" %compte
        ##########################################
        # tableau des perles existantes
        ##########################################
        tf= TableFormat(
            "perles",
            "perleTable",
            ("id", "orig", "trad", "lang", "datecreated"),
            ("%03d","%s",  "%s",   "%s",   "%s"),
            (u"Id",u"Phrase de départ",u"Phrase d'arrivée",u"Chaîne de langues",u"Date d'enregistrement"),
            ("perleid","p1","p2","lang","date")
            )
        result += tf.table(c)
        ##########################################
        # fin du traitement par défaut
        ##########################################
        result += "</body>"
        conn.close()
        return result


    index.exposed = True




if __name__=='__main__':
    cherrypy.quickstart(PerleServer('example.db'), config="serveur0.conf")
