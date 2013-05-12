all : doc/html/index.html

clean:
	rm -rf *~

doc/html/index.html: bableur.js doxy.cfg
	mkdir -p doc/html
	jsdoc --directory=doc/html bableur.js

