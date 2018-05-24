var username;
$(document).ready(function(){
    $('#btn_create_channel').click(function() {
        alert("Create channel");
        var new_name = prompt("Please Enter the name of channel", "New Channel");
        var new_topic = prompt("Please Enter the topic of channel", "An interesting topic");
        //we should get from server
        //var new_admin = prompt("Please Enter your username again","My username");
        if(new_name == null || new_topic == null) {
            alert("Please enter correct information!");
            return;
        }
        var old_name = new_name;
        new_name = "#" + new_name; //add a # before the channel name to let it 
        console.log(new_name);
        var data = {};
        data["name"] = new_name;
        data["topic"] = new_topic;
        data["admin"] = username;
        $.ajax({
        type: 'POST',
        url: '/channels',
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        data: JSON.stringify(data),
        context: document.getElementById("mytable"),
        success: function(callback) {
            console.log(callback);
            // Watch out for Cross Site Scripting security issues when setting dynamic content!
            //$(this).text('Hello!');
            alert("You have created the channel successfully!");
            create_new_channel(this, old_name,new_topic,username);

        },
        error: function() {
            //$(this).html("error!");
            alert("The channel has existed, please change a name");
        }
        });
    });

    // $('input[type="button"]').click(function() {
    //     alert("now?");
    //     alert("I have been clicked, I am " + this.id);
    // });

});

function create_new_channel($this,new_name,new_topic, new_admin) {  
//var table = document.getElementById("mytable"); //we can use $this to replace
var c_name = document.createElement("th");
var new_channel = document.createElement("tr");
var c_topic = document.createElement("td");
var c_admin = document.createElement("td");
var name = document.createTextNode("#" + new_name); // data comes from user need to send to server
var topic = document.createTextNode(new_topic); //one node can only be used in one cell
var admin = document.createTextNode(new_admin); //the admin should be came from the server database
//send the data to server here -- ask kris

//link to the chat page
var c_link = document.createElement('a');
//c_link.href = "/chatroom/" + new_name;
//a.href = "/chat_page/" + name; //goes to chat page
//here it should link to the chat function of web server
c_link.href="/chatroom"+ "/" + new_name;
//we need to have special form for flask
//c_link.href="\"" + chat_url + "\"";
//console.log(chat_url);
//c_link.href="../chatroom/chat.html";
//var c_link = document.createElement('p');
var c_button = document.createElement("BUTTON");
//c_button.setAttribute("type","button");
//c_button.setAttribute("value", new_name);
c_button.appendChild(name);
c_link.appendChild(c_button);
c_name.appendChild(c_link);
new_channel.appendChild(c_name);
c_topic.appendChild(topic);
new_channel.appendChild(c_topic);
c_admin.appendChild(admin);
new_channel.appendChild(c_admin);
$($this).append(new_channel);

};

function load_default() {
    //in this function we should load from the server database and add the row into the table
    //now it is hard code
    var topic_list;
    var admin_list;
    var channel_list;
    var init_length;
    var username_temp = document.getElementById("username");
    //var channel_list_temp = document.getElementById("channel_list"); // channel list should still comes forom
    username = username_temp.textContent;
    document.getElementById("username").style.display = "none";
    //get the default channel thing
    $.get("/get_channel_list", function(c_list,status){
        console.log(c_list);
        channel_list = c_list.channel_list;
        topic_list = c_list.topic;
        admin_list = c_list.admin;
        init_length = channel_list.length;
        // console.log(channel_list);
        // console.log(topic_list);
        // console.log(admin_list);
        var table = document.getElementById("mytable")
        // var channels = [];
        // channels[0] = ["haha","this is a funny channel","mark"];
        // channels[1] = ["TT","this is a sorrow channel","alice"];
        console.log(init_length);
        console.log(channel_list)
        for(var i = 0; i < init_length; i++) {
            var tr = document.createElement("tr");
            var th = document.createElement("th");
            //add channel name
            console.log("I am here.")
            //I will use a id and use jquery to deal with it
            var c_link = document.createElement('a');
            //special solution to fit flask format
            //var chat_url =  baseURL.replace('REPLACE', channel_list[i]);
            //var chat_url = baseURL + '?channel_name=' + channel_list[i];
            //console.log(chat_url);
            //c_link.href="\"" + chat_url + "\"";
            //c_link.href="../chatroom/chat.html";
            var no_sharp_name = channel_list[i];
            no_sharp_name = no_sharp_name.slice(1);
            console.log(no_sharp_name);
            c_link.href="/chatroom/" + no_sharp_name;
            var c_name = document.createTextNode(channel_list[i]);
            var c_button = document.createElement("BUTTON");
            c_button.appendChild(c_name);
            c_link.appendChild(c_button);
            th.appendChild(c_link);
            tr.appendChild(th);

            //add channel topic
            var c_topic = document.createElement("td");
            var c_txt = document.createTextNode(topic_list[i]);
            c_topic.appendChild(c_txt);
            tr.appendChild(c_topic);

            //add admin list -- now it is just one
            var c_admin = document.createElement("td");
            var admin_name = document.createTextNode(admin_list[i]);
            c_admin.appendChild(admin_name);
            tr.appendChild(c_admin);        
            //update the table now 
            table.appendChild(tr);
        }
    });

}