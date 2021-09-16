class Chat:
    def __init__(self) -> None:
        self.userlist = dict()
        self.messagelist = list()
    
    def add_user(self, private_uuid, public_uuid, name):
        self.userlist[private_uuid] = {
            'priv_uuid' : private_uuid,
            'pub_uuid' : public_uuid,
            'username' : name,
            'last_read' : 0
        }
    
    def remove_user(self, private_uuid):
        del self.userlist[private_uuid]
    
    def get_messages(self, private_uuid):
        return self.messagelist[
            self.userlist[private_uuid]['last_read']:
        ]
    
    def send_message(self, private_uuid, message):
        self.messagelist.append(
            {
                'text' : message,
                'username' : self.userlist[private_uuid]['name'],
                'uuid' : self.userlist[private_uuid]['pub_uuid']
            }
        )

    def handle_requests(self, data):
        pass

    

    