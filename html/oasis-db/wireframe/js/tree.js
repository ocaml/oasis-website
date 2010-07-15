function showNode(image,no){	
	var img = "parent"+no;
	if(document.getElementById(no).style.display == 'none'){
		document.getElementById(no).style.display = 'block';
		document.getElementById(img).src = '../images/open_'+image+'.png';
	}else{
		document.getElementById(no).style.display = 'none';
		document.getElementById(img).src = '../images/close_'+image+'.png';

	}
}