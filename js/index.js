let website_url = 'http://34.70.53.112';
let api_port = 8000;

login_button = document.getElementById("login");
login_button.onclick = function() {
    let username = document.getElementById("username").value;
    let password = document.getElementById("password").value;

    let data = {"username": username, "password": password};
    fetch(website_url + ":" + api_port + "/api/auth", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(data => {
        if (data['success'] === false) { // Failed to log in
            console.log('Incorrect username or password');
        } else {
            if (data['is_examiner']) {
                window.location.href = website_url + '/index/index3.html';
            } else {
                window.location.href = website_url + '/index/index2.html';
            }
            document.cookie = "username=" + username;
            document.cookie = "password=" + password;
            document.cookie = "display_name=" + data['display_name'];
            document.cookie = "is_examiner=" + data['is_examiner'];
            document.cookie = "initials=" + data['initials'];
        }
    });
};
