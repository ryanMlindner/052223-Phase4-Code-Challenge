#!/usr/bin/env python3

from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

class Restaurants(Resource):
    def get(self):
        restaurants_dict = [res.to_dict(rules=("-restaurant_pizzas",)) for res in Restaurant.query.all()]
        response = make_response(restaurants_dict, 200)
        return response
    
class RestaurantsByID(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter(Restaurant.id == id).first()
        if restaurant != None:
            response = make_response(restaurant.to_dict(), 200)
        else:
            response = make_response({"error": "Restaurant not found"}, 404)
        return response
    
    def delete(self, id):
        restaurant = Restaurant.query.filter(Restaurant.id == id).first()
        if restaurant != None:
            db.session.delete(restaurant)
            db.session.commit()
            response = make_response({}, 204)
        else:
            response = make_response({"error": "Restaurant not found"}, 404)
        return response

class Pizzas(Resource):
    def get(self):
        pizzas_dict = [pi.to_dict(rules=("-restaurant_pizzas",)) for pi in Pizza.query.all()]
        response = make_response(pizzas_dict, 200)
        return response

class Restaurant_Pizzas(Resource):
    def post(self):
        try:
            new_restaurant_pizza = RestaurantPizza(
                price= request.json["price"],
                pizza_id= request.json["pizza_id"],
                restaurant_id= request.json["restaurant_id"],
            )
            db.session.add(new_restaurant_pizza)
            db.session.commit()
            response = make_response(new_restaurant_pizza.to_dict(), 201)
            return response
        except ValueError:
            response = make_response({"errors": ["validation errors"]}, 400)
            return response



api.add_resource(Restaurants, "/restaurants")
api.add_resource(RestaurantsByID, "/restaurants/<int:id>")
api.add_resource(Pizzas, "/pizzas")
api.add_resource(Restaurant_Pizzas, "/restaurant_pizzas")

if __name__ == '__main__':
    app.run(port=5555, debug=True)
