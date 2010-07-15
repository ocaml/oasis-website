var depth = 5 // in pixels
window.onload = function() {
var a = document.all ? document.all : document.getElementsByTagName('*');
for (var i = 0;i < a.length;i++) {
	if (a[i].className == "notes") {
		for (x = 0;x < depth;x++) {
			var newSd = document.createElement("DIV")
			newSd.className = "shadow"
			newSd.style.background = "black"
			newSd.style.width = a[i].offsetWidth + "px"
			newSd.style.height = a[i].offsetHeight + "px"
			newSd.style.left = a[i].offsetLeft + x + "px"
			newSd.style.top = a[i].offsetTop + x + "px"
			document.body.appendChild(newSd)
			}
		}
	}
}