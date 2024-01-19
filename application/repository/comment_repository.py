import json

from supabase import create_client

with open("application/config.json", "r") as f:
    appsettings = json.load(f)

supabase = create_client(appsettings["SUPABASE_URL"], appsettings["SUPABASE_KEY"])


class CommentRepository:
    def __init__(self):
        self.collection = supabase.table('comment')

    def createComment(self, comment):
        self.collection.insert(comment).execute()

    def findCommentsOfPost(self, post_id):
        comments = self.collection.select('id, description, user(id, username)').eq('post_id', post_id).execute().data
        return comments

    def findCommentsOfTrail(self, trail_id):
        comments = self.collection.select('id, description, user(id, username)').eq('trail_id', trail_id).execute().data
        return comments
