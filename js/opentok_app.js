import{parse_cookies} from "./utils.js";

cookies = parse_cookies(document.cookie);

let api_key = '46869784';
let session_id = cookies['session_id'];
let session_token = cookies['session_token'];

initializeSession(api_key, session_id);

// Handling all of our errors here by alerting them
function handleError(error) {
    if (error) {
        alert(error.message);
    }
}

function initializeSession(api_key, session_id) {
    var session = OT.initSession(api_key, session_id);

    // Subscribe to a newly created stream
    session.on('streamCreated', function(event) {
    session.subscribe(event.stream, 'subscriber', {
        insertMode: 'append',
        width: '100%',
        height: '100%'
    }, handleError);
});

    // Create a publisher
    var publisher = OT.initPublisher('publisher', {
        insertMode: 'append',
        width: '100%',
        height: '100%'
    }, handleError);

    // Connect to the session
    session.connect(token, function(error) {
        // If the connection is successful, publish to the session
        if (error) {
            handleError(error);
        } else {
            session.publish(publisher, handleError);
        }
    });
}
