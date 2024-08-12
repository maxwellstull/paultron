# A hopefully simple way to handle information on servers
import json

class Application():
    def __init__(self):
        self.servers = {}
    def load_json(self):
        fp = open("savedata.json","r")
        to_load = json.load(fp)
        for server_id, server in to_load.items():
            self.servers[server_id] = Server(server_id)
            self.servers[server_id].load_json(server)
        print("Json Loaded")
    def save_json(self):
        to_save = {}
        for server_id, server in self.servers.items():
            to_save[server_id] = server.save_json()
        with open("savedata.json","w") as fp:
            json.dump(to_save, fp, default=str)
    def add_server(self, id):
        self.servers[str(id)] = Server(id)
    
class Server():
    def __init__(self, id):
        self.users = {}
        self.channels = {}
        self.id = id
        self.name = None
        self.reacters = {}
        self.most_recent_message = None
    def load_json(self, json_data):
        for user_id, user in json_data['users'].items():
            self.users[user_id] = User(None)
            self.users[user_id].load_json(user)
        for channel_id, channel in json_data['channels'].items():
            self.channels[channel_id] = Channel(None)
            self.channels[channel_id].load_json(channel)
        self.id = json_data['id']
        self.reacters = json_data['reacters']
        self.name = json_data['name']
        self.most_recent_message = json_data['most_recent_message']
    def save_json(self):
        to_save = {}
        to_save['id'] = self.id
        user_info = {}
        for user_id, user in self.users.items():
            user_info[user_id] = user.save_json()
        to_save['users'] = user_info
        channel_info = {}
        for channel_id, channel in self.channels.items():
            channel_info[channel_id] = channel.save_json()
        to_save['channels'] = channel_info
        to_save['reacters'] = self.reacters
        to_save['name'] = self.name
        to_save['most_recent'] = self.most_recent_message
        return to_save
    def add_user(self, user):
        self.users[str(user.id)] = User(user)
        self.reacters[str(user.id)] = {}
    def add_channel(self, channel):
        self.channels[str(channel.id)] = Channel(channel)
    def summarize_yaps(self):
        retval = {user:0 for user in self.users.keys()}
        for channel_id, channel in self.channels.items():
            for yapper, count in channel.yappers.items():
                retval[yapper] += count

        return retval
    def summarize_reactions(self):
        emojis = {}
        for user_id, user in self.users.items():
            for reaction, amount in user.reactions.items():
                if reaction not in emojis:
                    emojis[reaction] = amount
                else:
                    emojis[reaction] += amount
        return emojis

class Channel():
    def __init__(self, channel=None):
        if channel:
            self.id = channel.id
            self.name = channel.name
            self.last_traversal = None
        self.yappers = {}
    def save_json(self):
        return {"id": self.id,
                "last_traversal": self.last_traversal,
                "name":self.name,
                "yappers":self.yappers,
                }
    def load_json(self, json_data):
        self.id = json_data['id']
        self.last_traversal = json_data['last_traversal']
        self.name = json_data['name']
        self.yappers = json_data['yappers']

class User():
    def __init__(self, user=None):
        if user:
            self.id = user.id
            self.name = user.name
            self.nick = user.display_name
        
        self.messages = []
        self.reactions = {}

    def load_json(self, json_data):
        self.id = json_data['id']
        self.name = json_data['name']
        self.nick = json_data['nick']
        self.messages = json_data['messages']
        self.reactions = json_data['reactions']
    def save_json(self):
        return {'id':self.id, 'nick':self.nick, 'name':self.name, 'messages':self.messages, 'reactions':self.reactions}