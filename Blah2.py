#!/usr/bin/env python
import time
# import mysql.connector
import mariadb


# db = mysql.connector.connect(
#  host="localhost",
#   host="192.168.0.19",
#  user="cubcaradmin",
#  passwd="cubsrock",
#  database="CubCar"
# )

db = mariadb.connect(
 #   host="localhost",
    host="192.168.100.18",
    user="cubcaradmin",
    passwd="cubsrock",
    database="CubCar"
)

cursor = db.cursor()
sql = "INSERT INTO racerinfo( RacerFirstName,RacerLastName) VALUES (%s, %s)"
val = ("Bear", "Wilts")
# cursor.execute(sql, val )
# db.commit()

DID = 2
sql = "SELECT RacerID, RacerFirstName, RacerLastName, RacerPack,RacerCarName, RacerCarClass from RacerInfo WHERE RacerFirstName= 'Bear'"
cursor.execute(sql)
result = cursor.fetchall()
# result = cursor.fetchone()

if cursor.rowcount >= 1:
    for row in result:
        print("Welcome " , str(row[0]) , row[1] , row[2] )
        print("\n")
else:
    print("User does not exist.")

mydb = db.cursor()


sql = "SELECT RacerID, RacerFirstName, RacerLastName, RacerPack,RacerCarName, RacerCarClass from RacerInfo"

mydb.execute(sql)
results = mydb.fetchall()

print("Total rows are:  ", len(results))
print("Printing each row")
for row in results:
    print("ID: ", str(row[0]) + " First Name: ", row[1] +" Last Name: ", row[2] + " Pack: ", row[3])
    print("\n")
