# -*- coding: utf-8 -*-

import time
import datetime
import http.client
import urllib
import json

from bs4 import BeautifulSoup

from utils.NetworkingUtils import NetworkingUtils

'''
    Make requests to scrap data from Github
'''
class GithubController():

    def __init__(self):
        self.netUtils = NetworkingUtils()

    # TODO: Refactor this method
    def scrapUserInfoFromGithub(self, userId, language):
        response = {
            "success" : False,
            "msg" : "Failed to get information about this Github user",
            "basic_github_user_info" : None,
            "github_user_repos" : None,
            "github_user_commits" : None
        }

        try:
            if not userId:
                response["msg"] = "Invalid userId"
            else:
                # Desired information
                basicUserInfo = None
                userRepos = None

                # Create a connection with the Github API
                connection = http.client.HTTPSConnection(self.netUtils.GITHUB_API_ROOT_URL)

                # GET basic info about the user
                print("Requesting basic user info ...")

                time.sleep(2)
                connection.request("GET", "/search/users?q={0}".format(userId), headers={
                    "cache-control": "no-cache",
                    "User-Agent": "Linkehub-API"
                })

                res = connection.getresponse()
                data = res.read()
                basicUserInfo = json.loads(data.decode(self.netUtils.UTF8_DECODER))

                if basicUserInfo is not None:
                    response["msg"] = "We got some basic info about the user from Github. "
                    response["success"] = True
                    response["basic_github_user_info"] = basicUserInfo

                # GET the list of repositories of the user
                print("Requesting list of repositories ...")

                time.sleep(2)
                connection.request("GET", "/users/{0}/repos".format(userId), headers={
                    "cache-control": "no-cache",
                    "User-Agent": "Linkehub-API"
                })

                res = connection.getresponse()
                data = res.read()
                userRepos = json.loads(data.decode(self.netUtils.UTF8_DECODER))

                if userRepos is not None:
                    response["msg"] = response["msg"] + " We also got the list of repositories. "
                    response["success"] = True
                    response["github_user_repos"] = userRepos

                    for repo in userRepos:
                        fullName = repo["full_name"]
                        
                        # GET user commits x repo x language
                        print("Requesting list of commits on a specific language in each repository ...")

                        time.sleep(5)
                        connection.request("GET", "/search/code?q=language:{0}+repo:{1}".format(language, fullName), headers={
                            "cache-control": "no-cache",
                            "User-Agent": "Linkehub-API"
                        })

                        res = connection.getresponse()
                        data = res.read()
                        commitsPerLanguage = json.loads(data.decode(self.netUtils.UTF8_DECODER))

                        if commitsPerLanguage is not None:
                            response["msg"] = response["msg"] + " We also got commits made by the user in {0} ".format(language)
                            response["success"] = True
                            response["github_user_commits"] = commitsPerLanguage
                            response["code_samples"] = []

                            if commitsPerLanguage["items"] is not None:

                                for commit in commitsPerLanguage["items"]:
                                    userCodeUrl = commit["html_url"]
                                    userCodeUrl = userCodeUrl.replace("github.com", "api.github.com")
                                    userCodeUrl = userCodeUrl.replace("blob", "raw")

                                    response["code_samples"].append({
                                        "language" : language,
                                        "code_url" : []
                                    })

        except Exception as err:
            print("Failed to scrapUserInfoFromGithub {0}".format(err))

        return json.dumps(response)
    #./TODO