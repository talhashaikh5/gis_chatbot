import pymongo

mongo_uri = "mongodb://localhost:27017/rasacentral"


def push_otp(phone_number, otp):
    myclient = pymongo.MongoClient(mongo_uri)
    mydb = myclient["rasacentral"]
    mycol = mydb["otp"]
    # mydict = {"phone_number": phone_number, "otp": otp}
    myquery = {"phone_number": phone_number}
    newvalues = {"$set": {"otp": otp}}
    mycol.update_one(myquery, newvalues, upsert=True)


def pull_otp(phone_number):
    myclient = pymongo.MongoClient(mongo_uri)
    mydb = myclient["rasacentral"]
    mycol = mydb["otp"]
    get = mycol.find({"phone_number": phone_number}, {"otp": 1})
    for x in get:
        return x["otp"]


if __name__ == '__main__':
    push_otp("9168810003", "123456")
    # print(pull_otp("9168810003"))
