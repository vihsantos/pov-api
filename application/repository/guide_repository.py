import json
import firebase_admin
from firebase_admin import credentials, firestore

with open("application/config.json", "r") as f:
    appsettings = json.load(f)

certificate = credentials.Certificate(appsettings["secrets_path"])
firebaseApp = firebase_admin.initialize_app(certificate, {'databaseURL': appsettings['database_url']})
db = firestore.client()

class GuideRepository:

    def __init__(self):
        self.collection = db.reference("guide")

    def createGuide(self, guide):
        self.collection.add(guide)

    def getGuides(self):
        return self.collection.stream()