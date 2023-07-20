import json
from supabase import create_client

with open("application/config.json", "r") as f:
    appsettings = json.load(f)

supabase = create_client(appsettings["SUPABASE_URL"],appsettings["SUPABASE_KEY"])

class GuideRepository:

    def __init__(self):
        self.collection = supabase.table('guide')

    def createGuide(self, guide):
        self.collection.insert(guide).execute()

    def getGuides(self):
        return self.collection.select('*').execute()