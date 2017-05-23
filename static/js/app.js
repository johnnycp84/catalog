
// var loggedout_string = '<a id="login" class="login" href="{{url_for("login")}}">Login/Signup</a>';

// var loggedin_string = 'Signed in as {{login_session["username"]}}<a class="login" href="{{url_for("gDisconnect")}}">Logout</a>';

// // console.log(loggedout_string)

// $("#login-area").html(loggedout_string);




function loginStatus(username, loggedin_string, loggedout_string) {
    console.log('the unsername is')
    console.log(username)
        if (username.length != 0) {
        $("#login-area").html(loggedin_string);
        console.log('the username is good')
    }
    else {
        $("#login-area").html(loggedout_string);
        console.log('the username is undefined')
    }
}

