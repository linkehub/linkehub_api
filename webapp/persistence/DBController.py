# -*- coding: utf-8 -*-

import os
import json
import pyrebase

from utils.NetworkingUtils import NetworkingUtils
from utils.Logger import Logger

'''
    Manages the connection and operations of this service with its database
'''
class DBManager():

    def __init__(self):

        try:
            self.netUtils = NetworkingUtils()
            self.logger = Logger()
            
            dirname = os.path.dirname(__file__)
            configFileName = os.path.join(dirname, '../config/linkehub-api-firebase.json')

            with open(configFileName) as json_data:
                self.firebase = pyrebase.initialize_app(json.load(json_data))
        
        except Exception as e:
            print("Failed to __init__: {0}".format(e))


    '''
        Returns a valid access token if the user logs in with a valid email and password
    '''
    def login(self, email, password):
        token = ""

        try:

            if email and password:
                auth = self.firebase.auth()
                user = auth.sign_in_with_email_and_password(email, password)
                token = user["idToken"]

        except Exception as e:
            print("Failed to login: {0}".format(e))

        return token

    '''
        Store the basic profile info of a Github user in the database
    '''
    def storeBasicUserInfoFromGithub(self, token, githubProfile):
        status = False

        try:

            if githubProfile:

                if githubProfile["login"]:
                    githubProfile["queried_at"] = self.logger.get_utc_iso_timestamp()

                    db = self.firebase.database()
                    db.child("github_profiles").child(githubProfile["login"]).child("profile").set(githubProfile, token)
                    
                    status = True

        except Exception as e:
            print("Failed to storeBasicUserInfoFromGithub: {0}".format(e))

        return status

    '''
        Store the list of repositories of a Github user
    '''
    def storeReposGithubUser(self, token, userId, repos):
        status = False

        try:

            if repos:
                db = self.firebase.database()
                db.child("github_profiles").child(userId).child("repos").set(repos, token)
                    
                status = True

        except Exception as e:
            print("Failed to storeReposGithubUser: {0}".format(e))

        return status

    '''
        Store the list of commits of a Github user for a specific language on a specific repository
    '''
    def storeUserCommitsLanguageOnGithubRepo(self, token, userId, commitsPerLanguage, codeSamples):
        status = False

        try:

            if commitsPerLanguage:
                dbCommits = self.firebase.database()
                dbCommits.child("github_profiles").child(userId).child("commits").set(commitsPerLanguage, token)

                status = True

            if codeSamples:
                dbCodeSamples = self.firebase.database()
                dbCodeSamples.child("github_profiles").child(userId).child("code_samples").set(codeSamples, token)

        except Exception as e:
            print("Failed to storeUserCommitsLanguageOnGithubRepo: {0}".format(e))

        return status

    '''
       Todo: >>>>> 
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
