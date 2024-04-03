import csv
import datetime
import json

from supabase import create_client

with open("application/config.json", "r") as f:
    appsettings = json.load(f)

supabase = create_client(appsettings["SUPABASE_URL"],appsettings["SUPABASE_KEY"])


class GuideRepository:
    def __init__(self):
        self.collection = supabase.table('guide')
        self.collection_userguide = supabase.table('user_guide')
        self.guideData = self.csv_to_list("application/services/guia-de-turismo.csv")

    def createGuide(self, guide):
        return self.collection.insert(guide).execute().data

    def getGuides(self):
        return self.collection.select('*').execute()

    def findRegister(self, certificado, validade):

        registro = list(filter(lambda item: item['Número do Certificado'] == certificado and datetime.datetime.strptime(item['Validade do Certificado'], '%d/%m/%Y') == validade , self.guideData))

        return registro

    def getGuides(self):
        guias = self.collection_userguide.select('guide(areaatuacao, cod_cadastur), user(id, username), person(filename)').execute().data
        for guia in guias:

            filename = guia['person']['filename']
            guia.pop('person')

            guia['user']['profileicon'] = filename if "" else ""



        return guias

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

    def createUserGuide(self, guidePerson):
        return self.collection_userguide.insert(guidePerson).execute().data