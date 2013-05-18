CHERRYPY_PATH = $(HOME)/.local/lib/python2.7/site-packages/CherryPy-3.2.2-py2.7.egg/cherrypy

all: install

install: $(CHERRYPY_PATH)/__init__.py

$(CHERRYPY_PATH)/__init__.py: setup.py
	python setup.py build
	python setup.py install --user

.PHONY: all install
