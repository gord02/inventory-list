from mongoengine import connect, Document, FileField, StringField, FloatField, IntField

connect("inventory")

class Item(Document):
    """
    MongoDB Document for the inventory item Collection.

    Name: string -- name of the item
    Description: string -- description of the item
    Price: float -- price of item
    Quantity int -- amount of item
    photo: GridFS Object -- image stored in bytes, managed with GridFS
    """
    
    name = StringField(required=True)
    description = StringField(required=True)
    price = FloatField()
    quantity = IntField(required=True)
    photo = FileField()
    meta = {
            'indexes': [
            {'fields': ['$name', "$description", '$price'],
            'default_language': 'english',
            'weights': {'name': 3, 'description': 2, 'price': 1}
        }]
   }

def addItem(name, description, price, quantity):
    """
    Creates item in the MongoDB database based on parameters

    name: string -- name of the item
    Description: string -- description of the item
    Price: float -- price of item
    Quantity int -- amount of item
    filepath: string -- path to the file of image 
    """
    item = Item(name=name)
    item.description = description
    item.price = price
    item.quantity = quantity
    # fileHandle = open(filepath, "rb")
    # image.photo.put(fileHandle, filename=filepath)
    item.save()

if __name__ == "__main__":
    # instantiate variable to test the add image function
    name = "Office chair"
    description = "office chair with legs and back support"
    price = 123.45
    quantity = 5

    # run the addItem function to populate db
    addItem(name, description, price, quantity)
