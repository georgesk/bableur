#!/usr/bin/python
# -*- coding: utf-8 -*-

import os.path
current_dir       = os.path.dirname(os.path.abspath(__file__))
current_ipaddress = '127.0.0.1'
current_port      = 8080

import cherrypy, sqlite3, os.path
from datetime import datetime

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
        
    def index(self, phrase1=None, phrase2=None, langues=None, *args, **kw):
        """
        Implémentation du service en une seule page (index). Les arguments
        arrivent par un méthode GET.
        @param phrase1 phrase avant traduction
        @param phrase2 phrase après traduction
        @param langues une chaîne de langues pour la traduction
        @param *args liste des arguments non nommés de la requête
        @param **kw dictionnaire des arguments nommés de la requête
        """
        conn = sqlite3.connect(self.dbName)
        # déclenche la fabrication d'objets ROW à chaque invocation de fetchone
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        ##########################################
        # En-tête HTML
        ##########################################
        result=u"""\
<html>
<head>
  <title>Serveur de perles basé sur CherryPy</title>
  <link rel="stylesheet" type="text/css" href="style.css"></link>
  <link rel="stylesheet" href="jquery-ui/themes/base/jquery.ui.all.css">  <script type="text/javascript" src="jquery-ui/jquery-1.9.1.js"></script>
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
<body>
"""
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
            result+= u'<div id="dialog-modal" title="Modification de la base de données">'
            result+="ajout de %s" %([phrase1, phrase2, langues, d])
            result += '</div>'
        ##########################################
        # traitement par défaut : on affiche le contenu de la BDD
        ##########################################
        c.execute("SELECT count(*) FROM perles")
        # self.conn.commit()
        compte = c.fetchone()[0]
        result+= u"<h1>La base de données contient %d perles :</h1>" %compte
        result+= u"<table class='perleTable'>\n"
        # En-têtes des colonnes
        result+= u"<tr><th class='perleid'>Id</th><th class='p1'>Phrase de départ</th><th class='p2'>Phrase d'arrivée</th><th class='lang'>Chaîne de langues</th><th class='date'>Date d'enregistrement</th></tr>\n"
        c.execute("SELECT id, orig, trad, lang, datecreated FROM perles")
        # fabrique un dictionnaire à partir de la donnée récupérée
        # en effet fetchone revoie un objet de type sqlite3.Row
        # qui permet de retrouver les noms de colonnes par sa méthode
        # keys().
        ligne=c.fetchone()
        if ligne:
            dico=dict(zip(ligne.keys(), ligne))
        while ligne:
            result+= u"<tr><th class='perleid'>%(id)03d</th><td class='p1'>%(orig)s</td><td class='p2'>%(trad)s</td><td class='lang'>%(lang)s</td><td class='date'>%(datecreated)s</td></tr>\n" % dico
            ligne=c.fetchone()
            if ligne:
                dico=dict(zip(ligne.keys(), ligne))
        result += "</table>\n"
        result += "</body>"
        ##########################################
        # fin du traitement par défaut
        ##########################################
        conn.close()
        return result
    
    index.exposed = True




if __name__=='__main__':
    cherrypy.quickstart(PerleServer('example.db'), config="serveur0.conf")
