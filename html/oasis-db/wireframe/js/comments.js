// Author : Dhanesh
jQuery.fn.center = function () { 
    this.css("position","absolute"); 
    this.css("top", ( $(window).height() - this.height() ) / 2+$(window).scrollTop() + "px"); 
    this.css("left", ( $(window).width() - this.width() ) / 2+$(window).scrollLeft() + "px"); 
    return this; 
}
var comment; 
function Comments(){
	this.currentEditElement='';
	this.leftPos	= '';
	this.topPos		= '';
	this.startLeft;
	this.startTop;
	this.isEditMode	= 'no';
	this.isLoggedIn;
	this.wireframeId;
	this.commentId = '';
	this.commentsMode;
	comment = this;

	this.closeMessageBox = function (){
		if(comment.isEditMode=='yes'){
			$("#bubble_"+comment.commentId).css("left",comment.startLeft);
			$("#bubble_"+comment.commentId).css("top",comment.startTop);
		}
		$("#box1").hide();
		this.checkAnyPopupsExists();
		comment.isEditMode = 'no';
		comment.removeInitialBubble();
		return false;
	}

	this.checkAnyPopupsExists = function(){ //hiding the bottom popup menu if opened
		if($('#commentPopUp').css("display")=='block'){ 
			$("#commentPopUp").slideUp();
		}
	}

	this.bubbleClick = function(obj){// Later enhancement :  Use Jquery function offset() to get the left and top
		comment.currentEditElement 	= obj.id;
		comment.leftPos 			= obj.offsetLeft;
		comment.topPos 				= obj.offsetTop;
		comment.commentId 			= obj.title;
		$("#box1").show();	
		this.showMessageBox('sticky');
		$("#box1").css({ left:comment.leftPos, top:comment.topPos });
		comment.showCommentsFromList(comment.leftPos, comment.topPos, comment.currentEditElement, comment.commentId, comment.wireframeId);
	}

	this.showMessageBox = function (mode){
		$("#box1").show();
		if(mode=='move'){
			$("#box1").easydrag();
			$("#box1").setHandler('handler');
			$("#box1").ondrop(function(e, element){
				comment.checkCordinatest($("#box1"));
			});
		}else{
			$("#box1").dragOff();
			$('#handler').css({ cursor:"default" });
		}
	}
	
	// Edit message.
	this.editMessage  = function (){
		comment.startLeft = comment.leftPos;
		comment.startTop = comment.topPos;
		comment.isEditMode = 'yes';
		$.post("../comments.ajax.php", { mode: "editMessage", commentId:comment.commentId },
		function(response){
			var data = comment.filterResponse(response);
			$("#messageList").fadeOut(300, function () {
				$("#content").fadeIn(300, function () { 
					$("#subject").val(data[0].Subject);
					$("#message").val(data[0].Message);	
					$("#hidCommentId").val(comment.commentId);					
				});
			});			
		});
		$("#box1").easydrag();
		$("#box1").setHandler('handler');
		$("#box1").ondrop(function(e, element){
			comment.editDrop($("#box1"));
		});
		return false;
	}

	this.editDrop = function (drop){
		$('#'+this.currentEditElement).remove();
		var newLeft   = parseInt(drop.css("left"))-10;
		var newTop    = parseInt(drop.css("top"))-10;
		comment.leftPos = newLeft;
		comment.topPos = newTop;
		var newDiv =  ('<div style="z-index:1000002; position:absolute; left:'+newLeft+'px; top:'+newTop+'px; cursor:pointer;"  id="'+this.currentEditElement+'" title="'+comment.commentId+'" onclick="return objComments.bubbleClick(this);"></div>');
		$('body').append(newDiv); 
		$('#'+this.currentEditElement).addClass("messageBubbles");
	}
	
	this.checkCordinatest = function(droppable){
		var box_left   	= parseInt(droppable.css("left"));
		var box_top    	= parseInt(droppable.css("top"));
		this.leftPos 	= box_left;
		this.topPos 	= box_top;
		comment.initialBubble(box_left,box_top);
	}

	/*List comments*/
	this.showCommentsList = function(){
		$("#commentPopUpList").html('<p>Loading comments...</p>');
		$("#commentList").addClass("current");
		$("#addComment").removeClass("current");
		$("#hideAllComment").removeClass("current");
		$("#commentPopUp").slideDown();
		comment.loadWireframeComment();
		return false;
	}

	this.loadWireframeComment = function (){ // Load comments
		$.post("../comments.ajax.php", { mode: "LoadWireframeComment" },
		function(data){
			if(data){
				$("#commentPopUpList").html(data);
			}else{
				$("#commentPopUpList").html('<p style="color:red;">No comments...</p>');
			}
		});	
	}
	
	this.showCommentsFromList = function (left,top,currentBubbleId,commentId, wireframeId){
		var pOffset = $("#bubble_"+commentId).offset().top;
		$.scrollTo("#bubble_"+commentId, pOffset);
		$("#messageList").html('<span class="listError">Loading.....</span>');
		var d = new Date()
		var UTCDiff = d.getTimezoneOffset();
		comment.commentId = commentId;
		comment.currentEditElement 	= currentBubbleId;
		$.post("../comments.ajax.php", { mode: "wireframeReply", wireframeId: wireframeId, UTCDiff:UTCDiff, commentId:commentId },
		function(response){
			var data = comment.filterResponse(response);
			if(data){
				$("#loginForm").remove();
				if(comment.isLoggedIn=='no'){
					$('#form2').html(comment.loginFormJs()); 
				}
				$("#messageList").html(data['data']);
				$("#handler").html(data['subject']);
				$(".commentReplyList").animate({ scrollTop: $(".commentReplyList").attr("scrollHeight") - $('.commentReplyList').height() }, 1000);
			}else{
				$("#messageList").html('<p style="color:red;">No messages...</p>');
			}
		});
		$("#content").hide();
		$("#messageList").show();
		
		var leftOff = parseInt(left)+10;
		var topOff = parseInt(top)+10;
		$("#box1").show();	
		this.showMessageBox('sticky');
		if ((leftOff==10) && (topOff==10)){ // This is for the bubble and popup box have 10px difference, to view the bubbles  even when placing the box. 
			$("#box1").center(); 
		}else{
			$("#box1").css({ left:leftOff, top:topOff });
		}
		return false;
	}
	
	this.showHideBubbles = function(mode){
		if(mode=='hide'){
			$("li#hideAllComment a").html("Show All Comment");
			 $(".messageBubbles").fadeOut(300);
			 comment.closeMessageBox();
		}else{
			$("li#hideAllComment a").html("Hide All Comment");
			 $(".messageBubbles").fadeIn(300);
		}
		$("#commentList").removeClass("current");
		$("#addComment").removeClass("current");
		$("#hideAllComment").addClass("current");
	}
	
	this.addComments = function(){
		comment.isEditMode = 'no';
		comment.leftPos = 0;
		comment.topPos 	= 0;
		if($('#isNewUser').is(":checked")==true){
			$('#isNewUser').attr('checked', false);
			$('#signInNameHolder').css("display","none");
			
		}
		comment.commentsMode='comments';
		$("#hidCommentId").val('');
		$("#box1").show();
		$("#messageList").html('');
		$("#commentList").removeClass("current");
		$("#addComment").addClass("current");
		$("#hideAllComment").removeClass("current");
		if(comment.isLoggedIn=='yes'){
			$("#content").show();
			$("#handler").html('Drag here to target your comment.');
		}
		this.showMessageBox('move');
		$("#box1").center(); 
		this.clearFormFields('message');
		var offset = $('#box1').offset();
		comment.initialBubble(offset.left,offset.top);
	}
	
	this.clearFormFields = function(formType){
		if(formType=='message'){
			$("#subject").val('');
			$("#message").val('');
		}
	}
	
	this.closeCommentPopUp = function(){
		$("#commentPopUp").slideUp();
		return false;
	}
	
	this.addWireframeComments = function (){
		var subject =  $("#subject").val();
		var message =  $("#message").val();
		if(subject==""){
			$("#subject").addClass("textErr");
			return false;
		}else{
			$("#subject").removeClass("textErr");
		}
		if(message==""){
			$("#message").css("border","1px solid red");
			return false;
		}else{
			$("#message").css("border","1px solid black");
		}
		comment.lockForm('content');
		var hidCommentId =  $("#hidCommentId").val();
		$.post("../comments.ajax.php", { mode: "CUDWireframeComment", subject:subject, message:message,left:comment.leftPos, top:comment.topPos, hidCommentId:hidCommentId },
		function(response){
			var data = comment.filterResponse(response);
				comment.startLeft 	= comment.leftPos;
				comment.startTop 	= comment.topPos;
			if(data['arrResponseReturn']['phpResponseCode']=='401'){
				if ((comment.leftPos!="") && (comment.topPos!="")){ // Creating bubbles while adding a comment.
					comment.commentId = data['arrResponseReturn']['phpCommentId'];
					var newCommentBubble =  ('<div  style="z-index:1000002; position:absolute; left:'+comment.leftPos+'px; top:'+comment.topPos+'px; cursor:pointer;"  id="bubble_'+comment.commentId+'" title="'+comment.commentId+'" onclick="return objComments.bubbleClick(this);" class="messageBubbles">&nbsp;</div>');
					$('body').append(newCommentBubble); 
				}
				comment.closeMessageBox();
			} else if(data['arrResponseReturn']['phpResponseCode']=='403'){
				comment.showCommentsFromList(comment.leftPos,comment.topPos,comment.currentEditElement,hidCommentId,comment.wireframeId);
			}
			comment.unlockForm();
			comment.removeInitialBubble();
		});
		return false;	
	}
	
	this.doLoginFromReply = function(){
		if(comment.commentsMode=='comments'){
			comment.checkLogin('comments');
			comment.commentsMode="";
		}else{
			comment.checkLogin('reply');
		} 
	}
	
	this.doLoginComments = function(){
		comment.checkLogin('comments');
	}
	
	this.checkLogin = function(loginFrom){
		if(comment.validateSignIn()==true){
			var email 		=  $("#signInEmail").val();
			var password	=  $("#signInPassword").val();
			var name 		=  $("#signInName").val();
			var newUser 	= $('#isNewUser').is(":checked")?1:0;
			$.post("../comments.ajax.php", { mode: "checkLogin", email:email, password:password, name:name, newUser:newUser },
			function(response){
				var data = comment.filterResponse(response);
				if(data['phpResponseCode'] != '101'){
					comment.showLoginBoxMessage(data['phpResponseString'])
				}else{
					$("#logoffBtn").attr('title','You are logged in as '+email+' Click here to sign-off from comments module');
					$("#loginForm").fadeOut(300, function () {
						comment.isLoggedIn = 'yes';
						$("#logoffBtn").fadeIn(300);
						$("#messageForm").fadeIn(300);
						if(loginFrom=='reply'){
							$(".commentReplyList").append(comment.replyFormJs());
							$(".commentReplyList").animate({ scrollTop: $(".commentReplyList").attr("scrollHeight") - $('.commentReplyList').height() }, 1000);
						}else if(loginFrom=='comments'){
							$('#content').css("display","block");
							$("#handler").html('Drag here to target your comment.');
						}
					});
				}
			}); 
		}
		return false;
	}
	
	this.toggleLogin = function(newUser){
		if($('#isNewUser').is(":checked")){
			$('#signInNameHolder').css("display","block");
		}
		else{
			$('#signInNameHolder').css("display","none");
		}
	}
	
	this.validateSignIn = function(){
		//Validation
		var signInPassword = $("#signInPassword");
		var signInEmail = $("#signInEmail");
		var err = false;
		var errMsg="";
		if(!(/(^([_a-z0-9-]+)(\.[_a-z0-9-]+)*@([a-z0-9-]+)(\.[a-z0-9-]+)*(\.[a-z]{2,4})$)/i).test(signInEmail.val())){
			err = true;
			errMsg = "Not a valid email";
			signInEmail.addClass('textErr');
			signInEmail.focus();
		}else{
			signInEmail.removeClass('textErr');
		}
		if(!$("#signInPassword").val()){
			err = true;
			$("#signInPassword").addClass('textErr');
			$("#signInPassword").focus();
			errMsg = "Password cannot be null";
		}else{
			if($("#signInPassword").val().length<4){
				err = true;
				$("#signInPassword").addClass('textErr');
				$("#signInPassword").focus();
				errMsg = "Password must be atleast 4 characters long.";				
			}else{
				$("#signInPassword").removeClass('textErr');
			}
		}
		if($('#isNewUser').is(":checked")){
			if(!$("#signInName").val()){
				err = true;
				$("#signInName").addClass('textErr');
				$("#signInName").focus();
				errMsg = "Name cannot be null.";
			}else{
				$("#signInName").removeClass('textErr');
			}
		}
		if(err==true){
			comment.showLoginBoxMessage(errMsg);
			return false;
		}
		return true;
	}

	this.showLoginBoxMessage = function (message){
		$("#errorBox").css("visibility","visible");
		$('#errorBox').html(message);
	}
	
	this.filterResponse = function(responseData) {
		var response = responseData;
		try	{
			response = response.replace(/\r/g, "\\r");
			response = response.replace(/\n/g, "\\n");
			response = response.replace(/&quot;/g, '\\"');
			response = response.replace(/&amp;/g, '\\&');
			response = eval("(" + response + ")");
			return response;
		} catch(err) {
			var response = responseData;
			try	{
				response = eval("(" + response + ")");
				return response;
			} catch(err) {
				return false;
			}
			return false;
		}
	}
	
	this.messageForm = function(){
		var str ='<div class="messageForm" id="messageForm">';
			str +=	'<p><label for="subject">Subject</label><input type="text" id="subject" name="subject" value="" maxlength="60" class="textInput" /></p>';			  
			str +=	'<p><label for="message">Comments</label><br/><textarea rows="5" cols="22" id="message" class="textarea"></textarea></p>';			  
			str +=	'<div class="buttonsDiv">';			  
			str +=	'<input type="submit" id="btnAddWireframeComments"  value="Submit" class="button"  onClick="return objComments.addWireframeComments();" />';
			str +=	'<input type="button" value="Cancel"  class="button"  onClick="return objComments.closeMessageBox();" />';	
			str +=	'<input type="hidden" value=""  id="hidCommentId"  />';
			str +=	'</div></div>';			  
		return str;	
	}
	
	this.loginFormJs = function(){
		var loginStr =	'<div class="loginForm" id="loginForm">';
			loginStr +=	'<p id="errorBox">&nbsp;</p>';
			loginStr += '<p class="loginHead">Login to Add or Reply to Comments</p>';
			loginStr +=	'<p><label for="signInEmail">Email</label><input type="text" id="signInEmail" name="signInEmail" value="" class="smallTextInput" /></p>';
			loginStr +=	'<p><label for="signInPassword">Password</label><input type="password" id="signInPassword" name="signInPassword" value="" class="smallTextInput" /></p>';
			loginStr +=	'<p id="signInNameHolder"><label for="signInName">Name</label><input type="text" id="signInName" name="signInName" value="" class="smallTextInput" /></p>';
			loginStr +=	'<p class="checkbox"><label for="isNewUser"><input onclick="return objComments.toggleLogin();" name="isNewUser" id="isNewUser" value="y" type="checkbox">No, I am a new user</label></p>';
			loginStr +=	'<div class="buttonsDiv">';
			loginStr +=	'<input type="button" id="btnLogin"  value="Submit" class="button"  onClick="return objComments.doLoginFromReply();" />';
			loginStr +=	'<input type="button" value="Cancel"  class="button"  onClick="return objComments.closeMessageBox();" />';
			loginStr +=	'</div>';
			loginStr +=	'</div>';
			return loginStr;
	}
	
	this.replyFormJs = function(){
		var replyStr  =	'<div id="replyContent" >';
            replyStr +=    '<form name="form1" method="post" id="form3">';
			replyStr +=    '<p><label for="reply">Reply</label><br/><textarea rows="5" cols="22" id="replyMessage" class="textarea"></textarea></p>';
			replyStr +=    '<div class="buttonsDiv">';
			replyStr +=    '<input type="submit" id="replyBtn"  value="Submit" class="button"   onClick="return objComments.replyMessage();"  />';
			replyStr +=    '<input type="button" value="Cancel"  class="button"   onClick="return objComments.closeMessageBox();" />';
			replyStr +=    '</div></form></div>';
		return replyStr;
	}
	
/*Delete comments*/
	this.deleteComments = function (commentId) {
		var msgAlert = 'Are you sure you want to delete this comments! ';
		if(confirm(msgAlert)){
			$.post("../comments.ajax.php", { mode: "deleteMessage", commentId:commentId },
			function(response){
				var data = comment.filterResponse(response);
				if(data['arrResponseReturn']['phpResponseCode']=='404'){
					$("#bubble_"+commentId).fadeOut('slow', function() {
						$("#"+comment.currentEditElement).remove();
					});
					comment.closeMessageBox();
				}
			});
		}
	}
	
/*	Reply comment */	
	this.replyMessage = function(){
		replyMsg = $("#replyMessage").val();
		if(replyMsg==""){
			$("#replyMessage").css("border","1px solid red");
			return false;
		}else{
			$("#replyMessage").css("border","1px solid black");
		}
		comment.lockForm('commentsListWrapper');
		if(comment.wireframeId && comment.commentId){
			$.post("../comments.ajax.php", { mode: "replyComment", commentId: comment.commentId, wireframeId : comment.wireframeId, replyMsg:replyMsg },
			function(response){
				var data = comment.filterResponse(response);
				if(data['arrResponseReturn']['phpResponseCode']=='405'){
					comment.showCommentsFromList(comment.leftPos, comment.topPos, comment.currentEditElement, comment.commentId, comment.wireframeId);
				}
				comment.unlockForm();
			});	
		}
		return false;
	}
	
	this.lockForm = function(elementId){
		switch (elementId){
			case "content": 
				$("#content").append("<div id='pageLock'></div>");
			break;
			case "commentsListWrapper": 
				$("#commentsListWrapper").append("<div id='pageLock'></div>");
			break;
			default : 
		}
	}
	
	this.unlockForm = function(){
		$('#pageLock').remove();
	}
	
	this.initialBubble = function(initLeft,initTop){
		comment.removeInitialBubble();
		var initBubble =  ('<div style="z-index:1000002; position:absolute; left:'+(initLeft-10)+'px; top:'+(initTop-10)+'px; cursor:pointer;"  class="messageBubblesInit" id="initBubble"></div>');
		$('body').append(initBubble); 
	}
	
	this.removeInitialBubble = function(){
		if($('#initBubble').css("display")=='block'){ 
			$("#initBubble").remove();
		}
	}
	
	this.logout = function(){
		var msgAlert = 'Logging off from comments will also log you off from the iplotz application.\nAre you sure you want to continue? ';
		if(confirm(msgAlert)){
			$.post("../comments.ajax.php", { mode: "logoff" },
			function(response){
				var data = comment.filterResponse(response);
				if(data['arrResponseReturn']['logout']==true){
					$("#logoffBtn").fadeOut(300);
					//comment.isLoggedIn='no';
					location.reload();
				}
			});
		}
	}

	
	
}

objComments = new Comments();
$(document).ready(function() {
	$("#icoDown").click(
		function (){
			$("#footerMenu").slideUp("slow", function () {
				$("#icoDown").fadeOut(300, function () {
					$("#icoUp").fadeIn(300, function () { });
				});
			});
	});
	
	$("#icoUp").click(
		function (){
			$("#footerMenu").slideDown("slow", function () {
				$("#icoUp").fadeOut(300, function () {
					$("#icoDown").fadeIn(300, function () { });
				});
			});
		});
	
	$("#hideAllComment").toggle(
		function () {
			objComments.showHideBubbles('hide');
		},
		function () {
			objComments.showHideBubbles('show');
		}
	);
	
	$('#commentList').click(function() {
		objComments.showCommentsList();
		return false;
	});
	
	$('#addComment').click(function() {
		objComments.addComments();
		return false;
	});
	$('#btnAddWireframeComments').click(function() {
		objComments.addWireframeComments();
		return false;
	});
	$('#logoffBtn').click(function() {
		objComments.logout();
		return false;
	});
	
	
	$("#commentList a").qtip({
		position: {
			corner: {target: 'topMiddle',	tooltip: 'bottomLeft'}
	    },
		style: {
			tip: true, background: '#131313', color: '#fff', 'font-size': '11px',		
			border: {width: 7,	radius: 5, color: '#131313'	}
		}
	});  
	
	
	$("#hideAllComment a").qtip({
		position: {
			corner: {target: 'topMiddle',	tooltip: 'bottomLeft'}
	    },
		style: {
			tip: true, background: '#131313', color: '#fff', 'font-size': '11px',		
			border: {width: 7,	radius: 5, color: '#131313'	}
		}
	}); 
	
	/*
	$("#totalcomments").qtip({
		position: {
			corner: {target: 'topMiddle',	tooltip: 'bottomLeft'}
	    },
		style: {
			tip: true, background: '#131313', color: '#fff', 'font-size': '11px',		
			border: {width: 7,	radius: 5, color: '#131313'	}
		}
	}); 
	
 	$("#targetedcomments").qtip({
		position: {
			corner: {target: 'topMiddle',tooltip: 'bottomLeft'}
	   },
	   style: {
			tip: true, background: '#131313',color: '#fff',	'font-size': '11px',
			border: {width: 7,radius: 5,color: '#131313'}
		}
	});  

	$("#floatingcomments").qtip({
		position: {
			corner: {target: 'topMiddle',tooltip: 'bottomLeft'	}
	   },
	   style: {
			tip: true,background: '#131313',color: '#fff','font-size': '11px',
			border: {width: 7,	radius: 5,	color: '#131313'}
		}
	}); */

	$("#logoffBtn").qtip({
		position: {
			corner: {target: 'topMiddle',tooltip: 'bottomLeft'	}
	   },
	   style: {
			tip: true,background: '#131313',color: '#fff','font-size': '11px',
			border: {width: 7,	radius: 5,	color: '#131313'}
		}
	}); 

});






