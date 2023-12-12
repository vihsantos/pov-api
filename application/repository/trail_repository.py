import json

from supabase import create_client

with open("application/config.json", "r") as f:
    appsettings = json.load(f)

supabase = create_client(appsettings["SUPABASE_URL"], appsettings["SUPABASE_KEY"])


class TrailRepository:
    def __init__(self):
        self.collection = supabase.table('trail')
        self.bucket = supabase.storage.from_('pov/trail')

    def createTrail(self, trail):
        self.collection.insert(trail).execute()

    def salvarTrailImage(self, file, filename, tipo):
        self.bucket.upload(filename, file, {"content-type": "image/" + tipo})