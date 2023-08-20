import json
import uuid

from supabase import create_client

with open("application/config.json", "r") as f:
    appsettings = json.load(f)

supabase = create_client(appsettings["SUPABASE_URL"], appsettings["SUPABASE_KEY"])


class UserRepository:

    def __init__(self):
        self.collection = supabase.table('user')

    def createUser(self, user):
        self.collection.insert(user).execute()

    def getUsers(self):
        return self.collection.select('*').execute()

    # def findByEmail(self, email):
    #     return self.collection.select('*').eq('')

    def findByLogin(self, login):
        return self.collection.select('*').eq("username", login["username"]).eq("password", login["password"]).execute().data

    def findById(self, id):
        return id

    def findByUsername(self, username):
        dado = self.collection.select('username').eq("username", username).execute().data
        if dado.__len__() is not 0:
            return True

        return False

