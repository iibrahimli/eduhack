import{parse_cookies} from "./utils.js";

let website_url = 'http://34.70.53.112';
let api_port = 8000;

let join_sess_button = document.getElementById("join_sess");
if (join_sess_button) {
    join_sess_button.onclick = function() {
        let cookies = parse_cookies(document.cookie);
        let username = cookies['username']; 
        let password = cookies['password'];
        let session_id = document.getElementById("sess_id").value;
        let session_password = document.getElementById("sess_password").value;
    
        let data = {"username": username,
                    "password": password,
                    "session_id": session_id, 
                    "session_password": session_password};
        fetch(website_url + ":" + api_port + "/api/session/join", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        })
        .then(res => res.json())
        .then(data => {
            if (data['success'] === false) {
                console.log('Incorrect Session ID or Session Password');
            } else {
                document.cookie = 'session_id=' + data['session_id'];
                document.cookie = 'session_token=' + data['session_token'];
                window.location.href = website_url + '/index/index4.html';
            }
        });
    };
}

let create_sess_button = document.getElementById("create_sess");
if (create_sess_button) {
    create_sess_button.onclick = function() {
        let cookies = parse_cookies(document.cookie);
        let username = cookies['username']; 
        let password = cookies['password'];
        let password = document.getElementById("sess_password").value;
    
        let data = {"username": username, 
                    "password": passwrod,
                    "session_password": password};
        fetch(website_url + ":" + api_port + "/api/session/create", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        })
        .then(res => res.json())
        .then(data => {
            if (data['success'] === false) { 
                console.log('There was a problem creating a session');
            } else {
                document.cookie = 'session_id=' + data['session_id'];
                document.cookie = 'session_token=' + data['session_token'];
                window.location.href = website_url + '/index/index4.html';
            }
        });
    };
}
