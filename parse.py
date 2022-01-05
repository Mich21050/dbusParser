import json

#simple config
inpFile = "inp.txt"
outFile = "outCmd.txt"
jsonFile = None #set None if you dont need it as a json (helpful when debugging)

def main():
    f = open(inpFile)
    inp = f.readlines()
    f.close()
    parsD = []

    curEl = -1
    global i
    for curL in inp:
        curD = {}
        if curL.split()[0] == "signal" or curL.split()[0] == "method":
            curD["mainStr"] = curL
            spltMain = curL.split()
            dicKeys = [
                'type',
                'sender',
                'dest',
                'serial',
                'interface',
                'member',
                'path'
                ]
            mainStruct = dict.fromkeys(dicKeys)
            for el in dicKeys:
                if el == "type":
                    if spltMain[0] == "signal": 
                        mainStruct["type"] = "signal"
                    elif spltMain[0] == "method":
                        mainStruct["type"] = "method call"
                elif el == 'dest':
                    res = spltMain[searchPart(spltMain,el)].split('=')
                    if res[1] == '(null':
                        mainStruct['dest'] = None
                    else:
                        mainStruct['dest'] = res[1]
                else:
                    res = spltMain[searchPart(spltMain,el)].split('=')
                    mainStruct[el] = res[1].replace(';','')
            #print(mainStruct)
            parsD.append({})
            curEl += 1
            parsD[curEl]['main'] = mainStruct
            parsD[curEl]['data'] = []
        
        else:
            dicKeys = ['type','value']
            chk = curL[0:2]
            if chk.isspace():
                subStruct = dict.fromkeys(dicKeys)
                res = curL.strip().split(' ')
                subStruct['type'] = res[0]
                subStruct['value'] = res[1].replace('"','')
                parsD[curEl]['data'].append(subStruct)
    print(json.dumps(parsD))
    jsonWriter(jsonFile,parsD)

    fC = open(outFile,'w')
    cmdLi = []
    for el in parsD:
        curM = el['main']
        if curM['dest'] == None:
            cmdS = 'dbus-send --system --type={type} {path} {pathMem}'.format(type =curM['type'], pathMem = curM['interface'] + '.' + curM['member'], path = '/' + curM['interface'].replace('.','/'))
        else:
            cmdS = 'dbus-send --system --type={type} --dest={dest} {path} {pathMem}'.format(type =curM['type'].replace(' ','_'), pathMem = curM['interface'] + '.' + curM['member'], path = '/' + curM['interface'].replace('.','/'),dest=curM['dest'])
        for elS in el['data']:
            if elS['type'] == 'string':
                cmdS += ' {type}:"{value}"'.format(type=elS['type'], value=elS['value'])
            else:
                cmdS += ' {type}:{value}'.format(type=elS['type'], value=elS['value'])
        print(cmdS)
        cmdLi.append(cmdS)
    for wEl in cmdLi:
        fC.write(wEl + '\n')
    fC.close()

def searchPart(listIn, searchT):
    for i, elem in enumerate(listIn):
        if searchT in elem:
            return i

def jsonWriter(path, dictIn):
    if path != None:
        with open(path,'w') as fS:
            fS.write(json.dumps(dictIn, indent=4))


if __name__ == '__main__':
    main()