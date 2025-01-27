import json

from supabase import create_client

from application.repository.person_repository import PersonRepository

with open("application/config.json", "r") as f:
    appsettings = json.load(f)

supabase = create_client(appsettings["SUPABASE_URL"], appsettings["SUPABASE_KEY"])

person = PersonRepository()

class TrailRepository:
    def __init__(self):
        self.collection = supabase.table('trails')
        self.bucket = supabase.storage.from_('trails')

    def createTrail(self, trail):
        self.collection.upsert(trail).execute()

    def salvarTrailImage(self, file, filename, tipo):
        self.bucket.upload(filename, file, {"content-type": "image/" + tipo})

    def buscarTrilhasDoGuia(self, id):
        trilhas = self.collection.select('id, name, description, occupation, files, user(id, username, ...user_person(...person(profile)))').eq('user', id).execute().data

        for trilha in trilhas:

            arquivos = trilha['files'].split(';')
            arquivos.pop()

            profile = trilha['user']['profile']
            trilha['user']['profile'] = person.getUrlIcon(profile)

            urls = ''

            for arq in arquivos:
                url = self.bucket.create_signed_url(arq, 180000)
                urls += url["signedURL"] + ";"

            trilha['files'] = urls

        return trilhas

    def buscarTrilhasRecentes(self):
        trilhas = self.collection.select('id, name, description, occupation, files, user(id, username, ...user_person(...person(profile))))').limit(5).execute().data

        for trilha in trilhas:

            arquivos = trilha['files'].split(';')
            arquivos.pop()

            profile = trilha['user']['profile']
            trilha['user']['profile'] = person.getUrlIcon(profile)

            urls = ''

            for arq in arquivos:
                url = self.bucket.create_signed_url(arq, 180000)
                urls += url["signedURL"] + ";"

            trilha['files'] = urls

        return trilhas

    def removeTrail(self, trail_id):

        filenames = self.collection.select('files').eq("id", trail_id).execute().data[0]["files"]
        files = filenames.split(';')

        for file in files:
            if file != "" or file is not None:
                self.bucket.remove(file)

        self.collection.delete().eq("id", trail_id).execute()

    def findTrailById(self, id):

        trilha = self.collection.select('id, name, description, occupation, files, user(id, username)').eq("id", id).execute().data[0]

        arquivos = trilha['files'].split(';')
        arquivos.pop()

        urls = ''

        for arq in arquivos:
            url = self.bucket.create_signed_url(arq, 180000)
            urls += url["signedURL"] + ";"

        trilha['files'] = urls

        return trilha