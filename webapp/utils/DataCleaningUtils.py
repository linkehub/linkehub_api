# -*- coding: utf-8 -*-

import math
import numbers
import datetime

from decimal import Decimal
from utils.StringUtils import StringUtils

'''
    Provide methods to extract data during the process of gathering information from external sources.
'''
class DataCleaningUtils():

    def __init__(self):
        self.TAG = "DCUtils"

    def ensureValidString(self, description):
        try:

            if description is not None:
                return description

        except Exception as err:
            print("{0} Failed to ensureValidString {1}".format(self.TAG, err))

        return ""

    def ensureValidFloatNumber(self, number):
        try:

            if number is None or math.isnan(number):
                number = 0

            return number

        except Exception as err:
            print("{0} Failed to ensureValidFloatNumber {1}".format(self.TAG, err))

        return ""

    def ensureSerializableDate(self, timestamp):
        try:

            if timestamp is not None:
                return timestamp.timestamp()

        except Exception as err:
            print("{0} Failed to ensureSerializableDate {1}".format(self.TAG, err))

        return ""

    def getGithubOwnerLogin(self, owner):
        try:

            if owner is not None:

                if "login" in owner:
                    return owner["login"]

        except Exception as err:
            print("{0} Failed to getGithubOwnerLogin {1}".format(self.TAG, err))

        return ""

    def isGithubUserOwnerRepo(self, owner, userId):
        try:

            if owner is not None and userId is not None:

                if userId == owner:
                    return True

        except Exception as err:
            print("{0} Failed to isGithubUserOwnerRepo {1}".format(self.TAG, err))

        return False

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

        except Exception as err:
            print("{0} Failed to buildDictObjectsFromDataFrame {1}".format(self.TAG, err))

        return None

    def flattenShallowObj(self, shallowDict, flatObj, flatKey, frequencySeries):
        try:
            strUtils = StringUtils()

            for key, value in shallowDict.items():
                cFlatKey = strUtils.getCleanedJsonVal(flatKey)
                cKey = strUtils.getCleanedJsonVal(key)

                if cFlatKey is not None and cKey is not None:

                    if cFlatKey is not "" and cKey is not "":
                        flatObj["{0}_{1}".format(cFlatKey, cKey)] = value
                        frequencySeries["{0}_{1}".format(cFlatKey, cKey)] = value

        except Exception as err:
            print("{0} Failed to flattenShallowObj {1}".format(self.TAG, err))

    def flattenDeep2Obj(self, deepDict, flatObj, flatKey, frequencySeries):
        try:
            strUtils = StringUtils()

            for funcName, funcSeries in deepDict.items():

                for langName, funcValue in funcSeries.items():
                    cFlatKey = strUtils.getCleanedJsonVal(flatKey)
                    cFuncName = strUtils.getCleanedJsonVal(funcName)
                    cLangName = strUtils.getCleanedJsonVal(langName)

                    if cFlatKey is not None and cFuncName is not None and cLangName is not None:

                        if cFlatKey is not "" and cFuncName is not "" and cLangName is not "":
                            flatObj["{0}_{1}_{2}".format(cFlatKey, cFuncName, cLangName)] = funcValue

                            if cFuncName == "sum":
                                frequencySeries["{0}_{1}_{2}".format(cFlatKey, cFuncName, cLangName)] = funcValue

        except Exception as err:
            print("{0} Failed to flattenDeep2Obj {1}".format(self.TAG, err))
