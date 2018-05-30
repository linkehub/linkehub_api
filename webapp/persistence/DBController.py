# -*- coding: utf-8 -*-

import os
import json
import pyrebase

from operator import attrgetter
from utils.NetworkingUtils import NetworkingUtils

'''
    Manages the connection and operations of this service with its database
'''
class DBManager():

    def __init__(self):
        self.netUtils = NetworkingUtils()
        
        dirname = os.path.dirname(__file__)
        configFileName = os.path.join(dirname, '../config/.json')

        with open(configFileName) as json_data:
            self.firebase = pyrebase.initialize_app(json.load(json_data))

    '''
        
    '''
    def storeLinkedinProfile(self, linkedinProfile):
        status = True

        try:

            if linkedinProfile:
                db = self.firebase.database()
                db.child("linkedin_profiles").set(linkedinProfile)

        except  Exception as e:
            print("Failed to storeLinkedinProfile: {0}".format(e))
            status = False

        return status

    '''
        
    '''
    def storeGithubProfile(self, githubProfile):
        status = True

        try:

            if githubProfile:
                db = self.firebase.database()
                db.child("github_profiles").set(githubProfile)

        except Exception as e:
            print("Failed to storeGithubProfile: {0}".format(e))
            status = False

        return status
