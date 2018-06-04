# -*- coding: utf-8 -*-

'''
    Provide methods to manipulate strings.
'''
class StringUtils():

    def __init__(self):
        self.FORBIDDEN_JSON_CHAR_IN_KEY_VALUES = "$ # [ ] / or ."

    def getCleanedJsonValue(self, rawJsonValue):
        try:

            if rawJsonValue is not None:

                if not isinstance(rawJsonValue, (int, float, bool)):
                    rawJsonValue = rawJsonValue.replace("$","-")
                    rawJsonValue = rawJsonValue.replace("#","-")
                    rawJsonValue = rawJsonValue.replace("[","-")
                    rawJsonValue = rawJsonValue.replace("]","-")
                    rawJsonValue = rawJsonValue.replace("/","-")
                    rawJsonValue = rawJsonValue.replace(".","-")

        except Exception as e:
            print("StringUtils: Failed to getCleanedJsonValue: {0} ".format(e))

        return rawJsonValue