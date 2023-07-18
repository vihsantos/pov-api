from flask import Flask
from flask_jwt_extended import JWTManager
import datetime

app = Flask(__name__)
jwt = JWTManager(app)

app.config['JWT_SECRET_KEY'] = 'sasasasas'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(seconds=18000)

app.secret_key = "algo"
app.config['SECRET_KEY'] = "algo"

from application import routes

