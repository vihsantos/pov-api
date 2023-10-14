import json
import uuid
from datetime import datetime

from flask import request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from postgrest import APIError

from application import app
from application.repository.followers_repository import FollowersRepository
from application.repository.guide_repository import GuideRepository
from application.repository.localization_repository import LocalizationRepository
from application.repository.person_repository import PersonRepository
from application.repository.post_repository import PostRepository
from application.repository.user_repository import UserRepository

user = UserRepository()
post = PostRepository()
person = PersonRepository()
guide = GuideRepository()
followers = FollowersRepository()
localizations = LocalizationRepository()


@app.route("/")
def hello():
    dados = guide.findRegister("44.943.872/0001-69")
    print(dados)
    return "Hello, World!"


@app.route("/criarusuario", methods=['POST'])
def criar_usuario():
    try:
        modelo = request.get_json()
        print(modelo)

        guiasalvo = None
        usuariosalvo = None
        pessoasalvo = None

        if modelo.__len__() == 0:
            return "Nenhum dado foi enviado", 400

        if modelo['guide'] is True:
            guia = {
                "cod_cadastur": modelo["cadastur"],
                "areaatuacao": modelo["areatuacao"],
                "data_vencimento": modelo["data_vencimento"]
            }

            registro = guide.findRegister(guia['cod_cadastur'])

            if registro is None:
                return 'Registro não encontrado', 404

            guiasalvo = guide.createGuide(guia)

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

        pessoasalvo = person.createPerson(pessoa)

        usuariosalvo = user.createUser(usuario)

        print(guiasalvo)
        print(pessoasalvo)
        print(usuariosalvo)

        userperson = {
            "user_id": usuariosalvo[0]['id'],
            "person_id": pessoasalvo[0]['id']
        }

        person.createUserPerson(userperson)

        if guiasalvo != None:
            guideperson = {
                "user_id": usuariosalvo[0]['id'],
                "guide_id": guiasalvo[0]['id'],
                "person_id": pessoasalvo[0]['id']
            }

            guide.createUserGuide(guideperson)

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
        "userid": usuario[0]['id'],
        "guide": usuario[0]['guide']
    }

    return jsonify(result), 200


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

    localization = novoPost["localization"]

    localizacaoCriada = localizations.createLocalization(localization)

    novoPost['localization'] = localizacaoCriada[0]['id']

    post.createPost(novoPost)

    return "Salvo com sucesso!", 200


@app.route("/posts", methods=['GET'])
@jwt_required()
def getPosts():
    current_user = get_jwt_identity()
    posts = post.listarPostHome()

    if posts is None:
        return "Nenhum post encontrado!", 404

    return jsonify(posts), 200


@app.route("/posts", methods=['GET'])
@jwt_required()
def getPostsByUserId():
    current_user = get_jwt_identity()

    posts = post.buscarPostsDoUsuario(current_user)
    if posts is None:
        return "Nenhum post encontrado!", 404

    return jsonify(posts), 200


@app.route("/post/<id>", methods=['GET'])
def getPostByID(id):
    data = post.findByID(id)

    if data is None:
        return "Post não encontrado!", 404

    return data[0], 200


@app.route("/profileposts/<id>", methods=['GET'])
@jwt_required()
def findPostProfile(id):
    data = post.buscarPostsDoUsuario(id)

    if data is None:
        return "Nenhum post encontrado", 404

    return jsonify(data), 200


@app.route("/guides", methods=['GET'])
@jwt_required()
def getGuides():
    guias = guide.getGuides()

    if guias is None:
        return "Nenhum guia encontrado", 404

    return guias, 200


@app.route("/following", methods=['POST'])
@jwt_required()
def following():

    follow = request.get_json()

    followers.follow(follow)

    return "Salvo com sucesso!", 200


@app.route("/unfollow", methods=['DELETE'])
@jwt_required()
def unfollow():
    current_user = get_jwt_identity()

    return "Salvo com sucesso!", 200


@app.route("/usuario/<id>", methods=['GET'])
def buscarUsuario(id):

    usuario = user.findById(id)

    if usuario is None:
        return "Usuário não encontrado", 404

    seguidores = followers.getFollowersByID(id)
    seguindo = followers.getFollowingByID(id)

    usuario[0]["followers"] = seguidores
    usuario[0]["following"] = seguindo

    return usuario[0], 200

@app.route("/ranking/local", methods=['GET'])
@jwt_required()
def gerRankingByLocal():
    current_user = get_jwt_identity()

    dados = post.getTopPostsByLocal()

    return dados, 200