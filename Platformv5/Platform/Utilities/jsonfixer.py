import json
#from numpy import unicode
from twisted.python.compat import unicode             ##added import

#from stackoverflow
#http://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-ones-from-json-in-python/6633651#6633651
def byteify(input):
    if isinstance(input, dict):
        return {byteify(key):byteify(value) for key,value in input.items()}          ##changed input.iteritems() to input.items()
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):                                               ## these two lines would be necessary in python 2, not in python 3
        return input.encode('utf-8')                                               ## just get rid of these two lines, do not encode 
    else:
        return input

def aload(instr):
    a = json.loads(instr)
    return byteify(a)
