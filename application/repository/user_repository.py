import json

from supabase import create_client

with open("application/config.json", "r") as f:
    appsettings = json.load(f)

supabase = create_client(appsettings["SUPABASE_URL"], appsettings["SUPABASE_KEY"])

class UserRepository:

    def __init__(self):
        self.collection = supabase.table('user')
        self.bucket = supabase.storage.from_('profile')

    def createUser(self, user):
        return self.collection.insert(user).execute().data

    def getUsers(self):
        return self.collection.select('*').execute()

    def findByLogin(self, login):
        return self.collection.select('*').eq("username", login["username"]).eq("password", login["password"]).execute().data

    def findById(self, id):
        return self.collection.select('username, guide').eq("id", id).execute().data[0]

    def findByUsername(self, username):
        dado = self.collection.select('username').eq("username", username).execute().data
        if dado.__len__() != 0:
            return True

        return False

