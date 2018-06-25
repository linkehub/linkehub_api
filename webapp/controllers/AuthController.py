# -*- coding: utf-8 -*-

import os
import json
import http.client
import urllib

from utils.Logger import Logger
from persistence.DBController import DBManager

'''
    Authenticate users on Firebase
'''
class AuthController():

    def __init__(self):
        self.logger = Logger()
        self.dbManager = DBManager()

    '''
        Return an access token if the user sucessfully logs into their account
    '''
    def loginWithUsernamePassword(self, username, password):
        response = {
            "success" : False,
            "msg" : "Failed to login with the given credentials",
            "access_token" : ""
        }

        try:

            if not username or not password:
                response["msg"] = "Invalid username or password"
            else:
                token = self.dbManager.login(username, password)

                if token:
                    response["msg"] = "Success. This is your access token: to not share it with anyone!"
                    response["access_token"] = token
                    response["created_at"] = self.logger.get_utc_iso_timestamp()

        except Exception as err:
            print("Failed to loginWithUsernamePassword {0}".format(err))

        return json.dumps(response)

    '''
        Verify if an access token is still valid
    '''
    def isValidToken(self, token):
        isValid = False

        try:
            
            if token:
                auth = self.dbManager.firebase.auth()
                user = auth.sign_in_with_custom_token(token)

                if user is not None:

                    if "idToken" in user:
                        isValid = True

        except Exception as e:
            print("{0} Failed to verify isValidToken {1}".format(self.TAG, e))

        return isValid
