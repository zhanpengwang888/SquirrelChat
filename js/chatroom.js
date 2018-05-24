$(function() {
/*
author：mr yang
webpage：www.seejoke.com
email:admin@seejoke.com
*/

	window['dandan'] = {}
	var ing_user; //current user -- get from server
	//all of this will ge from server by angular js
	channel_topic = "From server"; //now it is hard code, but should from database
	var file_list = ["some_file.py","some_file.txt"];
	var username = "mark";
	var channel_name ="#channel";
	var channel_topic;
	var users = ["mark","alice","Cici","Kris","WJP"];
	var admin= true;
	//to initialize browser
	//not change much probably
	function liulanqi() {
		var h = $(window).height();
		var w = $(window).width();
		$("#top").width(w);
		$("#foot").html(h);
		//control the format of whole page
		$(".box").height(h - 135);
		$("#mid_con").height(h - 255);
		$(".right_box").height(h - 134);
		$("#mid_say textarea").width(w - 480);
		
		//one more layer to prevent bad layout
		if ($(".box").height() < 350) {
			$(".box").height(350)
		}
		if ($("#mid_con").height() < 230) {
			$("#mid_con").height(230)
		}
		if ($(".right_box").height() < 351) {
			$(".right_box").height(351)
		}
		if ($("#mid_say textarea").width() < 320) {
			$("#mid_say textarea").width(320)
		}
		//keep the size of page to at least 800px, even page turns smaller will not change
		//but allow page to be wider than 800 page
		if (w <= 800) {
			$("#top").width(800);
			$("#body").width(800)
		} else {
			$("#body").css("width", "100%")
		}

		//the log can have scroll bar when it has too many contents
		$(".my_show").height($("#mid_con").height() - 30);
		//$(".my_show").scrollTop($(".con_box").height()-$(".my_show").height());//让滚动滚到最底端.在这里不加这句了，没多用，可能还卡

		//control the panel size of right panel
		r_h = $(".right_box").height() - 40 * 3;
		$("#right_top").height(r_h * 0.25)
		$("#right_mid").height(r_h * 0.45)
		$("#right_foot").height(r_h * 0.3)
	}
	window['dandan']['liulanqi'] = liulanqi; // add one member to window array dandan
	//I guess the window array will apply several features at once at the end of this big function

	//Time, can be deleted

	function mytime() {
		var now = (new Date()).getHours();
		if (now > 0 && now <= 6) {
			return "Time to sleep";
		} else if (now > 6 && now <= 11) {
			return "Good morning";
		} else if (now > 11 && now <= 14) {
			return "Good noon";
		} else if (now > 14 && now <= 18) {
			return "Good afternoon";
		} else {
			return "Good evening";
		}
	}
	window['dandan']['mytime'] = mytime;




	//when we resize or scroll the page, we will refresh browser by calling the initilization function again.  
	$(window).scroll(function() {
		dandan.liulanqi();
	}); //scroll happens
	$(window).resize(function() {
		dandan.liulanqi();
		return false;
	}); //window event
	dandan.liulanqi();

	//replace all enter to <br /> 
	// replace all the string element to special html element, to be able to show on screen
	function trim2(content) {
		var string = content;
		try {
			string = string.replace(/\r\n/g, "<br />")
			string = string.replace(/\n/g, "<br />");
		} catch (e) {
			alert(e.message);
		}
		return string;
	}
	//replace all space to &nbsp
	//same here, replace space by &nbsp
	function trim(content) {
		var string = content;
		try {
			string = string.replace(/ /g, "&nbsp;")
		} catch (e) {
			alert(e.message);
		}
		return string;
	}


	//show the number of file and users, same func
	function user_geshu() {
		var length1 = $(".ul_1 > li").length;
		var length2 = $(".ul_2 > li").length;
		$(".n_geshu_1").text(length1);
		$(".n_geshu_2").text(length2);
	}
	user_geshu()
	//alert(length1)

	//click to show the hidden member of file list and user list
	$(".h3").click(function() {
		$(this).toggleClass("click_h3").next(".ul").toggle(600);
	});

	//when mouse hover user, show the effect
	function hover_user($this) {
		$($this).hover(

		function() {
			$(this).addClass("hover");
		}, function() {
			$(this).removeClass("hover");
		});
	}

	//welcome page, should contain topic, channel name and user name -- get them from server
	//$("#top").html('<br />&nbsp;&nbsp;' + dandan.mytime() + ',' + username + ' <br />&nbsp;&nbsp;The topic of this channel is: ' + channel_topic);
	//$("#top").html('<br />&nbsp;&nbsp;' + dandan.mytime() + ',' + username + ' <br />&nbsp;&nbsp;Welcome to ' + channel_name  + '<br />&nbsp;&nbsp;The topic of this channel is: ' + channel_topic);
	//load the existing users
	// $(".ul").html(""); //clear the left message.
	// for (i = 0; i < $arr_user.length; i++) {
	// 	dandan.newuser('.ul_2', $arr_user[i], i); //put user into the current user list
	// }
	// $(".ul").html(""); //clear the left message.
 //    for (i = 0; i < users.length; i++) {
	// 	loaduser('.ul_2', users, i); //put user into the current user list
	// }
	// //also we need to load all the file list into the file list
 //    for (i = 0; i < file_list.length; i++) {
	// 	newfile('.ul_1', file_list, i); //put user into the current user list
	// }

	//my functions
	//get username
	//parse a list of string to a javascript object
	//Notes: the ul_1 should be file list, ul_2 should be user list
	function parse_string(raw_input) {
		var intermediate = raw_input.split(",");
		var temp = [];
		for(var i = 0; i < intermediate.length; i++) {
			if(intermediate[i] != "" && intermediate[i] != "None")
				temp.push(intermediate[i]);
		}
		return temp;
	}

	function loaduser($this, arr, i) {
		var id = "user";

		//alert(ing)
			//alert("最近聊天为真");
		console.log(arr[i]);
		$($this).prepend('<li id="' + id + i + '">' + arr[i] + '</li>');
		$('#' + id + i).click(function() {
			//title_newuser('title_' + id + ing, arr[0], arr[1]);
		}); //给按钮加事件
		hover_user('#' + id + i); //给经过触发	
		user_geshu(); //更新人数
	}

	function refresh_page() {
		var send_channel_name = channel_name.slice(1);
		$.get("/refresh/" + send_channel_name, function(url,status){
			console.log(url);
			console.log(status);
			window.location = url;
		});
	}
	//init the useful information of page
    function init_page() {

	    var username_temp = document.getElementById("username");
	    var admin_temp = document.getElementById("admin");
	    var users_temp = document.getElementById("users");
	    var files_temp = document.getElementById("files");
	    var channel_name_temp = document.getElementById("channel_name");
	    var channel_topic_temp = document.getElementById("channel_topic");
	    //var channel_list_temp = document.getElementById("channel_list"); // channel list should still comes forom
	    //store username
	    username = username_temp.textContent;
	    document.getElementById("username").style.display = "none";
	    //store admin
	    admin = admin_temp.textContent;
	    if(admin == "True")
	    	admin = true;
	    else
	    	admin = false;
	    document.getElementById("admin").style.display = "none";
	    //get raw data of users
	    var users_raw = users_temp.textContent;
	    document.getElementById("users").style.display = "none";
	    //get raw data of files
	    var files_raw = files_temp.textContent;
	    document.getElementById("files").style.display = "none";
	    //get channel name
	    channel_name = channel_name_temp.textContent;
	    document.getElementById("channel_name").style.display = "none";
	    //get topic of channel
	    channel_topic = channel_topic_temp.textContent;
	    document.getElementById("channel_topic").style.display = "none";
	    //console.log(admin)
	   //console.log(users_raw)
	    //console.log(files_raw)
	    //parse files and users
	    users = parse_string(users_raw);
	    file_list = parse_string(files_raw);
	    //console.log(users);
	    //console.log(file_list);
	    // file_list.push("test.txt");
	    // users.push("alice");
	    //console.log(users);
	    //console.log(files);
	    $(".ul").html(""); //clear the left message.
	    for (i = 0; i < users.length; i++) {
	    	//console.log("come here?");
			loaduser('.ul_2', users, i); //put user into the current user list
		}
		//also we need to load all the file list into the file list
	    for (i = 0; i < file_list.length; i++) {
	    	//console.log("come here?");
			newfile('.ul_1', file_list, i); //put user into the current user list
		}		
		//create some fancy icon to show you are an admin of this channel
		if(admin == true)
			$("#right_foot").html('<p><img src="../images/admin_icon.png" alt="head" /></p>' + "Admin:" + username);
		else
			$("#right_foot").html('<p></p>' + "Regular:  " + username);
		//have the head of channel
		//welcome page, should contain topic, channel name and user name -- get them from server
		$("#top").html('<br />&nbsp;&nbsp;' + dandan.mytime() + ', ' + username + ' <br />&nbsp;&nbsp;Welcome to ' + channel_name  + '<br />&nbsp;&nbsp;The topic of this channel is: ' + channel_topic);
		get_chats();
    }

    //helper function to parse the coming content of log
    function parse_content(raw_input) {
    	var temp = raw_input.split(" ");
    	//console.log(temp);
    	var raw_content = "";
		//console.log(raw_content);
		for(var i = 2; i < temp.length; i++) {
			raw_content = raw_content + temp[i] + " ";
		}
		//console.log(raw_content);
    	var content = raw_content.slice(0,raw_content.length);
    	//console.log(content);
    	return content;
    }
    //get chat log from server
    function get_chats() {
    	var send_channel_name = channel_name.slice(1);
    	$.getJSON("/get_chats/"+ send_channel_name, function(chats) {
    		//get the content from json
    		var chat_user_list = chats.users;
    		var chat_content_list = chats.contents;
    		//check the chat and user should be paired
    		var log_length;
			if(chat_user_list.length > 500 || chat_content_list.length > 500)
				log_length = 500;
			else {
				if(chat_user_list.length < chat_content_list.length)
					log_length = chat_user_list.length;
				else
					log_length = chat_content_list.length;
			}
    		// console.log(log_length);
    		// console.log(chat_user_list);
    		// console.log(chat_content_list);
    		//display the log in order
    		for(var i = 0; i < log_length; i++) {
    			var display_content = parse_content(chat_content_list[i]);
    			console.log(display_content);
    			$(".con_box").append('<div class="my_say_con"><font color=\"#0000FF\">' + chat_user_list[i] + "</font><p><font color=\"#333333\">" + trim2(trim(display_content)) + '</font></p></div>');
				$(".my_show").scrollTop($(".con_box").height() - $(".my_show").height());
    		}
    	});
	 //    var chat_user_list = ["mark","mark","alice","mark","alice"]
	 //    for(var i = 0; i < 20; i++)
	 //    	chat_user_list.push("mark");
		// var chat_content_list = ["Newbee will get TI8!", "Liquid will be defeated by Newbee!", "I don't think so...", "You must believe that, 2018 is even year!", "But Newbee might be defeated by other team..."];
		// for(var i = 0; i < 20; i++)
		// 	chat_content_list.push("NB champion!");
		// //check the chat and user should be paired
		// var log_length;
		// if(chat_user_list.length > 500 || chat_content_list.length > 500)
		// 	log_length = 500;
		// else {
		// 	if(chat_user_list.length < chat_content_list.length)
		// 		log_length = chat_user_list.length;
		// 	else
		// 		log_length = chat_content_list.length;
		// }
		// console.log(log_length);
		// //display the log in order
		// for(var i = 0; i < log_length; i++) {
		// 	$(".con_box").append('<div class="my_say_con"><font color=\"#0000FF\">' + chat_user_list[i] + "</font><p><font color=\"#333333\">" + trim2(trim(chat_content_list[i])) + '</font></p></div>');
		// 	$(".my_show").scrollTop($(".con_box").height() - $(".my_show").height());
		// }

    }
    //functino that change topic of current channel
	function change_topic() {
		//check whether it is the admin -- but we need admin list here
		//if(ing_usr in admin_list)
		//else alert("You can not change channel topic")
		if(admin != true) {
			alert("You are not allowed to set new admin!");
			return;
		}
		var new_topic = prompt("Please Enter channel topic", "An interesting topic");
		if(new_topic != null){
			var send_channel_name = channel_name.slice(1);
			var ban_mes = "/change_topic/" + send_channel_name + "/" + new_topic;
			$.get(ban_mes,function(url,status) {
				//console.log(status);
				if(status == "success")
					alert("change_topic succeed!")
				window.location = url;

			});
		}
		else
			alert("Please Enter some words...")
		//refresh the header
		//$("#top").html('<br />&nbsp;&nbsp;' + dandan.mytime() + ',' + username + ' <br />&nbsp;&nbsp;The topic of this channel is: ' + channel_topic);
		//$("#top").html('<br />&nbsp;&nbsp;' + dandan.mytime() + ', ' + username + ' <br />&nbsp;&nbsp;Welcome to ' + channel_name  + '<br />&nbsp;&nbsp;The topic of this channel is: ' + channel_topic);
		//send new topic to server
	}

	function set_admin() {
		if(admin != true) {
			alert("You are not allowed to set new admin!");
			return;
		}
		var flag = false;
		var adminned = prompt("Who do you want to set as admin?");
		//console.log(adminned);
		for(i = 0; i < users.length; i++) {
			if(users[i] == adminned) {
				flag = true;
				break;
			}
		}
		if(flag == false) {
			alert("the user you want to be admin does not exist");
		}
		var send_channel_name = channel_name.slice(1);
		var admin_mes = "/set_admin/" + send_channel_name + "/" + username + "/" + adminned;
		//console.log(admin_mes);
		$.get(admin_mes,function(url,status) {
			//console.log(status);
			if(status == "success")
				alert("set_admin succeed!")
			window.location = url;
		});

	}

	function ban_user() {
		if(admin != true) {
			alert("You are not allowed to ban user!");
			return;
		}
		var flag = false;
		var user_tag = "user";
		var banned = prompt("Who do you want to ban?");
		//console.log(banned);
		for(i = 0; i < users.length; i++) {
			if(users[i] == banned) {
				flag = true;
				user_tag = user_tag + i;
				break;
			}
		}
		if(flag == false) {
			alert("the user you want to ban does not exist");
		}
		//remove the user from users list and also in the screen
		var index = users.indexOf(banned);
		users.splice(index,1);
		//var elem = document.getElementById(user_tag);
		//elem.parentNode.removeChild(elem);
		//console.log(users);
		//send the information to web server
		var send_channel_name = channel_name.slice(1);
		var ban_mes = "/ban_user/" + send_channel_name + "/" + username + "/" + banned;
		$.get(ban_mes,function(url,status) {
			//console.log(status);
			if(status == "success")
				alert("it succeed!")
			window.location = url;

		});
	}
	function unban_user() {
		if(admin != true) {
			alert("You are not allowed to ban user!");
			return;
		}
		var flag = false;
		var user_tag = "user";
		var unbanned = prompt("Who do you want to unban?");
		//console.log(unbanned);
		for(i = 0; i < users.length; i++) {
			if(users[i] == unbanned) {
				flag = true;
				user_tag = user_tag + i;
				break;
			}
		}
		if(flag == true) {
			alert("the user you want to unban is not banned");
		}
		//send the information to web server
		var send_channel_name = channel_name.slice(1);
		var unban_mes = "/unban_user/" + send_channel_name + "/" + username + "/" + unbanned;
		$.get(unban_mes,function(url,status) {
			//console.log(status);
			if(status == "success")
				alert("it succeed!")
			window.location = url;
		});
	}
	//not tested yet, for downloading file
	// var $idown;
	// function download_file(file_name) {
	// 	  var url = '/download/'+file_name;
	// 	  if ($idown) {
	// 	   $idown.attr('src',url);
	// 	  } 
	// 	  else {
	// 	    $idown = $('<iframe>', { id:'idown', src:url }).hide().appendTo('body');
	// 	  }

	// }
	function clean(filename) {
		$.get("/clean/" + filename, function(sth) {
			//console.log(sth);
		});
	}
	function download_file(file_name) {
		var link = document.createElement("a");
		link.download = "name you want";
		link.href = "/download_file/"+file_name;
		link.click();
		clean(file_name);
	}
	function newfile($this, arr, i) {
		var id = "file"; //have a new function to deal with file and id
		var file_size;
		// console.log(size);
		// if(size < 1000)
		// 	file_size = size;
		// else if(size > 1000 && size < 1000000)
		// 	file_size = size / 1000 + "KB";
		// else
		// 	file_size = size / 1000000 + "MB"
		// console.log(file_size);
		$($this).prepend('<li id="' + id + i + '">' + arr[i] + '</li>');
		$('#' + id + i).click(function() {
			//add something or function to get the file from server
			alert(id + i + " has been called!");
			download_file(arr[i]);
			}); //给按钮加事件
		hover_user('#' + id + i); //hover event
		user_geshu(); //update the number

	}

	function add_file() {
		var fu1 = document.getElementById("fileupload");
		//alert("You selected " + fu1.value);
		//if it is null, return an alert to user
		//modify the action attribute in form elemetn
		var upload_banner = document.getElementById("uploadbanner")
		if(fu1 == null || fu1.value == "") {
			alert("Please upload a valid file!");
			var send_channel_name = channel_name.slice(1);
			upload_banner.action = "/chatroom/" + send_channel_name;
			return;
		}
		//parse fu1.value here, it is a path
		var parsed = fu1.value.split("\\");
		var file_name = parsed[parsed.length-1];
		//add the file_name into the file_list
		for(var i =0; i < file_list.length; i++) {
			if(file_name == file_list[i]) {
				alert("Please don't upload the same file twice");
				return;
			}
		}
		//alert(upload_banner.enctype);
		send_channel_name = channel_name.slice(1);
		//console.log(upload_banner.action);
		upload_banner.action = "/upload_file/" + send_channel_name;
		//console.log(upload_banner.action);
		//no need to update current page, we will refresh it and load it again
		file_list.push(file_name);
		//alert("the file is " + fu1.files[0].size + " the new file_list member is " + file_list[file_list.length-1]);
		//create list
		var index = file_list.length-1;
		newfile('.ul_1', file_list,index);
	}
	//create a button for change topic
	$("#right_mid").append('<input type="button" class="ctrl_but" value="Change Topic"/>');
	//block user
	$("#right_top").append('<input type="button" id="block" value="Block User"/>');
	$("#right_top").append('<input type="button" id="unblock" value="Unblock User"/>');
	//create a button for ban user, only works for admin
	$("#right_mid").append('<input type="button" id="ban" value="Ban User"/>');
	$("#right_mid").append('<input type="button" id="unban" value="Unban User"/>');
	//create a button for setting new admin, 
	$("#right_mid").append('<input type="button" id="set_admin" value="Set Admin"/>');
	//create a button for leaving the chatroom page
	$("#mid_foot").append('<input type="button" id="leave" value="Leave chatrrom"/>');
	//$("#right_mid").append('<input type="button" id="file_but" value="Upload" onclick="document.getElementById(\'file\').click();" />');
	//$("#right_mid").append('<input type="file" style="display:none;" id="file" name="upload"/>');
	$(".ctrl_but").click(function() {
		change_topic();
	});
	$("#file_but").click(function() {
		add_file();
	})
	$("#ban").click(function() {
		ban_user();
	});
	$("#unban").click(function() {
		unban_user();
	});
	$("#set_admin").click(function() {
		set_admin();
	});
	$("#leave").click(function(e) {
		alert("should leave");
		var send_channel_name = channel_name.slice(1);
		$.get("/leave/"+ send_channel_name + "/" + username,function(url,status) {
			//console.log(status);
			if(status == "success")
				alert("it succeed!")
			window.location = url;

		}); //leave the room
	});
	$("#block").click(function() {
		var blocked = prompt("Who do you want to block?");
		var send_channel_name = channel_name.slice(1);
		var block_mes = "/block_user/" + send_channel_name + "/" + username + "/" + blocked;
		$.get(block_mes,function(url,status) {
			//do we need to refresh page?
			if(status == "success")
				alert("it succeed!")
			window.location = url;
		});
	});
	$("#unblock").click(function() {
		var unblocked = prompt("Who do you want to unblock?");
		var send_channel_name = channel_name.slice(1);
		var unblock_mes = "/unblock_user/" + send_channel_name + "/" + username + "/" + unblocked;
		$.get(unblock_mes,function(url,status) {
			//do we need to refresh page?
			if(status == "success")
				alert("it succeed!")
			window.location = url;
		});
	});
	init_page();
	setInterval(refresh_page,10000);
	//setInterval(init_page, 2000);
	// function my_user_con(user, id) {
	// 	if ($("#user_con" + id).length < 1) {
	// 		$(".con_box").append('<div id="user_con' + id + '"><font color="#CCCCCC">请在下面文本框里输入你想要聊天的内容，与用户【' + user + '】聊天</font></div>');
	// 		$("#user_con" + id).hide(); //默认隐藏，增加效果
	// 	}
	// 	sibli_hide("#user_con" + id); //隐藏兄弟
	// }
	// var t = new Date().toLocaleTimeString(); //当前时间
	// for(var i = 0; i < 100; i ++) {
	// $(".con_box").append('<div class="my_say_con"><font color=\"#0000FF\">' + username + t + "</font><p><font color=\"#333333\">" + trim2(trim("Yoyo I am here!")) + '</font></p></div>');
	// $(".my_show").scrollTop($(".con_box").height() - $(".my_show").height()); 
	// }
	// $("#right_foot").html('<p><img src="../images/admin_icon.png" alt="head" /></p>' + "Admin:" + username);
	// users_raw = "alice,mark,kaka,Sccc,Miracle"
	// users = parse_string(users_raw);
	// console.log(users);

})
