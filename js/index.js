import{parse_cookies} from "./utils.js";

let cookies = parse_cookies(document.cookie);

let website_url = 'http://34.70.53.112';
let api_port = 8000;

// all pages
let initials_p = document.getElementById('initials');
if (initials_p) {
    if ('initials' in cookies) {
        initials_p.innerHTML = cookies['initials'];
    }
}

// login page
let login_button = document.getElementById('login');
if (login_button) {
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
}

// lobby
let join_sess_button = document.getElementById('join_sess');
if (join_sess_button) {
    join_sess_button.onclick = function() {
        let username = cookies['username']; 
        let password = cookies['password'];
        let session_id = document.getElementById("sess_id").value;
        let sess_password = document.getElementById("join_sess_password").value;
    
        let data = {"username": username,
                    "password": password,
                    "session_id": session_id, 
                    "session_password": sess_password};
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
                document.cookie = 'session_password=' + sess_password;
                window.location.href = website_url + '/index/index4.html';
            }
        });
    };
}

let create_sess_button = document.getElementById('create_sess');
if (create_sess_button) {
    create_sess_button.onclick = function() {
        let username = cookies['username']; 
        let password = cookies['password'];
        let sess_password = document.getElementById("create_sess_password").value;
    
        let data = {"username": username, 
                    "password": password,
                    "session_password": sess_password};
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
                document.cookie = 'session_password=' + sess_password;
                window.location.href = website_url + '/index/index4.html';
            }
        });
    };
}

// session
window.add_participant_to_ul = function add_participant_to_ul(ul, participant) {
    let li = document.createElement('li');
    li.innerHTML = participant['display_name'];
    li.className = (participant['is_examiner']) ? 'examiner' : 'student';
    li.id = participant['user_id'];
    ul.appendChild(li);
}

let ul = document.getElementById('participant_list');
if (ul) {
    function remove_participants() {
        let current_participants = ul.getElementsByTagName('li');
        for (let i = 0; i < current_participants.length; ++i) {
           ul.removeChild(current_participants[i]); 
        }
    }

    function add_participants() {
        remove_participants();

        let session_id = cookies['session_id'];
        let sess_password = cookies['session_password'];
         
        let data = {"session_id": session_id, 
                    "session_password": sess_password};
        fetch(website_url + ":" + api_port + "/api/session/users", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        })
        .then(res => res.json())
        .then(data => {
            if (data['success'] === false) { 
                console.log('There was a problem getting participant list for the session');
            } else {
                let users = data['users'];
                add_participant(ul, );
            }
        });
        setTimeout(add_participants, 10000); // Do this every 10 seconds
    }

    add_participants();
}

let session_id_p = document.getElementById('session_id');
if (session_id_p) {
    session_id_p.innerHTML += cookies['session_id'];
}
