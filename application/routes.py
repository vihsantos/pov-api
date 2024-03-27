import json
import uuid
from datetime import datetime

from flask import request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from postgrest import APIError

from application import app
from application.repository.comment_repository import CommentRepository
from application.repository.followers_repository import FollowersRepository
from application.repository.guide_repository import GuideRepository
from application.repository.localization_repository import LocalizationRepository
from application.repository.person_repository import PersonRepository
from application.repository.post_repository import PostRepository
from application.repository.trail_repository import TrailRepository
from application.repository.user_repository import UserRepository
from application.repository.voos_repository import VoosRepository

user = UserRepository()
post = PostRepository()
person = PersonRepository()
guide = GuideRepository()
followers = FollowersRepository()
localizations = LocalizationRepository()
trail = TrailRepository()
comment = CommentRepository()
voos = VoosRepository()

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

            registro = guide.findRegister(guia['cod_cadastur'], guia['data_vencimento'])

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

        userperson = {
            "user_id": usuariosalvo[0]['id'],
            "person_id": pessoasalvo[0]['id']
        }

        person.createUserPerson(userperson)

        if guiasalvo is not None:
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

        return "Ops! Ocorreu um erro!", 500


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


@app.route("/newpost", methods=['POST'])
@jwt_required()
def criarNovoPost():
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
    posts = post.listarTopPostsHome()

    if posts is None:
        return "Nenhum post encontrado!", 404

    return jsonify(posts), 200


@app.route("/post/<id>", methods=['GET'])
def getPostByID(id):
    data = post.findByID(id)

    if data is None:
        return "Post não encontrado!", 404

    count = comment.findCountCommentsByPost(id)

    data[0]['comentarios'] = count

    return data[0], 200


@app.route("/ranking/local", methods=['GET'])
@jwt_required()
def getRankingByLocal():
    dados = post.getTopPostsByLocal()

    return dados, 200


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


@app.route("/usuario/<id>", methods=['GET'])
@jwt_required()
def buscarUsuario(id):
    usuario = user.findById(id)

    if usuario is None:
        return "Usuário não encontrado", 404

    seguidores = followers.getFollowersByID(id)
    seguindo = followers.getFollowingByID(id)

    usuario["followers"] = seguidores
    usuario["following"] = seguindo

    return usuario, 200


@app.route("/following/<id>", methods=['POST'])
@jwt_required()
def following(id):
    current_user = get_jwt_identity()
    follow = {
        "user_seguidor": current_user,
        "user_seguindo": id
    }

    followers.follow(follow)

    return "Salvo com sucesso!", 200


@app.route("/unfollow/<id>", methods=['DELETE'])
@jwt_required()
def unfollow(id):
    current_user = get_jwt_identity()

    unfollow = {
        "user_seguidor": current_user,
        "user_seguindo": id
    }

    followers.unfollow(unfollow)

    return "Salvo com sucesso!", 200


@app.route("/newtrail", methods=['POST'])
@jwt_required()
def novaTrilha():
    current_user = get_jwt_identity()

    filenames = ""

    arquivos = request.files

    dados = request.values['dados']

    trilhaInformacoes = json.loads(dados)

    for file in arquivos:
        nomes = file.split('.')
        nomeArquivo = str(uuid.uuid4()) + '.' + nomes[1]
        filenames += nomeArquivo + ";"
        trail.salvarTrailImage(arquivos[file].read(), nomeArquivo, nomes[1])

    trilhaInformacoes['files'] = filenames
    trilhaInformacoes['user'] = current_user
    trilhaInformacoes["data_criacao"] = datetime.now().__str__()
    trilhaInformacoes.pop('id')

    trail.createTrail(trilhaInformacoes)

    return "Salvo com sucesso!", 200


@app.route("/trails/<id>", methods=['GET'])
@jwt_required()
def buscarTrilhasPorUsuario(id):
    trilhas = trail.buscarTrilhasDoGuia(id)

    if trilhas is None:
        return "Nada encontrado", 404

    return trilhas


@app.route("/trails", methods=['GET'])
@jwt_required()
def buscarTrilhas():
    current_user = get_jwt_identity()
    trilhas = trail.buscarTrilhasRecentes()
    
    if trilhas is None:
        return "Nada encontrado", 404

    return trilhas


@app.route("/commentByPost/<id>", methods=['GET'])
@jwt_required()
def buscarComentariosPorPost(id):
    current_user = get_jwt_identity()

    comentarios = comment.findCommentsOfPost(id)

    if comentarios is None:
        return "Nenhum comentário encontrado!", 404

    return comentarios


@app.route("/commentByTrail/<id>", methods=['GET'])
@jwt_required()
def buscarComentariosPorTrilha(id):
    current_user = get_jwt_identity()

    comentarios = comment.findCommentsOfTrail(id)

    if comentarios is None:
        return "Nenhum comentário encontrado!", 404

    return comentarios


@app.route("/comment", methods=['POST'])
@jwt_required()
def enviarComentario():
    try:
        current_user = get_jwt_identity()

        comentario = request.get_json()
        comentario["user_id"] = current_user
        comment.createComment(comentario)
        return "Foi!!", 200

    except APIError as e:
        return "Ops! Algo de errado aconteceu.", 500

@app.route("/addicon", methods=['POST'])
@jwt_required()
def adicionarIcon():
    try:
        current_user = get_jwt_identity()

        file = request.files['arquivo'].read()
        name = request.files['arquivo'].filename.split('.')
        filename = str(uuid.uuid4()) + '.' + name[1]

        person.addUserIcon(file, filename, name[1], current_user)

        return "Enviado", 200

    except APIError as e:
        return "Ops! Algo de errado aconteceu.", 500

@app.route("/isfollower/<id>", methods=['GET'])
@jwt_required()
def isFollower(id):
    try:
        current_user = get_jwt_identity()

        seguidor = {
            "user_seguidor": current_user,
            "user_seguindo": id
        }

        isFollower = followers.isFollower(seguidor)

        return json.dumps(isFollower), 200
    except APIError as e:
        return "Ops! Algo de errado aconteceu.", 500

@app.route("/addvooinpost/<id_post>", methods=['GET'])
@jwt_required()
def addVooInPost(id_post):
    try:
        current_user = get_jwt_identity()
        voo = {
            "user_id": current_user,
            "post_id": id_post
        }

        voos.createVoos(voo)
        return "Foi!!", 200

    except APIError as e:
        return "Ops! Algo de errado aconteceu.", 500