import json

from supabase import create_client

with open("application/config.json", "r") as f:
    appsettings = json.load(f)

supabase = create_client(appsettings["SUPABASE_URL"], appsettings["SUPABASE_KEY"])


class LocalizationRepository:
    def __init__(self):
        self.collection = supabase.table('localization')

    def createLocalization(self, localization):
        dado = self.collection.insert(localization).execute()
        return dado.data
