from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem


engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)
session = DBSession()

@app.route("/")
@app.route('/hello')
def HelloWorld():
	items = session.query(MenuItem).all()
	output = ""
	for i in items:
		output += i.name + "</br>" + i.price + "</br>" + i.description + "</br>"
		output += "</br>"
	return output

@app.route("/restaurants/<int:restaurant_id>/")
def restaurantMenu(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id)
	return render_template('menu.html', restaurant=restaurant, items=items)

@app.route("/restaurants/<int:restaurant_id>/JSON/")
def restaurantMenuJSON(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id)
	return jsonify(MenuItems = [serialize(i) for i in items])

@app.route("/restaurants/<int:restaurant_id>/new/", methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
	if request.method == "POST":
		newItem = MenuItem(name=request.form['name'], restaurant_id=restaurant_id)
		session.add(newItem)
		session.commit()
		flash("New menu item created.")
		return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
	return render_template('newmenuitem.html', restaurant_id=restaurant_id)

@app.route("/restaurants/<int:restaurant_id>/<int:item_id>/edit/", methods=["GET", "POST"])
def  editMenuItem(restaurant_id, item_id):
	item = session.query(MenuItem).filter_by(id=item_id).one()
	orig_name = item.name
	if request.method == "POST":
		if request.form['name']:
			item.name = request.form['name']
		session.add(item)
		session.commit()
		flash("Item edited: {0} changed to {1}".format(orig_name, item.name))
		return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
	return render_template("editmenuitem.html",  restaurant_id = restaurant_id, item=item)

@app.route("/restaurants/<int:restaurant_id>/<int:item_id>/delete/", methods = ["GET", "POST"])
def deleteMenuItem(restaurant_id, item_id):
	item = session.query(MenuItem).filter_by(id=item_id).one()
	if request.method == "POST":
		session.delete(item)
		session.commit()
		flash(item.name + " deleted.")
		return redirect(url_for("restaurantMenu", restaurant_id=restaurant_id))
	return render_template("deletemenuitem.html", restaurant_id=restaurant_id, item=item)

@app.route("/restaurants/<int:restaurant_id>/<int:item_id>/JSON/")
def MenuItemJSON(restaurant_id, item_id):
	item = session.query(MenuItem).filter_by(id=item_id).one()
	return jsonify(MenuItem = serialize(item))

def serialize(menu):
	assert isinstance(menu, MenuItem)
	return {"name": menu.name, "description": menu.description, "id": menu.id, "price": menu.price, "course": menu.course}

if __name__ == "__main__":
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = "0.0.0.0", port = 5000)