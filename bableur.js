
/**
 * Fonction pour traduire un texte court en appelant le
 * service mymemory.translated.net
 * @param areaIds liste d'ids de conteneurs de texte
 * @param l liste de langues
 **/
function traduire(areaIds, l){
    if (l.length < 2) return; // s'il reste moins de 2 langues, on a fini !
    var o = $('#'+ areaIds[0]);
    var t = $('#'+ areaIds[1]);
    var langues = l[0]+'|'+l[1];
    var nextAreaIds = areaIds.slice(1);
    var nextL       = l.slice(1);
    t.val("");                                     // efface la traduction
    setWaiting(t, true);                           // début de l'attente
    $.getJSON(
	'http://mymemory.translated.net/api/get',  // service de traduction
	{ q: o.val(), langpair : langues })        // paramètres
	.done(function(data){                      // rappel en cas de réussite
	    var decoded =                          // décode les entités HTML
		$("<div/>").html(data.responseData.translatedText).text();
	    t.val(decoded);                        //écrit la traduction
	    setWaiting(t, false);                  // fin de l'attente 
	    traduire(nextAreaIds, nextL);          // appel récursif
	})
	.fail(function(){                         // rappel en cas d'échec
	    t.val("** Échec de la traduction **");// message d'erreur
	    setWaiting(t, false);                 // fin de l'attente
	    return;
	});
    return;
}

/**
 * Fonction pour faire apparaître un élément comme "en attente"
 * @param el l'élément à modifier
 * @param state booléen ; vrai => "en attente", faux => "normal"
 **/
function setWaiting(el,state){
    if(state){
	setTimeout(function(){
	    el.css("cursor", "progress") ; 
	    el.css("background-color","rgb(230,230,230)");
	},0);
    } else {
	setTimeout(function(){
	    el.css("cursor", "auto") ; 
	    el.css("background-color","white");
	},0);
    }
}
