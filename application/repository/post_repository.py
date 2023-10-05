import json

from supabase import create_client

with open("application/config.json", "r") as f:
    appsettings = json.load(f)

supabase = create_client(appsettings["SUPABASE_URL"], appsettings["SUPABASE_KEY"])


class PostRepository:

    def __init__(self):
        self.collection = supabase.table('post')
        self.bucket = supabase.storage.from_('pov/posts')

    def createPost(self, post):
        self.collection.insert(post).execute()

    def findByID(self, ID):
        post = self.collection.select('*, comment(*), voos(*), user(id, username)').eq("id", ID).execute().data

        url = self.bucket.create_signed_url(post[0]['filename'], 180000)
        post[0]['image_url'] = url["signedURL"]
        post[0].pop('filename')
        post[0].pop('user_id')

        return post

    def salvarPostImage(self, file, filename, type):
        self.bucket.upload(filename, file, {"content-type": "image/" + type})

    def buscarImagemPost(self, image_url):
        return self.bucket.download(image_url)

    def buscarUrlImagePost(self, image_url):
        return self.bucket.get_public_url(image_url)

    def listarPostHome(self):
        posts = self.collection.select(
            'id, filename, description, stars, localization(*), user(id, username)').limit(10).order("data_criacao", desc=True).execute().data

        for post in posts:
            url = self.bucket.create_signed_url(post['filename'], 180000)
            post['image_url'] = url["signedURL"]
            post.pop('filename')

        return posts

    def buscarPostsDoUsuario(self, userid):
        posts = self.collection.select(
            'id, filename, stars').eq("user_id", userid).order("data_criacao", desc=True).execute().data

        for post in posts:
            url = self.bucket.create_signed_url(post['filename'], 180000)
            post['image_url'] = url["signedURL"]
            post.pop('filename')

        return posts

    def getTopPosts(self):
        posts = self.collection.select(
            'id, filename, stars').eq("stars", 5).order("data_criacao", desc=True).execute().data