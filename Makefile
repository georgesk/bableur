CHERRYPY_PATH = $(HOME)/.local/lib/python2.7/site-packages/CherryPy-3.2.2-py2.7.egg/cherrypy

all : doc/html/index.html install-cherrypy

install-cherrypy: 
	$(MAKE) install --directory=CherryPy-3.2.2

clean:
	rm -rf *~

doc/html/index.html: bableur.js
	mkdir -p doc/html
	jsdoc --directory=doc/html bableur.js

.PHONY: all install-cherrypy