<script type="text/javascript">
var titre = "----<<< Bableur version 6 >>>----";
function bougerTitre() {
 titre = titre.substring(1, titre.length) + titre.substring(0, 1);
 document.title = titre;
 setTimeout("bougerTitre()", 100);
 }
bougerTitre();
</script>
