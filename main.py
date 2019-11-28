import requests
from json import JSONDecoder
from pyvis.network import Network
import keyring

decoder = JSONDecoder()

# vk restful_api_head
vk_api = 'https://api.vk.com/method/'

# FOR THE FIRST RUN: UNCOMMENT THE LINE BELOW TO PASTE YOUR ACCESS CODE THEN COMMENT IT AGAIN
# keyring.set_password('vk_api', input('insert username'), getpass.getpass('paste your access token'))

# common_parameters
# all specific methods update copy of this dict and send it to get_request_result()
params = {
        'v': '5.7',
        'filter': 'all',
        'access_token': keyring.get_password('vk_api', input('insert username'))
}

# request_json_wrapper
# It's recieve method and params, then try to request to vk restful api and decode it from JSON to dict


def get_request_result(method, params, inner_obj):
    result = requests.get(vk_api+method, params = params)
    try:
        return decoder.decode(result.text)['response'][inner_obj]
    except:
        error = decoder.decode(result.text)
        print(error['error']['error_msg'])
        if inner_obj == 'count':
            return 0
        else:
            return []


class Group:
    def __init__(self, group_id):
        self.group_id = group_id
        self.params = params.copy()
        self.method = 'groups.getMembers'
        self.params.update({
            'group_id': group_id
        })

    def get_members_count(self):
        users_count = get_request_result(self.method, self.params, 'count')
        return users_count

    def get_members_batch(self, count=100, offset=0):
        self.params_batch = self.params.copy()
        self.params_batch.update({
            'count': count,
            'offset': offset
        })

        members_batch = get_request_result(self.method, self.params_batch, 'users')
        return members_batch

    def get_members_all(self):
        self.members = []
        for i in range((self.get_members_count() // 100) + 1):
            self.members = self.members + self.get_members_batch(count=100, offset=i * 100)
        return self.members


class User:
    def __init__(self, user_id):
        self.user_id = user_id
        self.params = params.copy()
        self.method = 'friends.get'
        self.params.update({
            'user_id': user_id
        })

    def get_friends_count(self):
        friends_count = get_request_result(self.method, self.params, 'count')
        return friends_count

    def get_friends_batch(self, count, offset=0, fields=''):
        self.params_batch = self.params.copy()
        self.params_batch.update({
            'count': count,
            'offset': offset,
            'fields': fields
        })

        friends_batch = get_request_result(self.method, self.params_batch, 'items')
        return friends_batch

    def get_friends_all(self):
        self.friends = []
        for i in range((self.get_friends_count() // 100) + 1):
            self.friends = self.friends + self.get_friends_batch(count=100, offset=i * 100, fields='nickname')
        return self.friends


def concat_name(user):
    return user['last_name']+' '+user['first_name']


user = User('276048354')
friends = user.get_friends_all()

net = Network()
friends_ids = [i['id'] for i in friends]


for friend in friends:
    net.add_node(friend['id'], title = concat_name(friend))
    friend_instance = User(friend['id'])
    friends_of_friend = friend_instance.get_friends_all()
    for each in friends_of_friend:
        if each['id'] in friends_ids:
            if each['id'] not in net.get_nodes():
                net.add_node(each['id'], title = concat_name(each))
            net.add_edge(friend['id'], each['id'])

net.show("social graph.html")