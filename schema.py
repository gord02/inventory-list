from mongoengine import connect, Document, FileField, StringField, FloatField, IntField

connect("imageRepo")

class Image(Document):
    """
    MongoDB Document for the image Collection.

    title: string -- title of the image
    description: string -- description of the image
    photo: GridFS Object -- image stored in bytes, managed with GridFS
    """
    
    title = StringField(required=True)
    description = StringField(required=True)
    photo = FileField(required=True)
    meta = {"strict": False}

def addImage(filepath, title, description):
    """
    Creates image in the MongoDB database based on parameters

    filepath: string -- path to the file of image 
    title: string -- title of the image
    description: string -- description of the image
    """
    image = Image(title=title)
    image.description = description
    fileHandle = open(filepath, "rb")
    image.photo.put(fileHandle, filename=filepath)
    image.save()

if __name__ == "__main__":
    # instantiate variable to test the add image function
    filepath = "Dog"
    title = "Dog in sweater"
    description = "Dog.jpg"

    # run the addImage function
    # addImage(filepath, title, description)

# ========================
connect("inventory")

class item(Document):
    """
    MongoDB Document for the inventory item Collection.

    Name: string -- name of the item
    Description: string -- description of the item
    Price: float -- price of item
    Quantity int -- amount of item
    """
    
    Name = StringField(required=True)
    description = StringField(required=True)
    price = FloatField(required=True)
    quantity = IntField(required=True)
    meta = {"strict": False}

def addItem(name, description, price, quantity):
    """
    Creates item in the MongoDB database based on parameters

    Name: string -- name of the item
    Description: string -- description of the item
    Price: float -- price of item
    Quantity int -- amount of item
    """
    item = Item(name=name)
    item.description = description
    item.price = price
    item.quantity = quantity
    item.save()

if __name__ == "__main__":
    # instantiate variable to test the add image function
    name = "Office chair"
    description = "office chair with legs and back support"
    price = 123.45
    quantity = 5

    # run the addImage function
    addItem(name, description, price, quantity)
