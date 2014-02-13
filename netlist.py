#!/usr/bin/python

# URLs of the OrCAD netlist files - pstchip.dat, pstxnet.dat, pstxprt.dat
chip = "C:\Users\Jade Deng\PycharmProjects\OrcadNetlister\pstchip.dat"
xnet = "C:\Users\Jade Deng\PycharmProjects\OrcadNetlister\pstxnet.dat"
xprt = "C:\Users\Jade Deng\PycharmProjects\OrcadNetlister\pstxprt.dat"

class Part:
    def __init__(self, name, desc):
      self.name_ = name
      self.desc_ = desc
      self.properties_ = {}

    def __str__(self):
        return self.name_

    def setProperties(self, key, value):
        self.properties_[key] = value

    def description(self):
        return self.desc_

    def name(self):
        return self.name_

class Primitive:
    def __init__(self, name):
        self.name_ = name
        self.pins_ = []
        self.properties_ = {}

    def setName(self, name):
        self.name_ = name

    def addPin(self, num):
        self.pins_.append(num)

    def addProperty(self, prop, value):
        self.properties_[prop] = value

    def name(self):
        return self.name_

    def pins(self):
        return self.pins_

    def properties(self):
        return self.properties_

def stripquotes(name):
   if (len(name) > 1):
       ind1 = name.find("'")
       ind2 = name.find("'", ind1+1)
   if ind1 < 0 or ind2 < 0:
        return name
   return name[ind1+1:ind2]

def parsefield(field):
    ind = field.find('=')
    if (len(field) > 1) and ind > -1:
        fieldkey = field[0:ind]
        fieldvalue = stripquotes(field[ind+1:])
        return fieldkey, fieldvalue
    return None

def parsepin(p):
    pn = p[1][1:-1]
    pinnumber = pn.split(",")
    for pin in pinnumber:
        if pin != "0":
            return pin
    print "Unable to parse pin"
    return -1

# split spaces unless between quotes
def newsplit(s):
    words = s.split('"')
    newWords = []
    for w in words:
        seg = w.split("'")
        newWords = newWords + seg
    count = 0
    splitline = []
    for w in newWords:
        if count % 2 == 0:
          w = w.split()
        if type(w) is str:
            splitline.append(w)
        else:
            splitline = splitline + w
        count = count + 1
    if splitline[len(splitline) - 1] == ";":
        splitline = splitline[:len(splitline)-1]
    return splitline

# parse pstxprt.dat file to retrieve parts
def parseXprt(filename):
    partsList = {}
    while(True):
        f_ = filename.readline().strip()
        if f_ and f_ == "PART_NAME":
            f_ = filename.readline().strip().split(' ', 1)
            partName = f_[0]
            partDesc = f_[1][:-1]
            partDesc = stripquotes(partDesc)
            part = Part(partName, partDesc)
            while(True):
                f_ = filename.readline().strip()
                if not f_:
                    break
                else:
                    propLine = parsefield(f_)
                    part.setProperties(propLine[0], propLine[1])
            partsList[partName] = part
        elif f_ and f_ == "END.":
            break
    return partsList

# parse pstxnet.dat file to retrieve nets
def parseXnet(filename):
    netsList = {}
    f_ = filename.readline().strip()
    while(True):
        if f_ != "NET_NAME" and f_ != "END.":
            f_ = filename.readline().strip()
        if f_ == "NET_NAME":
            f_ = filename.readline().strip()
            netName = stripquotes(f_)
            nodes = []
            while(True):
                f_ = filename.readline().strip()
                f_split = f_.split()
                if f_split[0] == "NODE_NAME":
                    node = f_split[1] + "." + f_split[2]
                    nodes.append(node)
                if f_ and (f_ == "NET_NAME" or f_ == "END."):
                    break
            netsList[netName] = nodes
        elif f_ == "END.":
            break
    return netsList

# parse pstxchip.dat file to retrieve primitives
def parseChip(filename):
    primitiveList = {}
    f_ = filename.readline().strip()
    f_split = newsplit(f_)
    while(True):
        if f_split and f_split[0] == "primitive":
            desc = f_split[1]
            primitive = Primitive(desc)
            while(True):
                f_ = filename.readline().strip()
                f_split = newsplit(f_)
                if f_split[0] == "primitive" or f_split[0] == "END.":
                    break
                else:
                    f_split = parsefield(f_)
                    if f_split and len(f_split) == 2:
                        if f_split[0] == "PIN_NUMBER":
                            primitive.addPin(parsepin(f_split))
                        elif f_split[0] == "PART_NAME":
                            primitive.setName(f_split[1])
                        elif f_split[0] != "PINUSE": # all others are added to properties, except PINUSE since we don't care about it
                            primitive.addProperty(f_split[0], f_split[1])
            primitiveList[desc] = primitive
            if f_split[0] == "END.":
                    return primitiveList
        else:
            f_ = filename.readline().strip()
            f_split = newsplit(f_)


f = open(xprt, "r")
parts = parseXprt(f)

f = open(xnet, "r")
nets = parseXnet(f)

f = open(chip, "r")
chips = parseChip(f)

f.close()
