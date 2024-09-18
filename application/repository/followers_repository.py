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

    def unfollow(self, unfollow):
        return self.collection.delete().eq("user_seguidor", unfollow["user_seguidor"]).eq("user_seguindo", unfollow["user_seguindo"]).execute().data

    def getFollowersByID(self, id):
        return self.collection.select('*').eq("user_seguindo", id).execute().data

    def getFollowingByID(self, id):
        return self.collection.select('*').eq("user_seguidor", id).execute().data

    def getFollowingIDsByID(self, id):
        users = self.collection.select('user_seguindo').eq("user_seguidor", id).execute().data

        ids = []

        for user in users:
            id = int(user["user_seguindo"])
            ids.append(id)

        return ids



    def isFollower(self, seguidor):
        dado = self.collection.select('*').eq("user_seguidor", seguidor["user_seguidor"]).eq("user_seguindo", seguidor["user_seguindo"]).execute().data

        if dado.__len__() != 0:
            return True

        return False
