
/**
 * Fonction pour traduire un texte court en appelant le
 * service mymemory.translated.net
 * @param listenum une liste de numéros de textes à traduire
 * @param l liste de langues correspondant à ces textes
 * @param endl null ou la langue de départ si on veut une
 *  traduction circulaire
 **/
function traduire(listenum, l, endl){
    var o = $('#area'+ listenum[0]);
    var t = $('#area'+ listenum[1]);
    var n = listenum[1];        // numéro du texte destination
    var langues = l[0]+'|'+l[1];

    if (l.length == 0) return;  // traduction circulaire finie
    if (l.length == 1) {        // dernière langue
	if (endl === undefined) return;     // traduction non circulaire
	else {                  // traduction circulaire demandée
	    t = $('#area0');
	    n = 0;
	    langues = l[0]+'|'+endl;
	}
    }

    var nextList = listenum.slice(1);
    var nextL       = l.slice(1);
    var oldText = t.val();
    t.val("");
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
	    stackOldText(oldText, decoded, n);     // range l'ancien texte
	    setWaiting(t, false);                  // fin de l'attente 
	    traduire(nextList, nextL, endl);       // appel récursif
	})
	.fail(function(){                          // rappel en cas d'échec
	    t.val("** Échec de la traduction **"); // message d'erreur
	    setWaiting(t, false);                  // fin de l'attente
	    return;
	});
    return;
}

/**
 * empile l'ancien texte d'une traduction s'il est non vide, sous
 * le champ texte modifié.
 * @param oldtext l'ancien texte
 * @param newtext le nouveau texte
 * @param n le numéro du champ
 **/
function stackOldText(oldtext, newtext, n){
    if (oldtext.length > 0 && oldtext != newtext){
	var stack = $('#pile'+n);
	var li    = $("<li>", {class: 'lienDrole'})
	    .text(oldtext)
	    .click(function(){conserver(oldtext, newtext)});
	stack.prepend(li);
    }
}

/**
 * conserve si on veut un ancien texte et son remplaçant
 * @param ancienTexte l'ancien texte
 * @param nouveauTexte le nouveau texte
 **/
function conserver(ancienTexte, nouveauTexte){
    var ok    = confirm("Voulez-vous conserver ce texte ?\n"+ancienTexte+"\n   ---->\n"+nouveauTexte);
    if (ok) {
	var archiveCSV='"'+ancienTexte+'"; "'+nouveauTexte+'"';
	$("#archive").append($("<li>").text(archiveCSV));
    }
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
    /******************************
     * boîte pour l'archivage de traductions
     *****************************/
    target.append($("<div>", {id: "archiveBox"})
		  .append($("<h2>").text("archive de traductions"))
		  .append($("<ol>", {class : "archive", id : "archive"}))
		 );
    /******************************
     * boîte pour les traductions
     *****************************/
    var trad = $("<div>", {id: "translationBox"})
    target.append(trad);
    trad.append(roundTranslateButton(l));
    trad.append($("<br>"));
    for (var i=0; i < l.length; i++){
	trad.append(fsTraduction(l,i));
    }
    $("#area0").val("Comme un vol de gerfauts hors du charnier natal, Fatigués de porter leurs misères hautaines ...");
}

/**
 * crée un objet jQuery comprenant un bouton pour déclencher
 * une série circulaire de traductions
 * l une liste de langues
 * @return l'objet jQuery prêt à servir
 **/
function roundTranslateButton(l){
    var listeCirculaire=l.slice(0); // recopie
    listeCirculaire.push(l[0]);     // circularisation
    var text="Traduction circulaire : "+listeCirculaire.join(" -> ");
    var listenum=Array();
    for(var i=0; i<l.length; i++) listenum.push(i);
    var script="traduire("+JSON.stringify(listenum)+", "+JSON.stringify(l)+", '"+l[0]+"')";
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
 * en plus, un conteneur <ol id='pileN'> est ajouté pour contenir
 * les anciennes versions du texte
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
    fieldset.append($("<ol>",{id : "pile"+n, class: "ancienneTraduction"}));
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
	JSON.stringify([from, to])+
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
