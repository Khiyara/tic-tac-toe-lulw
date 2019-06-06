function newMessage(form) {
    if(form.length < 1) return;
    console.log(form);
    webchat.send(JSON.stringify(form));
}

var counter = 0;

var chatConnect = function(link){
    var protocolPrefix = (window.location.protocol === 'https:') ? 'wss:' : 'ws:';
    var ws = new WebSocket(protocolPrefix + '//' + location.host + "/chat/" + link);
    ws.onmessage = function(evt) {
        showMessage(JSON.parse(evt.data));
    }
    return ws;
}
showMessage = function(message) {
   
    var existing = document.getElementById('m'+message.id);
    if (existing == null) {
        var node = message.html;
        var temp = document.createElement('div');
        temp.innerHTML = node;
        temp.className = 'message';
        temp.id = message.id;
        console.log(temp);
        counter += 1;
        if(counter > 10) {
            document.getElementById('inbox').innerHTML = "";
            counter = 0;
        }
        document.getElementById('inbox').append(temp);
    }
}

