import json

from supabase import create_client

with open("application/config.json", "r") as f:
    appsettings = json.load(f)

supabase = create_client(appsettings["SUPABASE_URL"],appsettings["SUPABASE_KEY"])

class VoosRepository:
    def __init__(self):
        self.collection = supabase.table('voos')

    def createVoo(self, voo):
        self.collection.insert(voo).execute()

    def removeVoo(self, voo):
        self.collection.delete().eq("id", voo['id']).execute()