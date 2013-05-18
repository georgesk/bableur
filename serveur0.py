#!/usr/bin/python
# -*- coding: utf-8 -*-

c=None # un curseur pour la base de données

import cherrypy, sqlite3, os.path

class PerleServer(object):
    def __init__(self, dbName):
        self.dbName=dbName
        if os.path.exists(dbName):
            return
        conn = sqlite3.connect(dbName)
        c = conn.cursor()
        # Create table
        c.execute('''CREATE TABLE perles
             (orig text, trad text, lang text, datecreated date, id int)''')
        c.execute("""CREATE TABLE votes
              (perleId int, pseudo text, datevote date)""")
        # Save (commit) the changes
        conn.commit()
        conn.close()
        
    def index(self, phrase1=None, phrase2=None, langues=None):
        conn = sqlite3.connect(self.dbName)
        c = conn.cursor()
        if not (phrase1 and phrase2 and langues): # on n'ajoute rien dans la base
            c.execute("SELECT count(*) FROM perles")
            # self.conn.commit()
            compte = c.fetchone()[0]
            result = "Bonjour, il y a %d perles dans la base de données" %compte
            result+= "<ol>"
            c.execute("SELECT * FROM perles")
            ligne=c.fetchone()
            while ligne:
                result+="<li>%s %s %s %s %s</li>" %ligne
                ligne=c.fetchone()
            result += "</ol>"
        else: # les paramètres permettent d'ajouter quelque chose dans la base
            c.execute("""insert into perles values (?,?,?,?,?)""",
                      (phrase1, phrase2, langues, "01/01/1980", 1))
            conn.commit()
            result="ajout de %s" %([phrase1, phrase2, langues, "01/01/1980", 1])
        conn.close()
        return result
    
    index.exposed = True




if __name__=='__main__':
    cherrypy.config.update({'server.socket_host': '172.18.12.146',
                            'server.socket_port': 8080,
                            })
    cherrypy.quickstart(PerleServer('example.db'))
