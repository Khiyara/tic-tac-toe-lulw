//Pages for each game state
var state = ['on_deck', 'game', 'wait', 'won'];
var clear_all = function() {
    state.forEach(function(state) {
        console.log(state);
        if (document.getElementById(state).className != 'hide') {
            document.getElementById(state).className += 'hide';
        }
    });
};

var set_state = function(name) {
    clear_all();
    document.getElementById(name).className =
        document.getElementById(name).className.replace(/(?:^|\s)hide(?!\S)/g, '');
};




var elm = document.getElementById('main');
//Set up web socket
websocketConnect = function(link) {
    var ws = new WebSocket("ws://tic-tac-toe-ph.herokuapp/websocket/"+link);
    ws.onmessage = function(evt) {
        console.log("connecting..");
        data = JSON.parse(evt.data)
        console.log(data);
        //The overall page state is set by the state property on a WS message
        if ('state' in data) {
            console.log(data)
            set_state(data.state);
            //The whole state of the game is restored from a JSON object
            if (data.state == 'game') {
                //Set The player name
                if (data.player == 'x') {
                    document.getElementById('player').innerHTML = "You are player X";
                }
                if (data.player == 'o') {
                    document.getElementById('player').innerHTML = "You are player O";
                }
                if (data.game_state == 'x_turn') {
                    document.getElementById('game_state').innerHTML = "It's X's turn";
                }
                if (data.game_state == 'o_turn') {
                    document.getElementById('game_state').innerHTML = "It's O's turn";
                }
                if (data.game_state == 'x') {
                    document.getElementById('game_state').innerHTML = "X Wins!";
                }
                if (data.game_state == 'o') {
                    document.getElementById('game_state').innerHTML = "O Wins!";
                }
                if (data.game_state == 'stalemate') {
                    document.getElementById('game_state').innerHTML = "Stalemate!";
                }

                //Update the board
                if ('board' in data) {
                    update_board(data.board, data.boardO, data.boardX, data.turn);
                }
            };
        };
    };

    return ws;
}

var move = function(value) {
    console.log('sending json now');
    ws.send(JSON.stringify({
        move: value
    }))
};

var update_board = function(board, boardO, boardX, counter) {
    for (var i = 0; i < 3; i++) {
        for (var j = 0; j < 3; j++) {
            var index = i.toString() + j.toString();
            document.getElementById(index).innerHTML = "" + board[i][j].toUpperCase();
        }
    }
    if (counter[0] >= 3 && counter[1] >= 3) {
        for (let i = 0; i < 3; i++) {
            var index = boardO[i][0].toString() + boardO[i][1].toString();
            document.getElementById(index).innerHTML = document.getElementById(index).innerHTML + "" + "<sub>" + i + "</sub>";
            var index = boardX[i][0].toString() + boardX[i][1].toString();
            document.getElementById(index).innerHTML = document.getElementById(index).innerHTML + "" + "<sub>" + i + "</sub>";
        }
    }
}

for (var i = 0; i < 3; i++) {
    console.log('test2');
    for (var j = 0; j < 3; j++) {
        var index = i.toString() + j.toString()
        console.log(index);
        console.log('test3');
        (function(index) {
            document.getElementById(index).addEventListener('click', function() {
                console.log(index);
                move(index.toString());
            });
        })(index);
    }
}