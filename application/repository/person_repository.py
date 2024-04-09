import json

from supabase import create_client

with open("application/config.json", "r") as f:
    appsettings = json.load(f)

supabase = create_client(appsettings["SUPABASE_URL"],appsettings["SUPABASE_KEY"])

class PersonRepository:
    def __init__(self):
        self.collection = supabase.table('person')
        self.collection_userperson = supabase.table('user_person')
        self.bucket = supabase.storage.from_('pov/person')

    def createPerson(self, person):
        return self.collection.insert(person).execute().data

    def createUserPerson(self, userperson):
        return self.collection_userperson.insert(userperson).execute().data

    def findUserPersonByUser(self, user):
        return self.collection_userperson.select("*").eq("user_id", user).execute().data

    def findUrlProfileIcon(self, user):
        user_person = self.findUserPersonByUser(user)[0]

        filename = self.collection.select('filename').eq('id', user_person["person_id"]).execute().data[0]

        if filename["filename"] is None or "":
            return None

        url = self.bucket.create_signed_url(filename["filename"], 180000)

        return url["signedURL"]

    def addUserIcon(self, file, filename, tipo, user):
        self.bucket.upload(filename, file, {"content-type": "image/" + tipo})

        user_person = self.findUserPersonByUser(user)[0]

        self.collection.update({'filename': filename}).eq('id', user_person["person_id"]).execute()