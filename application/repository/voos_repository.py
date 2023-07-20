import json

from supabase import create_client

with open("application/config.json", "r") as f:
    appsettings = json.load(f)

supabase = create_client(appsettings["SUPABASE_URL"],appsettings["SUPABASE_KEY"])

class VoosRepository:
    def __init__(self):
        self.collection = supabase.table('voos')

    def createVoos(self, voos):
        self.collection.insert(voos).execute()