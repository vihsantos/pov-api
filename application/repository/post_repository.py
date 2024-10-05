import json
from supabase import create_client
from application.repository.person_repository import PersonRepository

with open("application/config.json", "r") as f:
    appsettings = json.load(f)

supabase = create_client(appsettings["SUPABASE_URL"], appsettings["SUPABASE_KEY"])

person = PersonRepository()


class PostRepository:

    def __init__(self):
        self.collection = supabase.table('post')
        self.bucket = supabase.storage.from_('posts')

    def createPost(self, post):
        self.collection.insert(post).execute()

    def findByID(self, ID):
        post = self.collection.select('*, localization(lat, long, local), comment(*), voos(*), user(id, username, ...user_person(...person(profile)))').eq(
            "id", ID).execute().data

        url = self.bucket.create_signed_url(post[0]['filename'], 180000)
        post[0]['image_url'] = url["signedURL"]
        post[0].pop('filename')
        post[0].pop('user_id')
        profile = post[0]['user']['profile']
        if profile is not None:
            post[0]['user']['profile'] = person.getUrlIcon(profile)

        return post

    def salvarPostImage(self, file, filename, tipo):
        self.bucket.upload(filename, file, {"content-type": "image/" + tipo})

    def listarTopPostsHome(self):
        posts = self.collection.select(
            'id, filename, description, stars, localization(lat, long, local), '
            'user(id, username, ...user_person(...person(profile)))').eq("stars", 5).limit(10).order("data_criacao", desc=True).execute().data

        for post in posts:
            url = self.bucket.create_signed_url(post['filename'], 180000)
            post['image_url'] = url["signedURL"]
            post.pop('filename')
            profile = post['user']['profile']
            if profile is not None:
                post['user']['profile'] = person.getUrlIcon(profile)

        return posts

    def buscarPostsDoUsuario(self, userid):
        posts = self.collection.select(
            'id, filename, stars').eq("user_id", userid).order("data_criacao", desc=True).execute().data

        for post in posts:
            url = self.bucket.create_signed_url(post['filename'], 180000)
            post['image_url'] = url["signedURL"]
            post.pop('filename')

        return posts

    def getTopPostsByLocal(self):
        posts = supabase.rpc('ranking_by_local', params={}).execute().data
        return posts

    def getDataRankingByLocal(self, local):
        rankings = supabase.rpc('search_ranking_by_local', params={"nome": local}).execute().data
        return rankings

    def getPosts(self, take, skip):
        posts = self.collection.select(
            'id, filename, description, stars, localization(lat, long, local), '
            'user(id, username, ...user_person(...person(profile)))').range(take,skip).order("data_criacao",
                                                                                                     desc=True).execute().data

        for post in posts:
            url = self.bucket.create_signed_url(post['filename'], 180000)
            post['image_url'] = url["signedURL"]
            post.pop('filename')
            profile = post['user']['profile']
            if profile is not None:
                post['user']['profile'] = person.getUrlIcon(profile)

        return posts

    def getPostsOfFollowing(self, take, skip, ids):
        posts = (self.collection.select(
            'id, filename, description, stars, localization(lat, long, local), '
            'user(id, username, ...user_person(...person(profile)))').range(take,skip).order("data_criacao", desc=True).execute().data)

        postfiltrados = []

        for post in posts:
            id = post['user']['id']

            if ids.__contains__(id):
                postfiltrados.append(post)

        for post in postfiltrados:
            url = self.bucket.create_signed_url(post['filename'], 180000)
            post['image_url'] = url["signedURL"]
            post.pop('filename')
            profile = post['user']['profile']
            if profile is not None:
                post['user']['profile'] = person.getUrlIcon(profile)

        return postfiltrados

    def removePost(self, post_id):

        arquivo = self.collection.select('filename').eq("id", post_id).execute().data[0]["filename"]

        print(arquivo)

        self.bucket.remove([arquivo])

        self.collection.delete().eq("id", post_id).execute()

