# -*- coding: utf-8 -*-

import time
import datetime
import http.client
import urllib
import json
import pandas as pd
import numpy as np

from utils.NetworkingUtils import NetworkingUtils
from utils.StringUtils import StringUtils
from utils.DataCleaningUtils import DataCleaningUtils
from persistence.DBController import DBManager

'''
    Make requests to scrap data from Github
'''
class GithubController():

    def __init__(self):
        self.netUtils = NetworkingUtils()
        self.dcUtils = DataCleaningUtils()
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
            # Make a request to the Github API and verify if the limit of requests per hour has been exceeded
            print("Making request to the Github API to determine if limit of requests per hour has been exceeded  ...")

            connection = http.client.HTTPSConnection(self.netUtils.GITHUB_API_ROOT_URL)
            connection.request("GET", "/rate_limit", headers=self.netUtils.AUTH_GITHUB_HEADER)

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
        Return and store the profile of a github user
    '''
    def scrapGithubUserProfile(self, token, userId):
        response = {
            "success" : False,
            "msg" : "Failed to collect the Github user profile",
            "user_profile" : ""
        }

        try:

            if not token or not userId:
                response["msg"] = "{0}. {1}".format(response["msg"], "Failed to validate the input parameters")
            else:
                # Make a request to the Github API to get the profile info of a user
                print("Making a request to the Github API to get the profile info of a user ...")

                connection = http.client.HTTPSConnection(self.netUtils.GITHUB_API_ROOT_URL)
                connection.request("GET", "/search/users?q={0}".format(userId), headers=self.netUtils.AUTH_GITHUB_HEADER)

                res = connection.getresponse()
                data = res.read()
                githubApiResponse = json.loads(data.decode(self.netUtils.UTF8_DECODER))

                if githubApiResponse is not None:
                        
                    if "items" in githubApiResponse:
                        listUsers = githubApiResponse["items"]

                        if listUsers[0] is not None:
                            profile = listUsers[0]
                            self.dbManager.storeBasicUserInfoFromGithub(token, profile)

                            response["success"] = True
                            response["msg"] = "We got a response from the Github API"
                            response["user_profile"] = profile

        except Exception as err:
            print("Failed to verify if scrapGithubUserProfile {0}".format(err))

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
                # Make a request to get the list of users from a location
                print("Making request to the get the list of Github users from a location ...")

                connection = http.client.HTTPSConnection(self.netUtils.GITHUB_API_ROOT_URL)
                endpoint = "/search/users?q=location:{0}&page={1}".format(
                    urllib.parse.quote(location),
                    urllib.parse.quote(pageNumber)
                )
                connection.request("GET", endpoint, headers=self.netUtils.AUTH_GITHUB_HEADER)

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
                            profileResponse = {}
                            profileResponse["success"] = False

                            for user in listUsers:
                                user["location"] = location

                                # Store the basic user profile into the database
                                if "login" in user:
                                    self.dbManager.storeBasicUserInfoFromGithub(token, user)

                            if profileResponse["success"]:
                                response["success"] = True
                                response["msg"] = "Stored user profile"
                                response["stored_in_db"] = True
                                response["users"] = listUsers

        except Exception as err:
            print("Failed to getGithubUsersFromLocation {0}".format(err))

        return json.dumps(response)

    '''
        Scrap the repositories, personal info and make a simple descriptive analysis of the skills of a 
        Github user.
    '''
    def scrapUserRepositoriesSkillsFromGithub(self, token, userId, location):
        response = {
            "success" : False,
            "msg" : "Failed to scrap info about the user repositories",
            "github_user_repos" : "",
            "sum_repos_x_skill" : "",
            "sum_star_x_skill" : "",
            "sum_watchers_x_skill" : "",
            "sum_forks_x_skill" : "",
            "strongest_repo" : "",
            "strongest_language" : ""
        }

        try:

            if not token or not userId:
                response["msg"] = "Invalid userId"
            else:
                # GET the list of repositories of the user
                print("Requesting list of repositories and skills ...")

                connection = http.client.HTTPSConnection(self.netUtils.GITHUB_API_ROOT_URL)
                endpoint = "/users/{0}/repos".format(
                    urllib.parse.quote(userId)
                )
                connection.request("GET", endpoint, headers=self.netUtils.AUTH_GITHUB_HEADER)
                res = connection.getresponse()
                data = res.read()

                if data is not None:
                    jsonData = data.decode(self.netUtils.UTF8_DECODER)

                    if jsonData is not None:
                        response["success"] = True

                        if jsonData == "[]":
                            response["msg"] = "The user doesn't have repositories"
                        else:
                            # If the user has repositories
                            # Pre-process the data within the response and extract some simple descriptive 
                            # statistics about the user skills
                            df = pd.read_json(jsonData)
                            toDrop = self.dcUtils.getColumnsToDrop(df,
                                [
                                    'archive_url',
                                    'assignees_url',
                                    'blobs_url',
                                    'branches_url',
                                    'clone_url',
                                    'compare_url',
                                    'deployments_url',
                                    'downloads_url',
                                    'events_url',
                                    'forks_url',
                                    'git_refs_url',
                                    'git_tags_url',
                                    'git_url',
                                    'merges_url',
                                    'milestones_url',
                                    'mirror_url',
                                    'notifications_url',
                                    'pulls_url',
                                    'releases_url',
                                    'ssh_url',
                                    'stargazers_url',
                                    'statuses_url',
                                    'subscription_url',
                                    'svn_url',
                                    'tags_url',
                                    'trees_url',
                                    'hooks_url',
                                    'issue_comment_url',
                                    'issue_events_url',
                                    'issues_url',
                                    'keys_url',
                                    'labels_url',
                                    'html_url',
                                    'collaborators_url',
                                    'comments_url',
                                    'commits_url',
                                    'contents_url',
                                    'contributors_url',
                                    'git_commits_url',
                                    'languages_url',
                                    'subscribers_url',
                                    'teams_url',
                                    'full_name',
                                    'archived',
                                    'default_branch',
                                    'fork',
                                    'forks',
                                    'node_id',
                                    'open_issues',
                                    'license',
                                    'watchers'
                                ]
                            )
                            df.drop(toDrop, inplace=True, axis=1)

                            # Only process valid indexable repositories
                            if self.dcUtils.columnExistsInDataFrame(df, 'id'):
                                df.set_index('id')

                                df['owner'] = df['owner'].apply(self.dcUtils.getGithubOwnerLogin)
                                df['is_owner'] = df['owner'].apply(self.dcUtils.isGithubUserOwnerRepo, args=(userId,))
                                df['created_at'] = df['created_at'].apply(self.dcUtils.ensureSerializableDate)
                                df['pushed_at'] = df['pushed_at'].apply(self.dcUtils.ensureSerializableDate)
                                df['updated_at'] = df['updated_at'].apply(self.dcUtils.ensureSerializableDate)
                                df.fillna(value=0)

                                # Build the list of repositories and store it on the database
                                userRepos = {}
                                sumReposPerSkill = {}
                                sumStarPerSkill = {}
                                sumWatchersPerSkill = {}
                                sumForksPerSkill = {}
                                strongRepo = ""
                                strongLanguage = ""
                                self.dcUtils.buildDictObjectsFromDataFrame(df, userRepos)

                                # Simple descriptive analysis of the user skills
                                userSkillsAnalysis = {}
                                userSkillsAnalysis["github_userid"] = userId
                                userSkillsAnalysis["location"] = location

                                # Repos x Skills
                                numReposPerSkill = df['language'].value_counts()
                                self.dcUtils.flattenShallowObj(numReposPerSkill, userSkillsAnalysis, "num_repos_skill", sumReposPerSkill)

                                # Strongest repository and language
                                rowRepoMaxNumStars = df['stargazers_count'].idxmax()
                                repoMaxNumStars = df.loc[rowRepoMaxNumStars]
                                strongRepo = repoMaxNumStars["name"]
                                strongLanguage = repoMaxNumStars["language"]
                                userSkillsAnalysis["strong_repo"] = strongRepo
                                userSkillsAnalysis["strong_language"] = strongLanguage

                                # Repos x Stargazers
                                starsPerSkill = df.groupby('language')['stargazers_count'].agg(['sum','max','mean'])
                                self.dcUtils.flattenDeep2Obj(starsPerSkill, userSkillsAnalysis, "lang_x_stargazers", sumStarPerSkill)

                                # Language x Watchers
                                watchersPerSkill = df.groupby('language')['watchers_count'].agg(['sum','max','mean'])
                                self.dcUtils.flattenDeep2Obj(watchersPerSkill, userSkillsAnalysis, "lang_x_watchers", sumWatchersPerSkill)

                                # Language x Forks
                                forksPerSkill = df.groupby('language')['forks_count'].agg(['sum','max','mean'])
                                self.dcUtils.flattenDeep2Obj(forksPerSkill, userSkillsAnalysis, "lang_x_forks", sumForksPerSkill)

                                # Store the results on the database
                                self.dbManager.storeReposGithubUser(token, userId, userRepos)
                                self.dbManager.storeIndicatorsGithubUserSkills(
                                    token,
                                    userId,
                                    sumReposPerSkill,
                                    sumStarPerSkill,
                                    sumWatchersPerSkill,
                                    sumForksPerSkill,
                                    strongRepo,
                                    strongLanguage
                                )
                                self.dbManager.storeAnalysisUserSkills(token, userId, userSkillsAnalysis)

                                # Fetch a successful response to the client                
                                response["msg"] = "We got the user repositories"
                                response["github_user_repos"] = userRepos
                                response["sum_repos_x_skill"] = sumReposPerSkill
                                response["sum_star_x_skill"] = sumStarPerSkill
                                response["sum_watchers_x_skill"] = sumWatchersPerSkill
                                response["sum_forks_x_skill"] = sumForksPerSkill
                                response["strongest_repo"] = strongRepo
                                response["strongest_language"] = strongLanguage

        except Exception as err:
            print("Failed to scrapUserRepositoriesSkillsFromGithub {0}".format(err))

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

                # GET user commits x repo x language
                connection = http.client.HTTPSConnection(self.netUtils.GITHUB_API_ROOT_URL)
                endpoint = "/search/code?q=language:{0}+repo:{1}/{2}".format(
                    urllib.parse.quote(language),
                    urllib.parse.quote(userId),
                    urllib.parse.quote(repo)
                )
                connection.request("GET", endpoint, headers=self.netUtils.AUTH_GITHUB_HEADER)

                res = connection.getresponse()
                data = res.read()
                commitsPerLanguage = json.loads(data.decode(self.netUtils.UTF8_DECODER))

                # Fetch the results that are going to be stored in the database
                if commitsPerLanguage is not None:
                    
                    if "items" in commitsPerLanguage:
                        userCommits = {}
                        codeSamples = {}

                        for commit in commitsPerLanguage["items"]:

                            if "sha" in commit:
                                userCommits[commit["sha"]] = commit

                                # Clean the list of commits
                                if "repository" in commit:
                                    del commit["repository"]

                                # Create a link to the actual file in which the user commited
                                userCodeUrl = commit["html_url"]
                                userCodeUrl = userCodeUrl.replace("api.github.com", "github.com")
                                userCodeUrl = userCodeUrl.replace("blob", "raw")

                                codeSample = {
                                    "commit_sha" : commit["sha"],
                                    "language"   : language,
                                    "code_url"   : userCodeUrl
                                }
                                codeSamples[commit["sha"]] = codeSample

                                response["code_samples"].append(codeSample)

                        # Fetch a success message
                        response["msg"] = "We got a few commits made by the user in {0} ".format(language)
                        response["success"] = True
                        response["github_user_commits"] = userCommits

                        # Stores the user commits and code samples from Github on the database
                        self.dbManager.storeUserCommitsLanguageOnGithubRepo(token, userId, userCommits, codeSamples)

        except Exception as err:
            print("Failed to scrapUserCommitsRepoLanguageFromGithub {0}".format(err))

        return json.dumps(response)

    '''
        Scrap the commits of a Github user made using a given language
    '''
    def scrapUserCommitsLanguageFromGithub(self, token, userId, language):
        response = {
            "success" : False,
            "msg" : "Failed to get the commits and code samples of this Github user",
            "github_user_commits" : "",
            "code_samples" : []
        }

        try:

            if not userId or not language:
                response["msg"] = "Invalid input parameters"
            else:
                print("Requesting list of commits made using a specific language ...")

                # GET user commits x language
                connection = http.client.HTTPSConnection(self.netUtils.GITHUB_API_ROOT_URL)
                endpoint = "/search/code?q=language:{0}+user:{1}".format(
                    urllib.parse.quote(language),
                    urllib.parse.quote(userId)
                )
                connection.request("GET", endpoint, headers=self.netUtils.AUTH_GITHUB_HEADER)

                res = connection.getresponse()
                data = res.read()
                commitsPerLanguage = json.loads(data.decode(self.netUtils.UTF8_DECODER))

                # Fetch the results that are going to be stored in the database
                if commitsPerLanguage is not None:

                    if "items" in commitsPerLanguage:
                        userCommits = {}
                        codeSamples = {}

                        for commit in commitsPerLanguage["items"]:

                            if "sha" in commit:
                                userCommits[commit["sha"]] = commit

                                # Clean the list of commits
                                if "repository" in commit:
                                    del commit["repository"]

                                # Create a link to the actual file in which the user commited
                                userCodeUrl = commit["html_url"]
                                userCodeUrl = userCodeUrl.replace("api.github.com", "github.com")
                                userCodeUrl = userCodeUrl.replace("blob", "raw")

                                codeSample = {
                                    "commit_sha" : commit["sha"],
                                    "language"   : language,
                                    "code_url"   : userCodeUrl
                                }
                                codeSamples[commit["sha"]] = codeSample

                                response["code_samples"].append(codeSample)

                        # Fetch a success message
                        response["msg"] = "We got a few commits made by the user in {0} ".format(language)
                        response["success"] = True
                        response["github_user_commits"] = userCommits

                        # Stores the user commits and code samples from Github on the database
                        self.dbManager.storeUserCommitsLanguageOnGithubRepo(token, userId, userCommits, codeSamples)

        except Exception as err:
            print("Failed to scrapUserCommitsRepoLanguageFromGithub {0}".format(err))

        return json.dumps(response)

    '''
        Get a list of ids of Github users from a location
    '''
    def getGithubUserIdsFromLocation(self, token, location):
        response = {
            "success" : False,
            "msg" : "Failed to get a list of github user ids",
            "github_user_ids" : ""
        }

        try:

            if not token or not location:
                response["msg"] = "Invalid input parameters"
            else:
                print("Requesting list of github user ids ...")

                # GET the list of ids from the project DB
                githubUserIds = self.dbManager.getListGithubUserIdsFromLocation(location)
                
                # Fetch a valid response to the user
                if githubUserIds is not None:
                    
                    # Fetch a success message
                    response["msg"] = "We got a list of github user ids from {0} ".format(location)
                    response["success"] = True
                    response["github_user_ids"] = githubUserIds

        except Exception as err:
            print("Failed to getGithubUserIdsFromLocation {0}".format(err))

        return json.dumps(response)

    '''
        Returns a Github user profile stored in the database
    '''
    def getGithubUser(self, token, userId):
        response = {
            "success" : False,
            "msg" : "Failed to get the profile",
            "github_profile": ""
        }

        try:
            
            if token and userId:
                profile = self.dbManager.getGithubUser(userId)

                if profile:
                    response["success"] = True
                    response["msg"] = "We found the profile"
                    response["github_profile"] = profile

        except Exception as err:
            print("Failed to getGithubUser from DB {0}".format(err))

        return json.dumps(response)

    '''
        Deletes a Github profile from the database
    '''
    def deleteGithubUser(self, token, userId):
        response = {
            "success" : False,
            "msg" : "Failed to delete profile"
        }

        try:
            
            if token and userId:

                if self.dbManager.deleteGithubUser(token, userId):
                    response["success"] = True
                    response["msg"] = "The Github profile has been deleted"

        except Exception as err:
            print("Failed to deleteGithubUser from DB {0}".format(err))

        return json.dumps(response)
