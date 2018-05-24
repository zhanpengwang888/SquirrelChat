/** 
 * Created by Mark on 2018/4/22.
 * Inspired by this web page: https://blog.csdn.net/fifteen718/article/details/50836046 
 */  
function login() {  
  
    var username = document.getElementById("username");  
    var pass = document.getElementById("password");  
  
    if (username.value == "") {  
  
        alert("please Enter the username!");  
  
    } else if (pass.value  == "") {  
  
        alert("Please enter the password!");  
  
    }
    else{  
        //here we should send the username and password to web server
        //and request web server to search it in the database
        //use XMLHttpRequest -- simulate 3I part3
        //var log = new XMLHttpRequest();
        //log.open('POST', "http://127.0.0.1:5000/login", false);
        alert("You have login in successfully, Let's chat!");
        window.location.href="../chatroom/chat.html";
  
    }  
}