import entity_model as em
import inflect
from pymongo.mongo_client import MongoClient
p = inflect.engine()
client = MongoClient("192.168.1.231", 27017)
#client.noisy_NER.authenticate("fwadmin", "fwadmin")
db = client['noisy_NER']
entity_collection = db['entity']
new_c = db['questions']

# Function to delete the entitys from databases which are from commensense_linguist
# we have the list of all commenesense linguist and here we have the query to remove
# all the elemets fom entity collection
#
def removeMongoEntityAndQuestion(entity):
    entity_collection.remove(
                             {'intended_trainer':'Foodweasel_trainer',
                             "surface_text": entity,
                             }
                             )
    new_c.remove(
    {"question": entity
    })
    entity_collection.remove({"surface_text" : {"$in":["6","66"]}})
def updateDatabase():
    list = range(41, 10001)
    complete = []
#    entity_collection.remove({"surface_text" : {"$in":["6","66"]}})
    for num in list:
#       removeMongoEntityAndQuestion(num)
        num = str(num)
        complete.append(num)
        num_text = p.number_to_words(num).replace("-", " ")
        num_text = str(num_text)
        complete.append(num_text)
#       removeMongoEntityAndQuestion(num_text);
    final = complete + ['bottle', 'pitcher', 'can', 'and', '&', '2', '20', 'with', 'w/', 'along with', 'small', 'medium', 'large', 'big', '1', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '21', '22', '23', '24', '25', '26', '27', '28', '35', '37', '39', '29', '30', '31', '32', '33', '34', '36', '38', '40', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'ninteen', 'twenty', 'twenty one', 'twenty two', 'twenty three', 'twenty four', 'twenty five', 'twenty six', 'twenty seven', 'twenty eight', 'twenty nine', 'thirty', 'thirty one', 'thirty two', 'thirty three', 'thirty four', 'thirty five', 'thirty six', 'thirty seven', 'thirty eight', 'thirty nine', 'fourty', 'a', 'an', ',', 'extra', 'oz', 'ounce', 'kg', 'kilogram', 'gram', 'g', 'pound', 'lb', 'lbm', 'pint', 'pt', 'p', 'quart', 'inch', 'in', 'cm', 'foot', 'feet', 'ft', 'ml', 'liter', 'litre', 'l', 'bottle', 'cup', 'slice', 'bowl', 'jug', 'order of', 'order', 'on the side', 'side of', 'side']
    print complete
    entity_collection.remove({"surface_text" : {"$in":final}})
    new_c.remove(
    {"question": final
    })
updateDatabase()
