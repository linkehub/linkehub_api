# -*- coding: utf-8 -*-

import math
import datetime

from utils.StringUtils import StringUtils

'''
    Provide methods to extract data during the process of gathering information from external sources.
'''
class DataCleaningUtils():

    def ensureValidString(self, description):
        try:

            if description is not None:
                return description

            return ""

        except Exception:
            return ""

    def ensureValidFloatNumber(self, number):
        try:

            if number is None or math.isnan(number):
                number = 0

            return number

        except Exception:
            return ""

    def getGithubOwnerLogin(self, owner):
        try:

            if owner is not None:

                if "login" in owner:
                    return owner["login"]

            return ""

        except Exception:
            return ""

    def isGithubUserOwnerRepo(self, owner, userId):
        try:

            if owner is not None and userId is not None:

                if userId == owner:
                    return True

            return False

        except Exception:
            return ""

    def flattenShallowObj(self, shallowDict, flatObj, flatKey):
        try:
            strUtils = StringUtils()

            for key, value in shallowDict.items():
                cFlatKey = strUtils.getCleanedJsonVal(flatKey)
                cKey = strUtils.getCleanedJsonVal(key)

                flatObj["{0}_{1}".format(cFlatKey, cKey)] = value

        except Exception:
            return ""

    def flattenDeep2Obj(self, deepDict, flatObj, flatKey):
        try:
            strUtils = StringUtils()

            for funcName, funcSeries in deepDict.items():
                        
                for langName, funcValue in funcSeries.items():
                    cFlatKey = strUtils.getCleanedJsonVal(flatKey)
                    cFuncName = strUtils.getCleanedJsonVal(funcName)
                    cLangName = strUtils.getCleanedJsonVal(langName)

                    flatObj["{0}_{1}_{2}".format(cFlatKey, cFuncName, cLangName)] = funcValue

        except Exception:
            return ""

    def ensureSerializableDate(self, timestamp):
        try:
            
            if timestamp is not None:
                return timestamp.timestamp()

        except Exception:
            return ""

    def buildDictObjectsFromDataFrame(self, df, dictObj):
        try:
            strUtils = StringUtils()

            for valueSeries in df.values:
                obj = {}
                objKey = ""

                for idx, val in enumerate(valueSeries):
                    cKey = strUtils.getCleanedJsonVal(df.columns[idx])

                    if cKey is not "":
                        obj[cKey] = val

                    if cKey == "name":
                        objKey = strUtils.getCleanedJsonVal(val)

                if objKey is not "":
                    dictObj[objKey] = obj

            return dictObj

        except Exception:
            print("")
