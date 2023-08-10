import io
import json
import uuid
from datetime import datetime

from flask import request, jsonify, send_file
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from postgrest import APIError

from application import app
from application.repository.person_repository import PersonRepository
from application.repository.post_repository import PostRepository
from application.repository.user_repository import UserRepository

user = UserRepository()
post = PostRepository()
person = PersonRepository()


@app.route("/")
def hello():
    return "Hello, World!"


@app.route("/criarusuario", methods=['POST'])
def criar_usuario():
    try:
        modelo = request.get_json()

        if modelo.__len__() == 0:
            return "Nenhum dado foi enviado", 400

        if modelo['guide'] is True:
            return "Olá"

        pessoa = {
            "nome": modelo["nome"],
            "data_nascimento": modelo["data_nascimento"],
            "email": modelo["email"]
        }

        usuario = {
            "username": modelo["username"],
            "password": modelo["password"],
            "guide": modelo["guide"]
        }

        person.createPerson(pessoa)

        user.createUser(usuario)

        return "Salvo com sucesso", 201

    except APIError as e:

        if e.message.__contains__("duplicate key"):
            return "Usuário existente", 400

        return "aaa", 400


@app.route("/acesso", methods=['POST'])
def acessar():
    login = request.get_json()

    usuario = user.findByLogin(login)

    if usuario is None or usuario.__len__() == 0:
        return "Não foi possivel realizar o acesso", 401

    result = {
        "token": create_access_token(usuario[0]["id"]),
        "acessoem": datetime.now().__str__()
    }

    return jsonify(result), 200


# @app.route("/usuariolocalizacao", methods =  ['GET'])
# @jwt_required()
# def buscarLocalizacaoPorUsuario():
#     current_user = get_jwt_identity()
#     localizacao = user__collection.find_one({"_id": ObjectId(current_user['$oid'])}, {"_id": 0, "localizacao": 1})
#
#     if localizacao is None:
#         return "Localização não encontrada", 404
#
#     return jsonify(localizacao)

@app.route("/teste", methods=['POST'])
@jwt_required()
def enviarImagemPost():
    current_user = get_jwt_identity()

    file = request.files['arquivo'].read()
    name = request.files['arquivo'].filename.split('.')
    filename = str(uuid.uuid4()) + '.' + name[1]
    post.salvarPostImage(file, filename, name[1])


    dados = request.values['dados']

    novoPost = json.loads(dados)
    novoPost["user_id"] = current_user
    novoPost["data_criacao"] = datetime.now().__str__()
    novoPost['filename'] = filename

    post.createPost(novoPost)

    return "Salvo com sucesso!", 200


@app.route("/newpost", methods=['POST'])
@jwt_required()
def criarPost():
    current_user = get_jwt_identity()

    novoPost = request.get_json()
    novoPost["user_id"] = current_user
    novoPost["data_criacao"] = datetime.now().__str__()

    post.createPost(novoPost)

    return "Salvo com sucesso!", 200

@app.route("/post/<id>", methods=['GET'])
@jwt_required()
def buscarPostPorID(id):
    current_user = get_jwt_identity()

    data = post.findByID(id)

    if data is None:
        return "Post não encontrado", 404

    return jsonify(data), 200

@app.route("/posts", methods=['GET'])
@jwt_required()
def getPosts():
    current_user = get_jwt_identity()
    posts = post.listarPostHome()
    if posts is None:
        return "Nenhum post encontrado!", 404

    return jsonify(posts), 200

