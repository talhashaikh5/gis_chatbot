import pymongo

mongo_uri = "mongodb://admin:Zsd#fdc^fgT@10.8.46.185:27017,10.8.46.184:27017," \
            "10.8.46.183:27017/rasacentral?replicaSet=happy&authSource=admin"


def push_otp(phone_number, otp):
    myclient = pymongo.MongoClient(mongo_uri)
    mydb = myclient["rasacentral"]
    mycol = mydb["otp"]
    mydict = {"phone_number": phone_number, "otp": otp}
    x = mycol.insert_one(mydict)


def pull_otp(phone_number):
    myclient = pymongo.MongoClient(mongo_uri)
    mydb = myclient["rasacentral"]
    mycol = mydb["otp"]
    get = mycol.find({"phone_number": phone_number}, {"otp": 1})
    for x in get:
        return x["otp"]


if __name__ == '__main__':
    push_otp("9168810003", "00111")
    print(pull_otp("9168810003"))
