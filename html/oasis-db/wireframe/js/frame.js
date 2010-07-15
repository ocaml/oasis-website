function selectClass(t){
	$(".selected").removeClass("selected");
	$("#"+t.id).addClass("selected");
}