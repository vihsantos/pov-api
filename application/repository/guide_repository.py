import csv
import datetime
import json

from supabase import create_client

from application.repository.person_repository import PersonRepository

with open("application/config.json", "r") as f:
    appsettings = json.load(f)

supabase = create_client(appsettings["SUPABASE_URL"],appsettings["SUPABASE_KEY"])

person = PersonRepository()

class GuideRepository:
    def __init__(self):
        self.collection = supabase.table('guide')
        self.collection_userguide = supabase.table('user_guide')
        self.guideData = self.csv_to_list("application/services/guia-de-turismo.csv")

    def createGuide(self, guide):
        return self.collection.insert(guide).execute().data

    def getGuides(self):
        return self.collection.select('*').execute()

    def findRegister(self, guia):
        registro = list(
            filter(lambda item: item['Número do Certificado'] == guia["cod_cadastur"]
                                and datetime.datetime.strptime(item['Validade do Certificado'], '%d/%m/%Y') == guia["data_vencimento"]
                   and item['UF'] == guia["estado"] and item['Município'] == guia["municipio"]
                   , self.guideData))

        return registro

    def getGuides(self):
        guias = self.collection_userguide.select('guide(areaatuacao, cod_cadastur), user(id, username, ...user_person(...person(profile)))').execute().data
        for guia in guias:
            profile = guia['user']['profile']
            guia['user']['profile'] = person.getUrlIcon(profile)

        return guias

    def searchGuidesByEstadoAndMunicipio(self, estado, municipio):
        guias = (self.collection_userguide.select('guide(areaatuacao, cod_cadastur, estado, municipio), '
                                                 'user(id, username, ...user_person(...person(profile)))')
                 .eq('guide.estado', estado)
                 .eq('guide.municipio', municipio)
                 .execute().data)

        for guia in guias:
            profile = guia['user']['profile']
            guia['user']['profile'] = person.getUrlIcon(profile)

        return guias

    def searchGuidesByEstado(self, estado):
        guias = (self.collection_userguide.select('guide(areaatuacao, cod_cadastur, estado, municipio), '
                                                 'user(id, username, ...user_person(...person(profile)))')
                 .eq('guide.estado', estado)
                 .execute().data)

        for guia in guias:
            profile = guia['user']['profile']
            guia['user']['profile'] = person.getUrlIcon(profile)

        return guias

    def searchGuidesByMunicipio(self, municipio):
        guias = (self.collection_userguide.select('guide(areaatuacao, cod_cadastur, estado, municipio), '
                                                 'user(id, username, ...user_person(...person(profile)))')
                 .eq('guide.municipio', municipio)
                 .execute().data)

        for guia in guias:
            profile = guia['user']['profile']
            guia['user']['profile'] = person.getUrlIcon(profile)

        return guias

    def csv_to_list(self, path):
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

    def getInfosGuide(self, user):
        guide_id = self.collection_userguide.select('guide_id').eq("user_id", user).execute().data[0]

        guide = self.collection.select('cod_cadastur, data_vencimento, areaatuacao, estado, municipio, contato').eq("id", guide_id["guide_id"]).execute().data[0]

        return guide

    def alterarContato(self, contato, user):
        guide_id = self.collection_userguide.select('guide_id').eq("user_id", user).execute().data[0]

        self.collection.update({"contato": contato}).eq("id", id).execute()


