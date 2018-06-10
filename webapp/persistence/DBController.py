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
                    db.child("github_profiles").child(githubProfile["login"]).update(githubProfile, token)
                    
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
        Store objects that represent the frequency distribuition of a few indicators of the user skills
    '''
    def storeIndicatorsGithubUserSkills(self, token, userId, sumReposPerSkill, sumStarPerSkill, sumWatchersPerSkill, sumForksPerSkill, strongRepo, strongSkill):
        status = False

        try:

            if token and userId and sumReposPerSkill and sumStarPerSkill and sumWatchersPerSkill and sumForksPerSkill and strongRepo and strongSkill:
                db = self.firebase.database()
                db.child("github_profiles").child(userId).child("sum_repos_x_skill").set(sumReposPerSkill, token)
                db.child("github_profiles").child(userId).child("sum_stars_x_skill").set(sumStarPerSkill, token)
                db.child("github_profiles").child(userId).child("sum_watchers_x_skill").set(sumWatchersPerSkill, token)
                db.child("github_profiles").child(userId).child("sum_forks_per_skill").set(sumForksPerSkill, token)
                db.child("github_profiles").child(userId).child("strongest_repo").set(strongRepo, token)
                db.child("github_profiles").child(userId).child("strongest_skill").set(strongSkill, token)

                status = True

        except Exception as e:
            print("Failed to storeIndicatorsGithubUserSkills: {0}".format(e))

        return status

    '''
        Upsert the list of skills of a user and add an analysis about their strenghts
    '''
    def storeAnalysisUserSkills(self, token, userId, skills):
        status = False

        try:

            if token and userId and skills:
                db = self.firebase.database()
                db.child("github_profile_skills_location").child(userId).set(skills, token)

                status = True

        except Exception as e:
            print("Failed to storeAnalysisUserSkills: {0}".format(e))

        return status

    '''
        Store the list of commits of a Github user for a specific language on a specific repository
    '''
    def storeUserCommitsLanguageOnGithubRepo(self, token, userId, commitsPerLanguage, codeSamples):
        status = False

        try:

            if commitsPerLanguage:
                dbCommits = self.firebase.database()
                dbCommits.child("github_profiles").child(userId).child("commits").update(commitsPerLanguage, token)

                status = True

            if codeSamples:
                dbCodeSamples = self.firebase.database()
                dbCodeSamples.child("github_profiles").child(userId).child("code_samples").update(codeSamples, token)

        except Exception as e:
            print("Failed to storeUserCommitsLanguageOnGithubRepo: {0}".format(e))

        return status

    '''
       Return a list of Github user ids that were associated to a given location on the moment of the storage
    '''
    def getListGithubUserIdsFromLocation(self, location):
        userIds = []

        try:

            if location:
                db = self.firebase.database()
                baseUrlGithubProfiles = db.child("github_profiles")
                profiles = baseUrlGithubProfiles.order_by_child('location').equal_to(location).get()

                for profile in profiles.each():
                    dbObject = profile.val()

                    if dbObject is not None:
                        userIds.append(dbObject['login'])

        except  Exception as e:
            print("Failed to getListGithubUserIdsFromLocation: {0}".format(e))

        return userIds

    '''
       Return a Github user by its id
    '''
    def getGithubUser(self, userId):
        user = {}

        try:

            if userId:
                db = self.firebase.database()
                userFromDb = db.child("github_profiles/{0}".format(userId)).get()

                if userFromDb:
                    user = userFromDb.val()

        except  Exception as e:
            print("Failed to getGithubUser: {0}".format(e))

        return user
