import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import csv
import json
import requests 
from collections import *
import math
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np

class carCrashTimes(dml.Algorithm):
    contributor = 'cfortuna_houset_karamy_snjan19'
    reads = ['cfortuna_houset_karamy_snjan19.CarCrashData']
    writes = ['cfortuna_houset_karamy_snjan19.CrashTimes']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('cfortuna_houset_karamy_snjan19', 'cfortuna_houset_karamy_snjan19')

        # Trial Mode is basically limiting data points on which to run execution if trial parameter set to true
        repoData = repo['cfortuna_houset_karamy_snjan19.CarCrashData'].find().limit(0) if trial else repo['cfortuna_houset_karamy_snjan19.CarCrashData'].find()

        # Categorize the times into the hour that the crash has occured
        times = []
        for element in repoData:
            time_string = element["Crash Time"]
            time_split = time_string.split(" ")

            if time_split[1] == "PM" and int(time_split[0].split(":")[0]) != 12:
                time_digit = int(time_split[0].split(":")[0]) + 12
            else:
                time_digit = int(time_split[0].split(":")[0])
            
            times.append(time_digit)
            print(time_string)

        # Count the amount of car crashes that appear in the hour ranges
        count = Counter(times)
        x = []
        y = []
        for key, value in count.items():
            x.append(key)
            y.append(value)

        # Calculate the linear regression on the data set
        meanX = sum(x) * 1.0 / len(x)
        meanY = sum(y) * 1.0 / len(y)

        varX = sum([(v - meanX)**2 for v in x])
        varY = sum([(v - meanY)**2 for v in y])

        minYHatCov = sum([(x[i] - meanX) * (y[i] - meanY) for i in range(len(y))])

        slope = minYHatCov / varX
        intercept = meanY - slope * meanX

        MSE = sum([(y[i] - (slope * x[i] + intercept))**2 for i in range(len(x))]) * 1.0 / len(x)
        RMSE = math.sqrt(MSE)
        lineOfBestFit = "y = " + str(slope) + "x + " + str(intercept)

        # Place the results of the linear regression into Mongo
        result = {"line of best fit": lineOfBestFit, "slope": slope , "intercept": intercept, "mean square error": MSE, "root mean square error": RMSE}
    
        repo.dropCollection("CrashTimes")
        repo.createCollection("CrashTimes")

        repo['cfortuna_houset_karamy_snjan19.CrashTimes'].insert(result)

        repo.logout()
        endTime = datetime.datetime.now()

        return {"start":startTime, "end":endTime}

    """Provenance of this Document"""
    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        '''
            Create the provenance document describing everything happening
            in this script. Each run of the script will generate a new
            document describing that invocation event.
            '''

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('cfortuna_houset_karamy_snjan19', 'cfortuna_houset_karamy_snjan19')
        doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')
        doc.add_namespace('mag', 'https://data.mass.gov/resource/')

        this_script = doc.agent('alg:cfortuna_houset_karamy_snjan19#retrieveData', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        
        wazeResource = doc.entity('bdp:dih6-az4h', {'prov:label':'Waze Traffic Data', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        hospitalsResource = doc.entity('bdp:u6fv-m8v4', {'prov:label':'Boston Hospitals Data', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        streetResource = doc.entity('mag:ms23-5ubn', {'prov:label':'Boston Streets Data', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})

        getWazeTrafficData = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        getBostonHospitalsData = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        getBostonStreetsData = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(getWazeTrafficData, this_script)
        doc.wasAssociatedWith(getBostonHospitalsData, this_script)
        doc.wasAssociatedWith(getBostonStreetsData, this_script)
        
        doc.usage(getWazeTrafficData, wazeResource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  #'ont:Query':'?type=Neighborhood+Area+Boston'
                  }
                  )
        doc.usage(getBostonHospitalsData, hospitalsResource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  #'ont:Query':'?type=Neighborhood+Area+Cambridge'
                  }
                  )
        doc.usage(getBostonStreetsData, streetResource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  #'ont:Query':'?type=Neighborhood+Area+Cambridge'
                  }
                  )
        WazeTrafficData = doc.entity('dat:cfortuna_houset_karamy_snjan19#WazeTrafficData', {prov.model.PROV_LABEL:'Waze Traffic Data', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(WazeTrafficData, this_script)
        doc.wasGeneratedBy(WazeTrafficData, getWazeTrafficData, endTime)
        doc.wasDerivedFrom(WazeTrafficData, wazeResource, getWazeTrafficData, getWazeTrafficData, getWazeTrafficData)

        BostonHospitalsData = doc.entity('dat:cfortuna_houset_karamy_snjan19#BostonHospitalsData', {prov.model.PROV_LABEL:'Boston Hospitals Data', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(BostonHospitalsData, this_script)
        doc.wasGeneratedBy(BostonHospitalsData, getBostonHospitalsData, endTime)
        doc.wasDerivedFrom(BostonHospitalsData, hospitalsResource, getBostonHospitalsData, getBostonHospitalsData, getBostonHospitalsData)

        BostonStreetsData = doc.entity('dat:cfortuna_houset_karamy_snjan19#BostonStreetsData', {prov.model.PROV_LABEL:'Boston Streets Data', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(BostonStreetsData, this_script)
        doc.wasGeneratedBy(BostonStreetsData, getBostonStreetsData, endTime)
        doc.wasDerivedFrom(BostonStreetsData, streetResource, getBostonStreetsData, getBostonStreetsData, getBostonStreetsData)

        repo.logout()
                  
        return doc

carCrashTimes.execute()
# doc = retrieveData.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))

## eof
