"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planets, Favorite

# Configuración de la aplicación
app = Flask(__name__)
app.url_map.strict_slashes = False

# Configuración de la base de datos
db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialización de la base de datos y migraciones
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Manejo de errores como objetos JSON
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# Generar el sitemap con todos los endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# Rutas de usuarios
@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    all_users = [user.serialize() for user in users]
    return jsonify(all_users), 200

# Rutas de personas
@app.route('/people', methods=['GET'])
def get_all_people():
    people = People.query.all()
    all_people = [person.serialize() for person in people]
    return jsonify(all_people), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_one_person(people_id):
    person_query = People.query.filter_by(id=people_id).all()
    one_person = [person.serialize() for person in person_query]
    return jsonify(one_person), 200

# Rutas de planetas
@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planets.query.all()
    all_planets = [planet.serialize() for planet in planets]
    return jsonify(all_planets), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_one_planet(planet_id):
    planet_query = Planets.query.filter_by(id=planet_id).all()
    one_planet = [planet.serialize() for planet in planet_query]
    return jsonify(one_planet), 200

# Rutas de favoritos
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    planet = Planets.query.get(planet_id)

    new_favorite = Favorite(user_id=user_id, planet_id=planet_id)
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify(new_favorite.serialize()), 201

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    person = People.query.get(people_id)

    new_favorite = Favorite(user_id=user_id, people_id=people_id)
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify(new_favorite.serialize()), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def remove_favorite_planet(planet_id):
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"msg": "Favorite planet removed"}), 200

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def remove_favorite_people(people_id):
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)  
    favorite = Favorite.query.filter_by(user_id=user_id, people_id=people_id).first() 
    
    db.session.delete(favorite) 
    db.session.commit()

    return jsonify({"msg": "Favorite person removed"}), 200


# Ejecutar la aplicación
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
