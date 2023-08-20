import csv
import json
from supabase import create_client

with open("application/config.json", "r") as f:
    appsettings = json.load(f)

supabase = create_client(appsettings["SUPABASE_URL"],appsettings["SUPABASE_KEY"])


class GuideRepository:
    def __init__(self):
        self.collection = supabase.table('guide')
        self.guideData = self.csv_to_list("application/services/guia-de-turismo.csv")

    def createGuide(self, guide):
        self.collection.insert(guide).execute()

    def getGuides(self):
        return self.collection.select('*').execute()

    def findRegister(self, certificado):
        registro = list(filter(lambda item: item['Número do Certificado'] == certificado, self.guideData))
        return registro


    def csv_to_list(self,path):
        dicts = []

        # read csv file
        with open(path, encoding='utf-8') as csvf:
            # load csv file data using csv library's dictionary reader
            leitor_de_csv = csv.DictReader(csvf)

            # convert each csv row into python dict
            for row in leitor_de_csv:
                # add this python dict in list
                dicts.append(row)
        return dicts