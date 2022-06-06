from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from random import choice

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)
    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

@app.route("/")
def home():
    return render_template("index.html")


## HTTP GET - Read Record
@app.route("/random")
def random():
    all_cafes = Cafe.query.all()
    random_cafe = choice(all_cafes)

    return jsonify(name=random_cafe.name, id=random_cafe.id, map_url=random_cafe.map_url,
                       location=random_cafe.location, seats=random_cafe.seats, has_toilet=random_cafe.has_toilet,
                       has_wifi=random_cafe.has_wifi, has_sockets=random_cafe.has_sockets,
                       can_take_calls=random_cafe.can_take_calls,
                       coffee_price=random_cafe.coffee_price)


@app.route("/all")
def all():
    cafes = db.session.query(Cafe).all()
    # This uses a List Comprehension but you could also split it into 3 lines.
    return jsonify(cafes=[cafe.to_dict() for cafe in cafes])

@app.route("/search")
def search():
    query_loc = request.args.get('loc')
    cafes = Cafe.query.filter_by(location=query_loc).all()
    if cafes:
        return jsonify(cafe=[cafe.to_dict() for cafe in cafes])
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})


## HTTP POST - Create Record
@app.route("/add", methods=['POST'])
def add():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})




## HTTP PUT/PATCH - Update Record
@app.route("/update-price/<cafe_id>", methods=['PATCH'])
def patch(cafe_id):
    cafe_to_update = Cafe.query.get(cafe_id)
    new_price = request.args.get('new_price')
    if cafe_to_update:
        cafe_to_update.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price"}), 200
    else:
        return jsonify(response={"error": "Not found in database"}), 400


## HTTP DELETE - Delete Record
@app.route("/delete/<cafe_id>", methods=['DELETE', 'GET'])
def delete(cafe_id):
    cafe_to_delete = Cafe.query.get(cafe_id)
    api = request.args.get('key')
    if api == "secret":
        if cafe_to_delete :
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted cafe"}), 200
        else:
            return jsonify(response={"error": "Not found in database"}), 400
    else:
        return jsonify(response={"error": "Sorry, that's not allowed. Make sure you have the correct api_key"}), 403

if __name__ == '__main__':
    app.run(debug=True)
