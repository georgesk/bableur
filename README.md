bableur
=======

Un logiciel parasitant les traducteurs automatiques, et pour faire de 
drôles de poésies.


Cahier de charges :
===================
Nous allons essayer de mettre en place une application qui accepte un
texte de 140 signes (pas plus si on veut utiliser des tweets).

Ce texte sera soumis à un traducteur automatique pour y faire un
aller-retour entre deux langues choisies "fr -> en" et "en -> fr", ou
encore pour faire une série de traductions ciculaire, par exemple :
"fr -> en", "en -> es" et "es -> fr".

L'utilisateur pourra spécifier les langues choisies.

L'utilisateur pourra enregistrer les "perles" quand elles apparaissent.

Usage :
=======
il suffit d'ouvrir le fichier bableur5.html, dans un navigateur.
On peut éditer une phrase à traduire dans un champ, et lancer la traduction.

Outils utilisés :
=================

Le traducteur automatique :
+++++++++++++++++++++++++++
Le but du projet est de jouer avec un traducteur automatique en
ligne. Les APIs de Google translate et Bing translate étant maintenant
payantes, on a cherché une API gratuite en mai 2013, qu'on a trouvée à
http://mymemory.translated.net/api/get


Les bibliothèques Javascript :
++++++++++++++++++++++++++++
Les bibliothèques jQuery et jQuery-UI ont été utilisées, pour
faciliter le développement de cette application : en effet, ces
bibliothèques offrent des facilités pour les échanges AJAX que fait le
service http://mymemory.translated.net/api/get, et d'autre part
jQuery-IU facilite la création de widgets interactifs, par exemple des
étiquettes de langues qu'on déplace à la souris pour faire la liste
des langues choisies. Ces bibliothèques ont été téléchargées depuis
https://github.com/jquery/jquery-ui

Ces bibliothèques sont distribuées sous une licence libre de type MIT.