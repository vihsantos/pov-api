import json

from supabase import create_client

with open("application/config.json", "r") as f:
    appsettings = json.load(f)

supabase = create_client(appsettings["SUPABASE_URL"],appsettings["SUPABASE_KEY"])

class FollowersRepository:

    def __init__(self):
        self.collection = supabase.table('followers')

    def follow(self, follow):
        return self.collection.insert(follow).execute().data

    def unfollow(self, id):
        return self.collection.delete().eq("id", id).execute().data

    def getFollowersByID(self, id):
        return self.collection.select('*').eq("user_seguindo", id).execute().data

    def getFollowingByID(self, id):
        return self.collection.select('*').eq("user_seguidor", id).execute().data