import json

from supabase import create_client

with open("application/config.json", "r") as f:
    appsettings = json.load(f)

supabase = create_client(appsettings["SUPABASE_URL"],appsettings["SUPABASE_KEY"])

class PostRepository:

    def __init__(self):
        self.collection = supabase.table('post')

    def createPost(self, post):
        self.collection.insert(post).execute()

    def findByID(self, ID):
        self.collection.select('*').eq("id", ID).execute()


