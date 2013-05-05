
/**
 * Fonction pour traduire un texte court en appelant le
 * service mymemory.translated.net
 * @param areaIds liste d'ids de conteneurs de texte
 * @param endl null ou la langue de départ si on veut une
 *  traduction circulaire
 * @param l liste de langues
 **/
function traduire(areaIds, l, endl){
    var o = $('#'+ areaIds[0]);
    var t = $('#'+ areaIds[1]);
    var langues = l[0]+'|'+l[1];

    if (l.length == 0) return;  // traduction circulaire finie
    if (l.length == 1) {        // dernière langue
	if (endl === undefined) return;     // traduction non circulaire
	else {                  // traduction circulaire demandée
	    t = $('#area0');
	    langues = l[0]+'|'+endl;
	}
    }

    var nextAreaIds = areaIds.slice(1);
    var nextL       = l.slice(1);
    t.val("");                                     // efface la traduction
    setWaiting(t, true);                           // début de l'attente
    $.getJSON(
	'http://mymemory.translated.net/api/get',  // service de traduction
	{ q: o.val(),                              // paramètres
	  langpair : langues,
	  de: "georges.khaznadar@free.fr"})        // dont un e-mail valide
	.done(function(data){                      // rappel en cas de réussite
	    var decoded =                          // décode les entités HTML
		$("<div/>").html(data.responseData.translatedText).text();
	    t.val(decoded);                        //écrit la traduction
	    setWaiting(t, false);                  // fin de l'attente 
	    traduire(nextAreaIds, nextL, endl);    // appel récursif
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
 * @param el l'objet jQuery à modifier
 * @param state booléen ; vrai => "en attente", faux => "normal"
 **/
function setWaiting(el,state){
    // l'usage de setTimeout permet de forcer la modification
    // immédiate de l'interface utilisateur ; sans ça les
    // changements de style n'ont pas lieu à temps.
    if(state){
	setTimeout(function(){
	    el.addClass("busy");
	},0);
    } else {
	setTimeout(function(){
	    el.removeClass("busy");
	},0);
    }
}

/**
 * La fonction bableur_init crée les formulaires avec des boutons
 * qui correspondent à une liste de langues
 * @param l une liste de langues, comme ['fr', 'en', ...]
 * @param targetId l'identifiant d'un élément où insérer les
 *  formulaires.
 **/
function bableur_init(l, targetId){
    var target=$("#"+targetId);
    target.append(roundTranslateButton(l));
    target.append($("<hr>"));
    for (var i=0; i < l.length; i++){
	target.append(fsTraduction(l,i));
    }
    $("#area0").text("Comme un vol de gerfauts hors du charnier natal, Fatigués de porter leurs misères hautaines ...");
}

/**
 * crée un objet jQuery comprenant un bouton pour déclencher
 * une série circulaire de traductions
 * l une liste de langues
 * @return l'objet jQuery prêt à servir
 **/
function roundTranslateButton(l){
    var text="Traduction circulaire : "+l.join(" -> ");
    var areaIds=Array();
    for(var i=0; i<l.length; i++) areaIds.push("area"+i);
    var script="traduire("+JSON.stringify(areaIds)+", "+JSON.stringify(l)+", '"+l[0]+"')";
    var button=$(
	"<input>",
	{ type: "button",
	  onclick: script,
	  value: text
	}
    );
    return button;
}


/**
 * crée un objet jQuery comprenant un bouton et un champ de texte
 * le champ de texte possède un identifiant numéroté "area" +n
 * @param l une liste de langues
 * @param n l'index sur la première langue à considérer dans la liste
 * @return l'objet jQuery prêt à servir
 **/
function fsTraduction(l,n){
    var fieldset;
    var legendText = "Langue : "+l[n];
    if (n == 0){
	legendText = "Langue de départ : "+l[n];
    }
    fieldset=$("<fieldset>",{class: "translator"});
    fieldset.append($("<legend>").text(legendText));
    fieldset.append($("<input>", 
		      {type: "button", 
		       value: evoqueTraduire(l,n),
		       onclick: invoqueTraduire(l,n)
		      })
		   );
    fieldset.append($("<br>"));
    fieldset.append($("<textarea>",
		      {cols: "40",
		       rows: "4",
		       id: "area"+n})
		   );
    return fieldset;
}

/**
 * crée un script pour traduire d'une langue vers un autre
 * d'après une liste et un index. Si l'index pointe à la fin
 * de la liste, on traduit du dernier vers la première langue
 * @param l une liste de langues
 * @param n index sur cette liste
 * @return le texte du script qui fait la traduction
 **/
function invoqueTraduire(l,n){
    var from = n
    var to   = (n+1) % l.length;
    var callback="traduire("+
	JSON.stringify(["area"+from, "area"+to])+
	", "+
	JSON.stringify([l[from],l[to]])+
	");"
    return callback;
}

/**
 * crée un scripttexte pour évoquer d'une langue vers un autre
 * d'après une liste et un index. Si l'index pointe à la fin
 * de la liste, on traduit du dernier vers la première langue
 * @param l une liste de langues
 * @param n index sur cette liste
 * @return le texte évoquant la traduction
 **/
function evoqueTraduire(l,n){
    var from = n
    var to   = (n+1) % l.length;
    return "Traduire : "+[l[from],l[to]].join(" -> ");
}
