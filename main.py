import logging
from base64 import b64encode

import redis
from mongoengine import connect
from flask import (Flask, render_template, request, send_file, redirect)

from schema import Item
from decoder import decode_redis


# Allows use to add to the database in mongoDB called inventory
connect(db='inventory')

app = Flask("__main__")

# Setup logging config
logging.basicConfig(level=logging.INFO)

@app.route("/")
def displayAllItems():
    """
    This route is used to display the items from the MongoDB database in the jinja2 frontend template.
    """
    items = list() 
    # Gets documents from Item collection
    mongoengineObjects = Item.objects()
    for obj in mongoengineObjects:
        ItemObject = {
            "name": obj.name,
            "description": obj.description,
            "price": obj.price,
            "quantity": obj.quantity,
            "image": obj.photo.read(),  # Reads item as binary 
            "id": obj.id
        }
        # Allows only type bytes to be added to item list
        if(type(ItemObject['image']) is bytes):
            # Converts bytes into base64 to be displayed in html
            ItemObject['image'] = b64encode(ItemObject['image']).decode("utf-8")
            # Pushes displayable items into list
            items.append(ItemObject)
        else:
            logging.error( "this item is not of type bytes", ItemObject)
           
    # Sends list of items to frontend for rendering
    return render_template("allItems.html", items=items)

@app.route("/", methods=['POST'])
def search():
    """
    This route is used to limit the results displayed in the frontend allowing user to filter through all the pictures in the database based on a specifc word search
    """
    items = list()
    if request.method == "POST":
        searchValue = request.form["searchValue"]
        mongoengineObjects = Item.objects.search_text(searchValue)

        for obj in mongoengineObjects:
            ItemObject = {
                "name": obj.name,
                "description": obj.description,
                "price": obj.price,
                "quantity": obj.quantity,
                "image": obj.photo.read(),   
                "id": obj.id
            }
            if(type(ItemObject['image']) is bytes):
                ItemObject['image'] = b64encode(ItemObject['image']).decode("utf-8")
                items.append(ItemObject)
            else:
                logging.error("this item is not of type bytes", ItemObject)

    return render_template("show.html", items=items)

@app.route("/addItem", methods=['GET','POST'])
def addItemToDB():
    """
    Route for adding an item to the database
    """
    if request.method == "POST":
        searchValue = request.form["searchValue"]
        description = request.form["description"]
        price = request.form["price"]
        quantity = request.form["quantity"]
        file = request.files["file"].read()

        # creates a document for item in collection item
        item = Item(name=searchValue)
        item.description = description
        item.price = price
        item.quantity = quantity

        # if empty use default blank photo
        item.photo.put(file, filename=(searchValue+".jpg"))                                 # !!!!!!

        item.save()

        return redirect("/")
    return render_template("form.html")

@app.route("/item/<id>", methods=['GET'])
def displayIndividualItem(id):
    """
    Route for displaying a single item based on id

    id: string -- id of item to be displayed in database
    """
    # redis configuration
    r = redis.Redis(host='localhost', port=6379, db=0)

    redisValue = r.hgetall(id)
    # Checks if the item is in Redis first, if the item is not found in Redis, the item is searched for in mongoDB
    if redisValue == {}:
        mongoengineObject = Item.objects(id=id).first()

        # If the item is not found in MongoDB, an error is logged and error page is rendered
        if mongoengineObject is None:
            logging.error("The user has tried to display item that is not available, item id doesn't correspond to an item Id: '", id ,"' was not found")    
            return render_template("error.html")

        ItemObject = {
            "name": mongoengineObject.name, 
            "description": mongoengineObject.description,
            "price": mongoengineObject.price,
            "quantity": mongoengineObject.quantity,
            "image": mongoengineObject.photo.read(), 
            "id": str(mongoengineObject.id)
        }
        ItemObject['image'] = b64encode(ItemObject['image']).decode("utf-8")

        # Adds the item to Redis so that the next time it is retrived in this route it will be found in Redis which is a faster process than MongoDB
        r.hmset(id, ItemObject)

        imgObjectToSendToHtml = ItemObject
    else:
        # If the item was found in Redis it will be sent to frontend
        item = decode_redis(redisValue)
        imgObjectToSendToHtml = item

    return render_template("anItem.html", item=imgObjectToSendToHtml)

@app.route("/delete/<id>", methods=['POST'])
def delete(id):
    """
    Route for deleting items from the database based on the id passed through url of post request

    id: string -- id of item to be deleted in database
    """
    if request.method == 'POST':
        # item is deleted and the if statement verifies that it was successful
        if(Item.objects(id=id).delete() != 1):
            logging.error("User tried to delete an item unsuccessfully. Id: ", id)

    return redirect("/")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """
    Route created to redirect to homepage of application if route is not already specified 

    path: string -- undefined url
    """
    return redirect("/")

app.run(debug=True)
