/** 
 * Created by Mark on 2018/4/22.
 * Inspired by this web page: https://blog.csdn.net/fifteen718/article/details/50836046 
 */  
function register() {  
  
    var username = document.getElementById("username");  
    var pass = document.getElementById("password");  
  
    if (username.value == "") {  
  
        alert("please Enter the username!");  
  
    } else if (pass.value  == "") {  
  
        alert("Please enter the password!");  
  
    }else {  
        alert("username is " + username.value + " password is " + pass.value);
        //here we send the username and password to our web server
        //var log = new XMLHttpRequest();
        //log.open('POST', "http://127.0.0.1:5000/register", false);
        alert("You have registered successfully, return to login page!");
        window.location.href="login.html";
  
    }  
}