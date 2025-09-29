from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from random import randint

'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        return {column.name:getattr(self,column.name) for column in self.__table__.columns}

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random")
def random():
    cafe_id = randint(1,21)
    cafe = Cafe.query.get_or_404(cafe_id)
    return jsonify(cafe={
        "id": cafe.id,
        "name": cafe.name,
        "location": cafe.location,
        "map_url": cafe.map_url,
        "img_url": cafe.img_url,
        "seats": cafe.seats,
        "coffee_price": cafe.coffee_price,
        "has_wifi": cafe.has_wifi,
        "has_toilet": cafe.has_toilet,
        "has_sockets": cafe.has_sockets,
        "can_take_calls": cafe.can_take_calls,
    })

@app.route("/all")
def all_cafes():
    cafes = Cafe.query.all()
    return jsonify(cafes=[cafe.to_dict() for cafe in cafes]) ##list comprehension

@app.route("/search")
def search():
    loc = request.args.get('loc')
    if loc:
        cafe = Cafe.query.filter_by(location=loc).all()
        if cafe:
            return jsonify(cafe=[caf.to_dict() for caf in cafe])
        else:
            return jsonify(error={"not found": "sorry we dont have any cafe in your location"})
    else:
        return jsonify(error={"Bad request": "Please provide a location"})

# HTTP POST - Create Record
@app.route("/add",methods=["POST"])
def add():
    new_cafe = Cafe(
        name=request.form.get("name"),
        location=request.form.get("location"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
        has_wifi=bool(request.form.get("has_wifi")),
        has_toilet=bool(request.form.get("has_toilet")),
        has_sockets=bool(request.form.get("has_sockets")),
        can_take_calls=bool(request.form.get("can_take_calls")),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(Response={"success": "Successfully added a new cafe"})


# HTTP PUT/PATCH - Update Record
@app.route("/patch/<cafe_id>",methods=["PATCH"])
def patch(cafe_id):
    try:
        cafe = Cafe.query.get(cafe_id)
        new_price = request.args.get("coffee_price")
        if new_price:
            cafe.coffee_price = new_price
            db.session.commit()
            return jsonify(success="Successfully updated coffee price")
        else:
            return jsonify(error={"Bad request":"Please provide a new coffee price"})
    except AttributeError:
        return jsonify(error={"Bad request":"No cafe with that id found"})

# HTTP DELETE - Delete Record
@app.route("/report-closed/<cafe_id>",methods=["DELETE"])
def delete(cafe_id):
    try:
        cafe_to_delete = Cafe.query.get(cafe_id)
        api_key = request.args.get("api_key")
        if api_key == "Welovesofi":
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(success="Successfully deleted cafe")
        else:
            return jsonify(error={"Unauthorized":"Please provide a valid API key"})
    except AttributeError:
        return jsonify(error={"Bad request":"No cafe with that id found"})




if __name__ == '__main__':
    app.run(debug=True)




