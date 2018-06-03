# -*- coding: utf-8 -*-

import time
import datetime
import http.client
import urllib
import json

from utils.NetworkingUtils import NetworkingUtils
from persistence.DBController import DBManager

'''
    Make requests to scrap data from Github
'''
class GithubController():

    def __init__(self):
        self.netUtils = NetworkingUtils()
        self.dbManager = DBManager()

    '''
        Returns true if the IP of this service has expired the number of requests per hour on the Github API
    '''
    def hasExpiredRequestsPerHourGithub(self):
        response = {
            "success" : False,
            "msg" : "Failed to make a request to the Github API to determine if the number of requests per hour has been exceeded",
            "has_expired_limit_requests_per_hour" : "",
            "usage" : ""
        }

        try:
            # Create a connection with the Github API
            connection = http.client.HTTPSConnection(self.netUtils.GITHUB_API_ROOT_URL)

            # Make a request to the Github API and verify if the limit of requests per hour has been exceeded
            print("Making request to the Github API to determine if limit of requests per hour has been exceeded  ...")

            connection.request("GET", "/rate_limit", headers={
                "cache-control": "no-cache",
                "User-Agent": "Linkehub-API",
                "Accept": "application/vnd.github.v3+json"
            })

            res = connection.getresponse()
            data = res.read()
            githubApiResponse = json.loads(data.decode(self.netUtils.UTF8_DECODER))

            if githubApiResponse is not None:
                    
                if "rate" in githubApiResponse:
                    usageRate = githubApiResponse["rate"]

                    response["success"] = True
                    response["msg"] = "We got a response from the Github API"
                    response["usage"] = usageRate

                    if "remaining" in usageRate:
                        response["has_expired_limit_requests_per_hour"] = usageRate["remaining"] is 0

        except Exception as err:
            print("Failed to verify if hasExpiredRequestsPerHourGithub {0}".format(err))

        return json.dumps(response)

    '''
       Returns a list of Github users from a given location.
    '''
    def getGithubUsersFromLocation(self, token, storeInDb, location, pageNumber):
        response = {
            "success" : False,
            "msg" : "Failed to get the list of Github users from the given location",
            "total_count" : -1,
            "stored_in_db" : False,
            "users" : []
        }

        try:

            if not token or not location or not pageNumber:
                response["msg"] = "{0}. {1}".format(response["msg"], "Invalid input parameters")
            else:
                # Create a connection with the Github API
                connection = http.client.HTTPSConnection(self.netUtils.GITHUB_API_ROOT_URL)

                # Make a request to get the list of users from a location
                print("Making request to the get the list of Github users from a location ...")

                connection.request("GET", "/search/users?q=location:{0}&page={1}".format(location, pageNumber), headers={
	                "cache-control": "no-cache",
	                "User-Agent": "Linkehub-API",
	                "Accept": "application/vnd.github.v3+json"
	            })

                res = connection.getresponse()
                data = res.read()
                githubApiResponse = json.loads(data.decode(self.netUtils.UTF8_DECODER))

                if githubApiResponse is not None:

                    if "items" in githubApiResponse and "total_count" in githubApiResponse:
                        listUsers = githubApiResponse["items"]

                        response["total_count"] = githubApiResponse["total_count"]
                        response["success"] = True
                        response["msg"] = "We got a list of users from {0} ".format(location)
                        response["users"] = listUsers

                        # Store the list of users in the database
                        if storeInDb:

                            for user in listUsers:
                                self.dbManager.storeBasicUserInfoFromGithub(token, user)
                            
                            response["stored_in_db"] = True

        except Exception as err:
            print("Failed to getGithubUsersFromLocation {0}".format(err))

        return json.dumps(response)

    '''
        Scrap the profile info of a Github user
    '''
    def scrapBasicUserInfoFromGithub(self, token, userId):
        response = {
            "success" : False,
            "msg" : "Failed to get profile info of the given Github user",
            "basic_github_user_info" : None,
            "github_user_repos" : None
        }

        try:

            if not userId:
                response["msg"] = "Invalid userId"
            else:
                # Create a connection with the Github API
                connection = http.client.HTTPSConnection(self.netUtils.GITHUB_API_ROOT_URL)

                # GET the basic profile info of a user
                print("Requesting basic user info ...")

                connection.request("GET", "/search/users?q={0}".format(userId), headers={
                    "cache-control": "no-cache",
                    "User-Agent": "Linkehub-API",
                    "Accept": "application/vnd.github.v3+json"
                })

                res = connection.getresponse()
                data = res.read()
                basicUserInfo = json.loads(data.decode(self.netUtils.UTF8_DECODER))

                if basicUserInfo is not None:

                    if "items" in basicUserInfo:
                        basicUserInfo = basicUserInfo["items"][0]

                        response["msg"] = "We got some basic info about the user from Github. "
                        response["success"] = True
                        response["basic_github_user_info"] = basicUserInfo

                        # Store the basic Github user profile into the database
                        self.dbManager.storeBasicUserInfoFromGithub(token, basicUserInfo)

                # GET the list of repositories of the user
                print("Requesting list of repositories ...")

                connection.request("GET", "/users/{0}/repos".format(userId), headers={
                    "cache-control": "no-cache",
                    "User-Agent": "Linkehub-API",
                    "Accept": "application/vnd.github.v3+json"
                })

                res = connection.getresponse()
                data = res.read()
                userRepos = json.loads(data.decode(self.netUtils.UTF8_DECODER))

                if userRepos is not None:
                    
                    for repo in userRepos:

                        # Clean the repo
                        if "owner" in repo:
                            del repo["owner"]

                        # GET the list of languages of a repo
                        print("Requesting list of languages of a repository ...")
                        
                        if "languages_url" in repo:
                            connection.request("GET", repo["languages_url"], headers={
                                "cache-control": "no-cache",
                                "User-Agent": "Linkehub-API"
                            })

                            res = connection.getresponse()
                            data = res.read()
                            repoLanguages = json.loads(data.decode(self.netUtils.UTF8_DECODER))

                            if repoLanguages is not None:
                                repo["languages"] = repoLanguages

                    # Fetch a success message
                    response["msg"] = response["msg"] + " We also got the list of repositories. "
                    response["success"] = True
                    response["github_user_repos"] = userRepos

                    # Store the list of repositories of the user into the database
                    self.dbManager.storeReposGithubUser(token, userId, userRepos)

        except Exception as err:
            print("Failed to scrapBasicUserInfoFromGithub {0}".format(err))

        return json.dumps(response)


    '''
        Scrap the commits of a Github user made on a given language on a given repository
    '''
    def scrapUserCommitsRepoLanguageFromGithub(self, token, userId, repo, language):
        response = {
            "success" : False,
            "msg" : "Failed to get the commits and code samples of this Github user",
            "github_user_commits" : "",
            "code_samples" : []
        }

        try:

            if not userId or not repo or not language:
                response["msg"] = "Invalid userId"
            else:
                print("Requesting list of commits on a specific language in the given repository ...")

                # Create a connection with the Github API
                connection = http.client.HTTPSConnection(self.netUtils.GITHUB_API_ROOT_URL)

                # GET user commits x repo x language
                url = "/search/code?q=language:{0}+repo:{1}/{2}".format(language, userId, repo)

                connection.request("GET", url, headers={
                    "cache-control": "no-cache",
                    "User-Agent": "Linkehub-API",
                    "Accept": "application/vnd.github.v3+json"
                })

                res = connection.getresponse()
                data = res.read()
                commitsPerLanguage = json.loads(data.decode(self.netUtils.UTF8_DECODER))

                # Fetch the results that are going to be stored in the database
                if commitsPerLanguage is not None:
                    
                    if "items" in commitsPerLanguage:

                        for commit in commitsPerLanguage["items"]:

                            # Clean the list of commits
                            if "repository" in commit:
                                del commit["repository"]

                            # Create a link to the actual file in which the user commited
                            userCodeUrl = commit["html_url"]
                            userCodeUrl = userCodeUrl.replace("api.github.com", "github.com")
                            userCodeUrl = userCodeUrl.replace("blob", "raw")

                            response["code_samples"].append({
                                "commit_sha" : commit["sha"],
                                "language"   : language,
                                "code_url"   : userCodeUrl
                            })

                        # Fetch a success message
                        response["msg"] = "We got a few commits made by the user in {0} ".format(language)
                        response["success"] = True
                        response["github_user_commits"] = commitsPerLanguage

                        # Stores the user commits and code samples from Github on the database
                        self.dbManager.storeUserCommitsLanguageOnGithubRepo(token, userId, response["github_user_commits"], response["code_samples"])

        except Exception as err:
            print("Failed to scrapUserCommitsRepoLanguageFromGithub {0}".format(err))

        return json.dumps(response)
