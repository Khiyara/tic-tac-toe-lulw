import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.websocket
import tornado.escape
import json
import time
from itertools import cycle
import numpy as np
import random
import string
import json
import os
import uuid


connections = dict()
connections['pepe'] = 'pepe'
print(connections)
class Game(object):
    def __init__(self, player, round):
        self.board = np.array([['']*3 for x in range(3)])
        self.current_player_cycle = ['o','x']
        self.current_player = player
        self.status_stack = {}
        self.status_stack['o'] = []
        self.status_stack['x'] = []
        self.counter_turn = {}
        self.counter_turn['o'] = 0
        self.counter_turn['x'] = 0
        self.round = round
    @staticmethod
    def make_serializable(nparray):
        return tuple([tuple(x) for x in nparray])
    def move(self,position):
        print ("moving")
        print (self.board)
        if self.board[int(position[0])][int(position[1])]:
            return {'sate':'game','game_state':'invalid','board':self.make_serializable(self.board)}
        else:
            if(self.current_player == 'o'):
                self.current_player = self.current_player_cycle[1]
                self.status_stack['x'].append([int(position[0]),int(position[1])])
                self.counter_turn['x'] += 1
                if self.counter_turn['x'] >= 4:
                    self.stack()
                print("status_stack x",self.status_stack['x'])
            else:
                self.current_player = self.current_player_cycle[0]
                self.status_stack['o'].append([int(position[0]),int(position[1])])
                self.counter_turn['o'] += 1
                if self.counter_turn['o'] >= 4:
                    self.stack()
                print("status_stack o",self.status_stack['o'])
            next_player_status = 'o_turn' if self.current_player == 'x' else 'x_turn'
            self.board[int(position[0])][int(position[1])] = self.current_player
            print("into")
            print(self.board)
            winner = self.check_win()
            status = winner if winner else next_player_status 
            return {'state':'game','game_state':status,'board':self.make_serializable(self.board),'boardX':self.status_stack['x'], 'boardO':self.status_stack['o'], 'turn': [self.counter_turn['x'],self.counter_turn['o']]}
    def check_win(self):
        x = np.array(['x','x','x'])
        o = np.array(['o','o','o'])
        print("checking the winner")
        #Check if X won
        if (self.board.diagonal() == x).all():
            return 'x'
        if (np.rot90(self.board).diagonal() == x).all():
            return 'x'
        for row in self.board:
            if (row == x).all(): 
              return 'x'
        for col in self.board.T:
            if (col == x).all(): 
              return 'x'
        #Check if O won
        if (self.board.diagonal() == o).all():
            return 'o'
        if (np.rot90(self.board).diagonal() == o).all():
            return 'o'
        for row in self.board:
            if (row == o).all(): 
              return 'o'
        for col in self.board.T:
            if (col == o).all(): 
              return 'o'
        return None
    def stack(self):
        print("STACK")
        self.board[self.status_stack[self.current_player][0][0]][self.status_stack[self.current_player][0][1]] = ''
        self.status_stack[self.current_player].pop(0)


class GameWebSocket(tornado.websocket.WebSocketHandler):
    print("access")
    def __init__(self,*args,**kwargs):
        tornado.websocket.WebSocketHandler.__init__(self,*args,**kwargs)
        self.player = None
        self.room_key = None
    def open(self, key): 
        print("WebSocket opened")
        print(self)
        self.room_key = key
        
        if key in connections.keys():
            connections[key].append(self)
        else:
            connections[key] = []
            connections[key].append(self)
            connections_game[key] = Game('o', 1)
        print(connections[key])
        self.update_state()   
        if key not in room_list.keys():
            print("Closing websocket you are not allowed to connect")
            self.close()
        
    def update_state(self):
        players = [x.player for x in connections[self.room_key]]
        print (players)
        if players:
            if (len(players) > 2) and ('x' in players) and ('o' in players):
                for x in connections[self.room_key]: 
                    if not x.player:
                        x.write_message({'state':'wait'})
            if (not 'x' in players) and (not 'o' in players):
                print ('In 1')
                connections[self.room_key][0].player = 'x'
                connections[self.room_key][0].write_message({'state':'on_deck'})
            elif not 'x' in players:
                print ('In 2')
                for x in connections[self.room_key]: 
                    if not x.player:
                        x.player = 'x'
                        x.write_message({'state':'game','game_state':'x_turn','player':'x'})
                connections[self.room_key][players.index('o')].write_message({'state':'game','game_state':'x_turn','player':'o'})
            elif not 'o' in players:
                print ('In 3')
                for x in connections[self.room_key]: 
                    if not x.player:
                        x.player = 'o'
                        x.write_message({'state':'game','game_state':'x_turn','player':'o'})
                connections[self.room_key][players.index('x')].write_message({'state':'game','game_state':'x_turn','player':'x'})
            elif ('x' in players) and ('o' in players):
                print ('creating a new game and sending the announcement')
                
                if(connections_game[self.room_key].round % 2 == 0):
                    temp = connections_game[self.room_key].round
                    connections_game[self.room_key] = Game('o', temp+1)
                    connections[self.room_key][players.index('x')].write_message({'state':'game',
                            'game_state':'x_turn',
                            'player':'x',
                            'board':connections_game[self.room_key].make_serializable(connections_game[self.room_key].board)})
                    connections[self.room_key][players.index('o')].write_message({'state':'game',
                           'game_state':'x_turn',
                           'player':'o',
                           'board':connections_game[self.room_key].make_serializable(connections_game[self.room_key].board)})
                elif(connections_game[self.room_key].round % 2 == 1):
                    temp = connections_game[self.room_key].round
                    connections_game[self.room_key] = Game('x', temp+1)
                    connections[self.room_key][players.index('x')].write_message({'state':'game',
                            'game_state':'o_turn',
                            'player':'x',
                            'board':connections_game[self.room_key].make_serializable(connections_game[self.room_key].board)})
                    connections[self.room_key][players.index('o')].write_message({'state':'game',
                            'game_state':'o_turn',
                            'player':'o',
                            'board':connections_game[self.room_key].make_serializable(connections_game[self.room_key].board)})
                    
            else:
                for x in connections[self.room_key]: 
                    if not x.player:
                        x.write_message({'state':'wait'})
        print ('Leaving update state')
    def on_message(self, message):
        print ('message is')
        print (message)
        message = json.loads(message)
        if (len(connections[self.room_key]) < 2):
            return
        if self.player == 'o':
            print ('O is trying making a move')
            print (message['move'])
            if connections_game[self.room_key].current_player == 'x':
                info = connections_game[self.room_key].move(message['move'])
            else:
                info = {'player':'o','state':'game','game_state':'invalid','board':connections_game[self.room_key].make_serializable(connections_game[self.room_key].board),'boardX':connections_game[self.room_key].status_stack['x'], 'boardO':connections_game[self.room_key].status_stack['o'], 'turn': [connections_game[self.room_key].counter_turn['x'],connections_game[self.room_key].counter_turn['o']]}
        if self.player == 'x':
            print ('X is trying making a move')
            print (message['move'])
            if connections_game[self.room_key].current_player == 'o':
                info = connections_game[self.room_key].move(message['move'])
            else:
                info = {'player':'x','state':'game','game_state':'invalid','board':connections_game[self.room_key].make_serializable(connections_game[self.room_key].board),'boardX':connections_game[self.room_key].status_stack['x'], 'boardO': connections_game[self.room_key].status_stack['o'], 'turn': [connections_game[self.room_key].counter_turn['x'],connections_game[self.room_key].counter_turn['o']]}
        info['player'] = 'x'
        self.find_player('x').write_message(info)
        info['player'] = 'o'
        self.find_player('o').write_message(info)
        if (info['game_state'] == 'x' or info['game_state'] == 'o'):
            time.sleep(3)
            print ("I should be restarting now!")
            self.update_state()

    def find_player(self,letter):
        players = [x.player for x in connections[self.room_key]]
        
        try: 
            return connections[self.room_key][players.index(letter)]
        except ValueError:
            return None
    def on_close(self):
        print ('websocket close')
        print (self.player)
        if self.player == 'o':
            print ('reseting board')
            connections_game[self.room_key] = Game('o', 1)
            print ('deleting o')
            if self.find_player('x'):
                print ('o forfeits')
                self.find_player('x').write_message({'state':'won'})
                self.find_player('x').player = None;
                time.sleep(3)
        if self.player == 'x':
            print ('reseting board')
            connections_game[self.room_key] = Game('o', 1)
            print ('deleting x')
            if self.find_player('o'):
                print ('x forfeits')
                self.find_player('o').write_message({'state':'won'})
                self.find_player('o').player = None;
                time.sleep(3)
        for i, x in enumerate(connections[self.room_key]):
            print(i,x)
            if self == x:
                print ('deleting it')
                del(connections[self.room_key][i])
                if (len(connections[self.room_key]) == 0):
                    print("deleting room until it's root")
                    del (connections_game[self.room_key])
                    del (connections_chat[self.room_key])
                    del (connections[self.room_key])
                    del (room_list[self.room_key])
                    return
        self.update_state()
            
class RedirectHandler(tornado.web.RequestHandler):
	def get(self):
		self.render('index.html')	
#		self.write('redirect')

class GameRoomHandler(tornado.web.RequestHandler):
    def get(self, **kwargs):
        key = kwargs.get('key')
        print(key)
        self.render('game.html', roomId=key, messages={})
        
class ChatWebSocket(tornado.websocket.WebSocketHandler):
    
    def __init__(self,*args,**kwargs):
        tornado.websocket.WebSocketHandler.__init__(self,*args,**kwargs)
        self.room_key = None
        self.player = None
    def open(self, key): 
        print("chat connect")
        self.room_key = key
        if key in connections_chat.keys():
            connections_chat[key].append(self)
        else:
            connections_chat[key] = []
            connections_chat[key].append(self)
        print(connections_chat[key])
        if(connections_chat[key][0].player == None):
            connections_chat[key][0].player = 'Player 1'
            self.player = 'Player 1'
        else:
            connections_chat[key][1].player = 'Player 2'
            self.player = 'Player 2'
        if key not in room_list.keys():
            print("Closing chat")
            self.close()

    def on_close(self):
        print ('chat close')
        for i, x in enumerate(connections_chat[self.room_key]):
            if self == x:
                print ('deleting it')
                temp = connections_chat[self.room_key][i].player == 'Player 1'
                del(connections_chat[self.room_key][i])
                if temp:
                    connections_chat[self.room_key][0].player = 'Player 1'

    def send_updates(self, chat):
        print("sending message to %d waiters", len(connections_chat[self.room_key]))
        for waiter in connections_chat[self.room_key]:
            try:
                waiter.write_message(chat)
            except:
                print("Error sending message", exc_info=True)

    def on_message(self, message):
        print("got message %s", message)
        chat = {"id": str(uuid.uuid4())}
        chat["html"] = self.player+" : "+message
        self.send_updates(chat)

class RoomTokenGenerator(tornado.web.RequestHandler):
    def post(self):
        token = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(10))
        room_list[token] = token
        self.write(json.dumps(token))
        self.finish()
        
if __name__ == "__main__":
    connections = {}
    connections_game = {}
    connections_chat = {}
    room_list = {}
    application = tornado.web.Application([
                (r"/websocket/(?P<key>\w+)", GameWebSocket),
                (r"/", RedirectHandler),
                (r"/game/(?P<key>\w+)", GameRoomHandler),
                (r"/game/(.*)", tornado.web.StaticFileHandler, {'path':r'./public'}),
                (r"/create/", RoomTokenGenerator),
                (r"/chat/(?P<key>\w+)", ChatWebSocket),
    ])
    http_server = tornado.httpserver.HTTPServer(application)
    port = int(os.environ.get("PORT", 5000))
    http_server.listen(port)
    tornado.ioloop.IOLoop.instance().start()
