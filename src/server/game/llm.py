import time
import uuid

import game.lib_llm

from settings import DefaultProvider

def getTime():
    return round(time.time())

class LeLonMo:
    def __init__(self) -> None:
        '''
        self.status : 
            0 : Waiting for admin
            1 : Waiting for other players
            2 : Game started
            3 : Waiting for admin to restart (game finished)
        '''
        self.status = 0
        self.admin_uuid = str()
        self.letters = list()
        self.players = dict()
        self.settings = DefaultProvider()

    def add_user(self, private_uuid: str, username: str)->dict:
        if self.status == 0:
            self.admin_uuid = private_uuid
            self.status = 1
            return self.add_user(private_uuid, username)
        elif self.status == 1:
            self.players[private_uuid] = {
                'private_uuid' : private_uuid,
                'public_uuid' : str(uuid.uuid4())[:8],
                'username' : username,
                'status' : 'wait_for_start',
                'last_update' : getTime(),
                'kicked' : False,
                'points' : 0,
                'latest_word' : '',
                'latest_points' : ''
            }
            return self.players[private_uuid]
    def kick_user(self, private_uuid: str)->None:
        self.players[private_uuid]['kicked'] = True
    
    def delete_user(self, private_uuid: str)->None:
        del self.players[private_uuid]
    
    def is_admin(self, private_uuid: str)->bool:
        return private_uuid == self.admin_uuid
    
    def is_kicked(self, private_uuid: str)->bool:
        return self.players[private_uuid]['kicked']

    def get_users(self)->list:
        player_list = list()
        for k in self.players:
            if not self.players[k]['kicked']:
                player_list.append({
                    'public_uuid' : self.players[k]['public_uuid'],
                    'username' : self.players[k]['username'],
                    'status' : self.players[k]['status'],
                    'points' : self.players[k]['points'],
                    'latest_word' : self.players[k]['latest_word'] if self.status == 3 else None,
                    'admin': k == self.admin_uuid
                })
        return player_list
        

    def validate_request(self, action : str)->bool:
        if action == 'join':
            return self.status == 0 or self.status == 1
        if action == 'submit_word':
            return self.status == 2
        if action == 'update':
            return True
        if action == 'create_game':
            return self.status == 3
        if action == 'start_game':
            return self.status == 1
        print('Unknown action :', action)
        return False
    
    def handle_requests(self, private_uuid: str, data: dict)->dict:
        
        try:
            if not self.validate_request(data['action']):
                return {'success' : False, 'message' : 'invalid_request'}

            if data['action'] == 'join':
                return self.add_user(private_uuid, data['username'])

            if data['action'] == 'update':
                self.players[private_uuid]['last_update'] = getTime()
                if self.status == 2:
                    if not self.players[private_uuid]['latest_word']:
                        self.players[private_uuid]['status'] = 'playing'
                return {
                    'success' : True,
                    'users' : self.get_users(),
                    'server_status' : self.status,
                    'letters' : self.letters,
                    'admin' : private_uuid == self.admin_uuid
                }
            
            if data['action'] == 'start_game':
                self.letters = game.lib_llm.generate_letters(self.settings['letter_number'])
                self.satus = 2
                return {'success' : True}
            if data['action'] == 'submit_word':
                if not game.lib_llm.check_list(data['word'], self.letters):
                    return {
                        'success' : True,
                        'valid' : False
                    }
                if not game.lib_llm.check_dict(data['word']):
                    return {
                        'success' : True,
                        'valid' : False
                    }
                
                self.players[private_uuid]['latest_word'] = data['word']
                self.players[private_uuid]['status'] = 'finished'
            if data['action'] == 'create_game':
                if private_uuid == self.admin_uuid:
                    self.__init__()
                    return {'success' : True}
                else:
                    return {'success' : False, 'message' : 'not_admin'}
            
        except KeyError as e:
            field = str(e).replace("KeyError: '", "").replace("'", '')
            print(f'[E] Missing required field : ' + field)
            return {'success' : False, 'message' : 'missing_field', 'detail' : 'Missing field ' + field }

        except:
            import traceback
            traceback.print_exc()
            return {'success' : False, 'message' : 'server_error', 'detail' : traceback.format_exc()}


    


