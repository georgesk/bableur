

/**
 * Fonction pour traduire un texte court en appelant le service mymemory.translated.net
 * @param original l'identifiant d'un textarea contenant l'original
 * @param l1 langue d'origine
 * @param l2 langue cible
 * @param traduction l'identifiant d'un textarea pour la traduction
 */
function traduire(original,l1,l2,traduction){
    var o = $('#'+original);
    var t = $('#'+traduction);
    var langues = l1+'|'+l2;
    t.val("");
    t.css("background-color","rgb(180,180,180)");
    $("*").css("cursor", "progress") ; // devrait afficher un cuseur d'attente
    $.getJSON(
	'http://mymemory.translated.net/api/get', 
	{ q: o.val(), langpair : langues },
	function(data){
	    t.val(data.responseData.translatedText);
	}
    );
    $("*").css("cursor", "auto") ; // remet le curseur normal
    t.css("background-color","white");
}

