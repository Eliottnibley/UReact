import json
import datetime
import numpy as np
from scipy import signal
from flask import Flask, jsonify, request, Response
from mysql import connector
from waitress import serve
from collections import OrderedDict
# pip install numpy
# pip install scipy
# pip install flask
# pip install mysql-connector-python
# pip install waitress
# pip install aws-secretsmanager-caching
# pip install boto3

# needed to set up a secret key for my user
# needed to run aws configure
import botocore 
import botocore.session 
from aws_secretsmanager_caching import SecretCache, SecretCacheConfig 

client = botocore.session.get_session().create_client('secretsmanager')
cache_config = SecretCacheConfig()
cache = SecretCache( config = cache_config, client = client)
secret = cache.get_secret_string('prod/kines')
CONFID = json.loads(secret)
# database connection
mydb = connector.connect(
host=CONFID['host'],
user=CONFID['username'],
password=CONFID['password']
)

app = Flask(__name__)
app.json.sort_keys = False

print("Server has started: ")

#json_file = {"TTS": 0}
#@app.route('/postData', methods=['POST'])
#def receive_post_data():
#    if request.method == 'POST':
#        data_from_post = request.json.get('counter')
#        json_file['counter'] = data_from_post
#        return jsonify(json_file)

# --------------------------------------------------------------- PATIENT ---------------------------------------------------------------

@app.route('/mysql/getAllPatients', methods=['GET'])
def getAllPatients():
    if request.method == 'GET':
        mycursor = mydb.cursor()
        mycursor.execute("USE Kinesiology_App") 
        mycursor.execute("SELECT * FROM Patient")
        myresult = mycursor.fetchall()
        # This is one element of the return json, may have multiple
        #{"pID": 1, "firstName": "John", "lastName": "Doe"}
        returnList = []
        for x in myresult:
            returnList.append(OrderedDict({"pID": x[0], "firstName": x[1], "lastName": x[2]}))
        return jsonify(returnList) 

@app.route('/mysql/getOnePatient', methods=['GET'])
def getOnePatient():
    # ?ID=1 need to add a value to key1 that is the patient pID in the url
    if request.method == 'GET':
        data = request.args.get('ID')
        mycursor = mydb.cursor()
        mycursor.execute("USE Kinesiology_App") 
        # ctrl-shift U
        sql = "SELECT * FROM Patient WHERE pID=%s"
        val = [(data)]
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()
        # This is one element of the return json, may have multiple
        #{"pID": 1, "firstName": "John", "lastName": "Doe", "dOB": "1998-04-18", "height": 70, "weight": 215,
        # "sport": "football", "gender": "M", "thirdPartyID": "62936", 
        # "patients": [{"iID": 1, "iName": "Concussion", "iDate": "2023-09-20"}, ... ]}
        returnList = []

        # Get the patient we are looking for
        patient = OrderedDict()
        for x in myresult:
            patient = OrderedDict({"pID": x[0], "firstName": x[1], "lastName": x[2], "dOB": x[3], "height": x[4], "weight": x[5], 
                "sport": x[6], "gender": x[7], "thirdPartyID": x[8], "incidents": []})
        
        # Get the Incidents that that patient has
        sql = "SELECT * FROM Incident WHERE pID=%s"
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()
        for x in myresult:
            patient['incidents'].append(OrderedDict({"iID": x[0], "iName": x[1], "iDate": x[2]}))
        
        returnList.append(patient)
        return jsonify(returnList) 

# RIGHT NOW, YOU MUST INPUT ALL VALUES, talk to kines about if they want this, or deal with it on front end
@app.route('/mysql/createNewPatient', methods=['POST'])
def createNewPatient():
    if request.method == 'POST':
        data = request.json
        mycursor = mydb.cursor()
        mycursor.execute("use Kinesiology_App") 
        sql = "INSERT INTO Patient (pFirstName, pLastName, dOB, height, weight, sport, gender, thirdPartyID) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"
        val = (data['firstName'], data['lastName'], data['dOB'], data['height'], data['weight'], data['sport'], data['gender'], data['thirdPartyID'])
        #datetime.date(1970,6,17)
        mycursor.execute(sql, val)
        mydb.commit()
        pID = mycursor.lastrowid
        returnPatient = {"pID": pID, "firstName": data['firstName'], "lastName": data['lastName'], "dOB": data['dOB'], "height": data['height'], 
            "weight": data['weight'], "sport": data['sport'], "gender": data['gender'], "thirdPartyID": data['thirdPartyID']}
        return jsonify(returnPatient)

@app.route('/mysql/updatePatient', methods=['PUT'])
def updatePatient():
    if request.method == 'PUT':
        data = request.json
        sql = "UPDATE Patient SET " + updatePatientHelper(data)
        print(sql)
        mycursor = mydb.cursor()
        mycursor.execute("use Kinesiology_App") 
        mycursor.execute(sql)
        mydb.commit()

        pID = [(data['pID'])]
        sql = "SELECT * FROM Patient WHERE pID=%s"
        mycursor.execute(sql, pID)
        myresult = mycursor.fetchall()
        returnList = {}
        # Get the patient we are looking for
        for x in myresult:
            returnList = {"pID": x[0], "firstName": x[1], "lastName": x[2], "dOB": x[3], "height": x[4], "weight": x[5], 
                "sport": x[6], "gender": x[7], "thirdPartyID": x[8]}
        return jsonify(returnList)

def updatePatientHelper(data):
    sql = ""
    firstBool=lastBool=dBool=hBool=wBool=sBool=gBool = False
    if 'firstName' in data:
        firstBool = True
        sql += "pFirstName='" + data['firstName'] + "'"
    if 'lastName' in data:
        if firstBool == True:
            sql += ", "
        lastBool = True
        sql += "pLastName='" + data['lastName'] + "'"
    if 'dOB' in data:
        if (firstBool or lastBool) == True:
            sql += ", "
        dBool = True
        sql += "dOB='" + str(data['dOB']) + "'"
    if 'height' in data:
        if (firstBool or lastBool or dBool) == True:
            sql += ", "
        hBool = True
        sql += "height=" + str(data['height'])
    if 'weight' in data:
        if (firstBool or lastBool or dBool or hBool) == True:
            sql += ", "
        wBool = True
        sql += "weight=" + str(data['weight'])
    if 'sport' in data:
        if (firstBool or lastBool or dBool or hBool or wBool) == True:
            sql += ", "
        sBool = True
        sql += "sport='" + data['sport']  + "'"
    if 'gender' in data:
        if (firstBool or lastBool or dBool or hBool or wBool or sBool) == True:
            sql += ", "
        gBool = True
        sql += "gender='" + data['gender'] + "'"
    if 'thirdPartyID' in data:
        if (firstBool or lastBool or dBool or hBool or wBool or sBool or gBool) == True:
            sql += ", "
        sql += "thirdPartyID='" + data['thirdPartyID'] + "'"

    sql += " WHERE pID=" + str(data['pID'])
    return sql


@app.route('/mysql/deletePatient', methods=['DELETE'])
def deletePatient():
    if request.method == 'DELETE':
        data = request.json
        mycursor = mydb.cursor()
        mycursor.execute("use Kinesiology_App") 
        sql = "Delete from Patient where pID = %s"
        val = [(data["pID"])]
        mycursor.execute(sql, val) 
        mydb.commit()
        sql = "SELECT * FROM Patient WHERE pID=%s"
        mycursor.execute(sql,val)
        patientExist = mycursor.fetchall()
        if len(patientExist) == 0:
            return jsonify({"Status": True})
        else:
            # make sure you pass in a valid pID
            return jsonify({"Status": False})


# --------------------------------------------------------------- INCIDENT --------------------------------------------------------------
@app.route('/mysql/getIncident', methods=['GET'])
def getIncident():
    #{"iID": 1, "iName": "Concussion", "iDate": "2023-09-20", "iNotes": "this person suffered a head injury", "tests": [{"tID": 1, "tDate": "2023-09-20", "tName": "Day of"}, ... ]}
    if request.method == 'GET':
        data = request.args.get('ID')
        mycursor = mydb.cursor()
        mycursor.execute("USE Kinesiology_App") 
        # ctrl-shift U
        sql = "SELECT * FROM Incident WHERE iID=%s"
        val = [(data)]
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()

        returnList = []
        # Get the Incident we are looking for
        incident = OrderedDict()
        for x in myresult:
            incident = OrderedDict({"iID": x[0], "iName": x[1], "iDate": x[2], "iNotes": x[3], "tests": []})

        # Get the Tests that that patient has
        sql = "SELECT * FROM Test WHERE iID=%s"
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()
        for x in myresult:
            incident['tests'].append(OrderedDict({"tID": x[0], "tDate": x[2], "tName": x[1]}))

        returnList.append(incident)
        return jsonify(returnList)

# RIGHT NOW, YOU MUST INPUT ALL VALUES, talk to kines about if they want this, or deal with it on front end
@app.route('/mysql/createIncident', methods=['POST'])
def createIncident():
    #'{"iID": 1, "iName": "Concussion", "iDate": "2023-09-20", "iNotes": "this person suffered a head injury", "pID": 1}'
    if request.method == 'POST':
        data = request.json
        mycursor = mydb.cursor()
        mycursor.execute("use Kinesiology_App") 
        sql = "INSERT INTO Incident (iName, iDate, iNotes, pID) VALUES(%s, %s, %s, %s)"
        val = (data['iName'], data['iDate'], data['iNotes'], data['pID'])
        mycursor.execute(sql, val)
        mydb.commit()
        iID = mycursor.lastrowid
        returnIncident = {"iID": iID, "iName": data['iName'], "iDate": data['iDate'], "iNotes": data['iNotes'], "pID": data['pID']}
        return jsonify(returnIncident)

@app.route('/mysql/updateIncident', methods=['PUT'])
def updateIncident():
    #'{"iID": 1, "iName": "Concussion", "iDate": "2023-09-20", "iNotes": "this person suffered a head injury", "pID": 1}'
    if request.method == 'PUT':
        data = request.json
        sql = "UPDATE Incident SET " + updateIncidentHelper(data)
        print(sql)
        mycursor = mydb.cursor()
        mycursor.execute("use Kinesiology_App") 
        mycursor.execute(sql)
        mydb.commit()

        iID = [(data['iID'])]
        sql = "SELECT * FROM Incident WHERE iID=%s"
        mycursor.execute(sql, iID)
        myresult = mycursor.fetchall()
        returnList = {}
        # Get the patient we are looking for
        for x in myresult:
            returnList = {"iID": x[0], "iName": x[1], "iDate": x[2], "iNotes": x[3], "pID": x[4]}
        return jsonify(returnList)

def updateIncidentHelper(data):
    # "iName": "Concussion", "iDate": "2023-09-20", "iNotes": "this person suffered a head injury"
    sql = ""
    nameBool=dateBool = False
    if 'iName' in data:
        nameBool = True
        sql += "iName='" + data['iName'] + "'"
    if 'iDate' in data:
        if nameBool == True:
            sql += ", "
        dateBool = True
        sql += "iDate='" + data['iDate'] + "'"
    if 'iNotes' in data:
        if (nameBool or dateBool) == True:
            sql += ", "
        dBool = True
        sql += "iNotes='" + str(data['iNotes']) + "'"

    sql += " WHERE iID=" + str(data['iID'])
    return sql

@app.route('/mysql/deleteIncident', methods=['DELETE'])
def deleteIncident():
    if request.method == 'DELETE':
        data = request.json
        mycursor = mydb.cursor()
        mycursor.execute("use Kinesiology_App") 
        sql = "Delete from Incident where iID = %s"
        val = [(data["iID"])]
        mycursor.execute(sql, val) 
        mydb.commit()
        sql = "SELECT * FROM Incident WHERE iID=%s"
        mycursor.execute(sql,val)
        patientExist = mycursor.fetchall()
        if len(patientExist) == 0:
            return jsonify({"Status": True})
        else:
            # make sure you pass in a valid iID
            return jsonify({"Status": False})


# --------------------------------------------------------------- TEST ------------------------------------------------------------------

@app.route('/mysql/getTest', methods=['GET'])
def getTest():
    #{"tID": 1, "tName": "Day of", "tDate": "2023-09-20", "tNotes": "this is some notes about the test", "baseline": 0, "iID": 1, "dynamic": {}, "static": {}, "reactive": {"rID": 1, "fTime": 1.234, "bTime": 0.873, "lTime": 0.876, "rTime": 0.945, "mTime": 0.912, "tID": 1}}
    if request.method == 'GET':
        data = request.args.get('ID')
        mycursor = mydb.cursor()
        mycursor.execute("USE Kinesiology_App") 
        # ctrl-shift U
        sql = "SELECT * FROM Test WHERE tID=%s"
        val = [(data)]
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()

        returnList = []
        # Get the Incident we are looking for
        test = OrderedDict()
        for x in myresult:
            test = OrderedDict({"tID": x[0], "tName": x[1], "tDate": x[2], "tNotes": x[3], "baseline": x[4], "iID": x[5], "dynamic": {}, "static": {}, "reactive": {}})

        # Get the Tests that that patient has
        sql = "SELECT * FROM ReactiveTest WHERE tID=%s"
        # {"rID": 1, "fTime": 1.234, "bTime": 0.873, "lTime": 0.876, "rTime": 0.945, "mTime": 0.912, "tID": 1}
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()
        for x in myresult:
            test['reactive'] = {"rID": x[0], "fTime": x[1], "bTime": x[2], "lTime": x[3], "rTime": x[4], "mTime": x[5], "tID": x[6]}

        returnList.append(test)
        return jsonify(returnList)

# RIGHT NOW, YOU MUST INPUT ALL VALUES, talk to kines about if they want this, or deal with it on front end
@app.route('/mysql/createTest', methods=['POST'])
def createTest():
    #'{"tID": 1, "tName": "Day of", "tDate": "2023-09-20", "tNotes": "this is some notes about the test", "baseline": 0, "iID": 1, "dynamic": {}, "static": {}, "reactive": {}
    if request.method == 'POST':
        data = request.json
        mycursor = mydb.cursor()
        mycursor.execute("use Kinesiology_App") 
        sql = "INSERT INTO Test (tName, tDate, tNotes, baseline, iID) VALUES(%s, %s, %s, %s, %s)"
        val = (data['tName'], data['tDate'], data['tNotes'], data['baseline'], data['iID'])
        mycursor.execute(sql, val)
        mydb.commit()
        tID = mycursor.lastrowid
        returnTest = {"tName": tID, "tName": data['tName'], "tDate": data['tDate'], "tNotes": data['tNotes'], "baseline": data['baseline'], "iID": data['iID'], "dynamic": {}, "static": {}, "reactive": {}}
        return jsonify(returnTest)

@app.route('/mysql/createReactiveTest', methods=['POST'])
def createReactiveTest():
    #'{"rID": 1, "fTime": 1.234, "bTime": 0.873, "lTime": 0.876, "rTime": 0.945, "mTime": 0.912, "tID": 1}'
    if request.method == 'POST':
        data = request.json
        mycursor = mydb.cursor()
        mycursor.execute("use Kinesiology_App") 
        sql = "INSERT INTO ReactiveTest (fTime, bTime, lTime, rTime, mTime, tID) VALUES(%s, %s, %s, %s, %s, %s)"
        val = (data['fTime'], data['bTime'], data['lTime'], data['rTime'], data['mTime'], data['tID'])
        mycursor.execute(sql, val)
        mydb.commit()
        rID = mycursor.lastrowid
        returnRTest = {"rID": rID, "fTime": data['fTime'], "bTime": data['bTime'], "lTime": data['lTime'], "rTime": data['rTime'], "mTime": data['mTime'], "tID": data['tID']}
        return jsonify(returnRTest)

# --------------------------------------------------------------- TEST SCRIPTS ----------------------------------------------------------

@app.route('/timeToStability', methods=['POST'])
def timeToStability():
    dataAcc = request.json.get('dataAcc')
    dataRot = request.json.get('dataRot')
    fs = request.json.get('fs')

    accNorm = np.linalg.norm(dataAcc, axis=0)
    rotNorm = np.linalg.norm(dataRot, axis=0)

    b, a = signal.butter(2, 10 / (fs / 2))

    #Foot Movement: 9.81*1.07; % based on El-Gohary Threshold for foot movement
    qaF = signal.filtfilt(b, a, accNorm) < 9.81*1.07
    #Rotational Foot Movement: 14/180*pi; % based on El-Gohary Threshold for foot movement* this should be 7 deg/sec?
    qrf = signal.filtfilt(b, a, rotNorm) < 14/180*np.pi
    qf = np.logical_and(qaF, qrf)

    #find t0
    peaks, _ = signal.find_peaks(np.flip(accNorm[fs * 3:]), height=14.6)

    movementF = peaks[-1]
    flipQf = qf[::-1]

    # find the index of release point
    release = 0
    for i, j in enumerate(flipQf[movementF:]):
        if (j == 1):
            release = i
            break

    # adding 2 accounts for index differences between matlab and python
    release = movementF+release + 2
    t0 = len(accNorm)-release

    #find TTS with adjustment for indexing differences
    movementReg = len(accNorm) - (movementF + 2)

    # find the index of release point
    EndTTS = 0
    for i, j in enumerate(qf[movementReg:]):
        if (j == 1):
            EndTTS = i
            break

    EndTTS = EndTTS+movementReg + 2

    TTS = (EndTTS - t0)/fs

    return jsonify(t0 = int(t0), EndTTS = int(EndTTS), TTS = TTS)


# --------------------------------------------------------------- SERVER ----------------------------------------------------------------

# Run the developement server
# if __name__ == '__main__':
#     app.run()

# This is to run as a WSGI server, which essentially means
# no default logging or hot reload. comment out the  development server code
# above then uncomment the code below.
# You will need to install waitress with this command
# python -m pip install waitress

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)

