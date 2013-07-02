
/**
 * Fonction pour traduire un texte court en appelant le
 * service http://mymemory.translated.net
 * @param listenum une liste de numéros de textes à traduire
 * @param l liste de langues correspondant à ces textes
 * @param endl null ou la langue de départ si on veut une
 *  traduction circulaire
 **/
function traduire(listenum, l, endl){
  var o = $('#area'+ listenum[0]);
  var t = $('#area'+ listenum[1]);
  var n = listenum[1];              // numéro du texte destination
  var langues = l[0]+'|'+l[1];

  if (l.length == 0) return;        // traduction circulaire finie
  if (l.length == 1) {              // dernière langue
    if (endl === undefined) return; // traduction non circulaire
    else {                          // traduction circulaire demandée
      t = $('#area0');
      n = 0;
      langues = l[0]+'|'+endl;
    }
  }

  var nextList = listenum.slice(1);
  var nextL       = l.slice(1);
  var oldText = t.val();
  t.val("");
  setWaiting(t, true);                       // début de l'attente
  $.getJSON(
    'http://mymemory.translated.net/api/get',// service de traduction
    { q: o.val(),                            // paramètres
      langpair : langues,
      de: "georges.khaznadar@free.fr"})      // dont un e-mail valide
    .done(function(data){                    // rappel en cas de réussite
      var decoded =                          // décode les entités HTML
      $("<div/>").html(data.responseData.translatedText).text();
      t.val(decoded);                        //écrit la traduction
      stackOldText(oldText, decoded, n);     // range l'ancien texte
      setWaiting(t, false);                  // fin de l'attente 
      traduire(nextList, nextL, endl);       // appel récursif
    })
    .fail(function(){                        // rappel en cas d'échec
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

// implementation d'un système pour formater les chaînes de caractères
// récupéré de http://stackoverflow.com/questions/610406/
// titre : javascript-equivalent-to-printf-string-format
if (!String.prototype.format) {
  String.prototype.format = function() {
    var args = arguments;
    return this.replace(/{(\d+)}/g, function(match, number) { 
      return typeof args[number] != 'undefined'
        ? args[number]
        : match
      ;
    });
  };
}

/**
 * Conserve, si on veut, un ancien texte et son remplaçant.
 * @param ancienTexte l'ancien texte
 * @param nouveauTexte le nouveau texte
 **/
function conserver(ancienTexte, nouveauTexte){
  var ok    = confirm("Voulez-vous conserver ce texte ?\n"+ancienTexte+"\n   ---->\n"+nouveauTexte);
  if (ok) {
    var langues = $("#circulaire").val();
    var archiveCSV='"{0}"; "{1}"; "{2}"'
      .format(ancienTexte,nouveauTexte,langues);
    var params="?phrase1={0}&phrase2={1}&langues={2}"
      .format(encodeURIComponent(ancienTexte),
              encodeURIComponent(nouveauTexte),
              encodeURIComponent(langues));
    var lien=$("<a>",{target: "perles",
                      href: "http://georges.khaznadar.fr/perles/"+params})
      .append($("<img>",{src: "perle.gif",
                         alt: "Perle",
                         title: "Cliquer ici pour conserver cette perle",
                         height: "12px"}));
    $("#archive").append($("<li>").text(archiveCSV).append(lien));
  }
}

/**
 * Fonction pour faire apparaître un élément comme "en attente".
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
 * qui correspondent à une liste de langues.
 * @param l une liste de langues, comme ['fr', 'en', ...]
 * @param targetId l'identifiant d'un élément où insérer les
 *  formulaires.
 **/
function bableur_init(l, targetId){
  var target=$("#"+targetId);
  /******************************
   * boîte pour définir la chaîne de langues
   *****************************/
  target.append($("<div>", {id: "langBox",
                            class: "blancTransparent"})
		.append($("<p>",{class: "langBoxTitle"}).text("Choix des langues"))
		.append($("<p>",{class: "langBoxHelp"}).text("Tirez-glissez les étiquettes.")
                        .append($("<br>"))
		        .append($("<input>",{
		          type: "button",
		          value: "Refaire la chaîne de traduction",
                          onclick: "chaineTrad_init();"
		        })))
                .append($("<fieldset>", {id: "langChain", // chaîne de langues
					 class: "colonne"})
			.append($("<legend>").text("Langues pour traduire")))
		.append($("<fieldset>", {id: "langHeap",  // tas de langues
					 class: "colonne"})
			.append($("<legend>").text("Langues en réserve")))
	       );
  lang_init();
  /******************************
   * boîte pour l'archivage de traductions
   *****************************/
  target.append($("<div>", {id: "archiveBox",
                            class: "blancTransparent1"})
		.append($("<h2>").text("archive de traductions"))
		.append($("<ol>", {class : "archive", id : "archive"}))
	       );
  /******************************
   * boîte pour les traductions
   *****************************/
  chaineTrad_init(l, target);
  /****************************
   * fait en sorte que les étiquettes mobiles de langues fonctionnent
   *************************/
  $( ".colonne" ).sortable({
    connectWith: ".colonne"
  });
  $( ".colonne" ).disableSelection();
}

/**
 * Initialisation de la chaîne de traductions.
 * @param l une liste de langues ; si cette liste est indéfinie, les
 *        langues définies par les étiquettes mobiles sont prises en compte
 * @param target un div où construire la chaîne de langues la première fois
 *        avant que la page n'ait été affichée
 **/
function chaineTrad_init(l, target){
  if (l == undefined) {
    var chaineTrad=$("#langChain").find(".drapeau");
    var l=Array();
    chaineTrad.each(function(i,val){
      l.push($(val).text());
    });
    if (l.length < 2){
      alert("Il faut deux langues au moins pour faire une traduction.\nAjoutez des langues dans la colonne de gauche.")
    }
    var trad = $("#translationBox"); // on récupère la boîte de traductions
    trad.empty();                    // et on la vide
  } else {                           // ou alors on crée la boîte de traductions
    var trad = $("<div>", {id: "translationBox",
                           class: "blancTransparent"})
    target.append(trad);
  }
  trad.append(roundTranslateButton(l));
  trad.append($("<br>"));
  for (var i=0; i < l.length; i++){
    trad.append(fsTraduction(l,i));
  }
  $("#area0").val("Entrez ici un texte à traduire");
}


/**
 * Crée un objet jQuery comprenant un bouton pour déclencher
 * une série circulaire de traductions.
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
      value: text,
      id : "circulaire"
    }
  );
  return button;
}

/**
 * Peuple les boîtes de "chaîne de langues" et "tas de langues"
 * avec des drapeaux mobiles par tirer-glisser.
 **/
function lang_init(){
  var langues=Array(
    "fr", "en", "es",
    "de","it","zh-cn"
  );
  insere_drapeau(langues[0],"langChain"); // trois langues pré-chargées
  insere_drapeau(langues[1],"langChain");
  insere_drapeau(langues[2],"langChain");
  for (var i=3; i< langues.length; i++){  // les autres langues
    insere_drapeau(langues[i],"langHeap");
  }
}

/**
 * Ajoute un drapeau dans une boîte.
 * @param lang l'identifiant de langue du drapeau
 * @param box l'identifiant du conteneur où ajouter le drapeau
 **/
function insere_drapeau(lang, box){
  var drapeau = new Drapeau(lang);
  $("#"+box).append(drapeau.ui);
}

/**
 * Drapeau sera utilisé comme une classe qu'on initialise avec
 * un identifiant de langue et qui offre pour l'interface utilisateur
 * une zone interagissant avec la souris
 * @param lang l'identifiant de langue utilisé par le constructeur
 **/
function Drapeau(lang){
  this.lang=lang;
  /*
   * le membre this.ui est un widget qui accepte le tirer-glisser
   */
  this.ui=$("<div>",{class: "drapeau",
		     title: "drapeau « "+lang+" » à tirer-glisser"
		    })
    .text(this.lang)
    .append($("<img>",{src             : "flags/"+lang+".png",
		       height          : "12px",
		       align           : "right",
		       alt             : "drapeau "+lang+" à tirer-glisser",
		      }
	     ));
}

/**
 * Crée un objet jQuery comprenant un bouton et un champ de texte
 * le champ de texte possède un identifiant numéroté : "area" +n.
 * En plus, une boîte avec une liste numérotée est ajouté pour
 * contenir les anciennes versions du texte.
 * @param l une liste de langues
 * @param n l'index sur la première langue à considérer dans la liste
 * @return l'objet jQuery prêt à servir
 **/
function fsTraduction(l,n){
  var fieldset;
  var legendText = "Langue : "+l[n]+" ";
  if (n == 0){
    legendText = "Langue de départ : "+l[n]+" ";
  }
  fieldset=$("<fieldset>",{class: "translator"});
  fieldset.append($("<legend>").text(legendText)
                  .append($("<img>",{src:"flags/"+l[n]+".png",
                                   height:"10px",
                                     alt:"drapeau "+l[n]}))
                 );
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
 * crée un script pour traduire d'une langue vers une autre
 * d'après une liste et un index. Si l'index pointe à la fin
 * de la liste, on traduit de la dernière vers la première langue.
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
 * crée un texte pour évoquer la traduction d'une langue vers une autre,
 * d'après une liste de langues et un index. Si l'index pointe à la fin
 * de la liste, on traduit de la dernière vers la première langue.
 * @param l une liste de langues
 * @param n index sur cette liste
 * @return le texte évoquant la traduction
 **/
function evoqueTraduire(l,n){
  var from = n
  var to   = (n+1) % l.length;
  return "Traduire : "+[l[from],l[to]].join(" -> ");
}


/* Réglage pour Emacs
   Local Variables:
   c-basic-offset: 2
   js-indent-level: 2
   indent-tabs-mode: nil
   End:
*/
