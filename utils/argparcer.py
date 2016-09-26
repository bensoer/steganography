__author__ = 'bensoer'

class ArgParcer:

    @staticmethod
    def getValue(args, key, default=""):
        for index, item in enumerate(args):
            if item == key:
                valueIndex = index + 1
                return args[valueIndex]
        return default

    @staticmethod
    def keyExists(args, key):
        for index, item in enumerate(args):
            if item == key:
                return True
        return False
