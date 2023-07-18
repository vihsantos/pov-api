from flask import request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from application import app
from application.repository.user_repository import UserRepository

user = UserRepository()


@app.route("/")
def hello():
    return "Hello, World!"


@app.route("/criarusuario", methods=['POST'])
def criar_usuario():
    modelo = request.get_json()
    user.createUser(modelo)

    # usuario = user__collection.find_one({"email":  modelo['email']})
    #
    # if usuario is not None:
    #     return "Usuário já existente", 409
    #
    # #result = user__collection.insert_one(modelo)

    return "Salvo com sucesso", 201


@app.route("/users", methods=['GET'])
def buscar_usuarios():
    dados = user.getUsers()
    result = [doc.to_dict() for doc in dados]
    return result, 200


@app.route("/usuario/<email>", methods=['GET'])
def buscar_usuario(email):
    # result = user.findByEmail(email)
    # dado = [doc.to_dict() for doc in result]
    #
    # if dado is None:
    #     return "Usuário não encontrado", 404

    return "dado", 200


@app.route("/acesso", methods=['POST'])
def acessar():
    login = request.get_json()
    usuario = [doc.to_dict() for doc in user.findByLogin(login)]

    if usuario is None:
        return "Não foi possivel realizar o acesso", 401

    token = create_access_token(usuario[0]["id"])
    return token, 200
#
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
