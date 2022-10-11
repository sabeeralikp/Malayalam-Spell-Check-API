import re
from flask import Flask, jsonify, request

nextStateDict = {}
endStateDict = {}
nextStateDictReverse = {}
endStateDictReverse = {}
suggestionDict = {}
look4ForwardBlocks = []
look4ForwardBlocksPosition = []
look4ForwardBlocksKey = {}
look4ReverseBlocks = []
trigramHashFreq = {}
trigramHashOpt = {}
wrdFreqDict = {}
currentWrds = {}
maxStateFSA = 0
maxStateFSAHash = {}
charBag = {}
flagSpellCheck = 0
flagSpellCheck2B = 0
totalCombi = ""
char2intDict = {}
int2charDict = {}
wordFreq = 0
lastCluster = {}
firstCluster = {}
allTrigramHashOpt = {}
maxIndex = 0

signs = [u'\u0d02', u'\u0d03', u'\u0d3e', u'\u0d3f', u'\u0d40', u'\u0d41', u'\u0d42', u'\u0d43', u'\u0d44',
         u'\u0d46', u'\u0d47', u'\u0d48', u'\u0d4a', u'\u0d4b', u'\u0d4c', u'\u0d4d', u'\u0d00', u'\u0d01', u'\u0d57']

chandrakkala = u'\u0d4d'

zeroWidth = [u'\u200d', u'\u200c']


def split_chars(input_word1):
    #text = input_word.decode("utf-8")
    text = str(input_word1)
    # print("inSplitter---"+text)

    text1 = text.replace(',', '')
    text = text1
    text1 = text.replace('.', '')
    text = text1
    text1 = text.replace(';', '')
    text = text1
    text1 = text.replace('\;', '')
    text = text1
    text1 = text.replace(':', '')
    text = text1
    text1 = text.replace('"', '')
    text = text1
    text1 = text.replace(')', '')
    text = text1
    text1 = text.replace('(', '')
    text = text1
    text1 = text.replace('`', '')
    text = text1
    text1 = text.replace('?', '')
    text = text1
    text1 = text.replace('\'', '')
    text = text1
    text1 = text.replace('~', '')
    text = text1
    text1 = text.replace('"', '')
    text = text1
    text1 = text.replace('!', '')
    text = text1
    text1 = text.replace('<', '')
    text = text1
    text1 = text.replace('>', '')
    text = text1
    text1 = text.replace('*', '')
    text = text1
    text1 = text.replace('%', '')
    text = text1
    text1 = text.replace('&', '')
    text = text1
    text1 = text.replace('\.', '')
    text = text1

    text1 = text.replace('ള്‍', 'ൾ')
    text = text1
    text1 = text.replace('ല്‍', 'ൽ')
    text = text1
    text1 = text.replace('ന്‍', 'ൻ')
    text = text1
    text1 = text.replace('ര്‍', 'ർ')
    text = text1
    text1 = text.replace('ണ്‍', 'ൺ')
    text = text1
    text1 = text.replace('ഉൗ', 'ഊ')
    text = text1
    text1 = text.replace('‍ഇൗ', 'ഈ')
    text = text1
    text1 = text.replace('‍ഒൗ', 'ഔ')
    text = text1
    text1 = text1.strip()

    lennn = len(text)

    # if(lennn == 0):
    #     text = str(input_word1)

    lst_chars = []
    for char in text:
        if char not in zeroWidth:
            if char in signs:
                if (len(lst_chars) != 0):
                    lst_chars[-1] = lst_chars[-1] + char
                else:
                    lst_chars.append(char)
            else:
                try:
                    if lst_chars[-1][-1] == chandrakkala:
                        if (len(lst_chars) != 0):
                            lst_chars[-1] = lst_chars[-1] + char
                        else:
                            lst_chars.append(char)
                    else:
                        lst_chars.append(char)
                except IndexError:
                    lst_chars.append(char)

    return lst_chars


def loadcharIndex():
    global maxIndex
    with open('./splrsc/charIndex.txt', 'r', encoding='utf8') as f:
        for line in f:
            line = line.replace('\n', '')
            splitLine = line.split('=>')
            char2intDict[splitLine[0]] = splitLine[1]
            int2charDict[splitLine[1]] = splitLine[0]

            if int(splitLine[1]) > int(maxIndex):
                maxIndex = splitLine[1]

            # print(splitLine[0] + "~~~"+splitLine[1])
            # print(splitLine[1] + "~~~"+splitLine[0])


def load1stCluster():
    # with open('./ml_wrdFreq.txt','r',encoding='utf8') as f: splrsc/f_char.txt
    with open('./splrsc/f_char.txt', 'r', encoding='utf8') as f1:
        for line in f1:
            line = line.replace('\n', '')
            firstCluster[line] = 1


def loadLastCluster():
    # with open('./ml_wrdFreq.txt','r',encoding='utf8') as f:
    with open('./splrsc/l_char.txt', 'r', encoding='utf8') as f1:
        for line in f1:
            line = line.replace('\n', '')
            lastCluster[line] = 1


def spellchk_NG(wrd007):
    letterArray1 = split_chars(wrd007)
    letterArray1.insert(0, "ST")
    letterArray1.append("END")

    l = len(letterArray1)
    l1 = l - 1

    true1 = 1
    true2 = 1
    true3 = 1
    true4 = 1
    true5 = 1

    for ijk in (range(l1)):

        if ((ijk >= 0) and (ijk < l1-1)):
            key1 = letterArray1[ijk]+letterArray1[ijk+1]
            key2 = letterArray1[ijk+1]+letterArray1[ijk+2]
            key = key1 + key2

            if key not in charBag:
                true1 = 0

        if (ijk > 1):
            key1 = letterArray1[ijk-1]+letterArray1[ijk]
            key2 = letterArray1[ijk]+letterArray1[ijk+1]
            key = key1 + key2

            if key not in charBag:
                true2 = 0

        if (ijk > 2):
            key1 = letterArray1[ijk-2]+letterArray1[ijk-1]
            key2 = letterArray1[ijk-1]+letterArray1[ijk]
            key = key1 + key2

            if key not in charBag:
                true3 = 0

    if (len(letterArray1) > 4):
        # if(l1 > 4):
        key1 = letterArray1[1]+letterArray1[2]
        key2 = letterArray1[2]+letterArray1[3]
        key = key1 + key2

        if key not in firstCluster:
            true4 = 0

    #n = len(letterArray1);
    n = l1
    if (len(letterArray1) > 4):
        # if(l1 > 4):
        key1 = letterArray1[n-4]+letterArray1[n-3]
        key2 = letterArray1[n-3]+letterArray1[n-2]
        key = key1 + key2

        if key not in lastCluster:
            true5 = 0

    if (true1 == 1 and true2 == 1 and true3 == 1 and true4 == 1 and true5 == 1):
        return (1)
    else:
        return (0)


def loadTrigramFreqHash():
    # with open('./ml_trigramFreq_280418.txt','r',encoding='utf8') as f:
    # with open('./trigramFreq_120918.txt','r',encoding='utf8') as f:
    with open('./splrsc/3gm_freq.txt', 'r', encoding='utf8') as f:
        for line in f:
            line = line.replace('\n', '')
            st = line.split("=>")
            ds = st[0]
            value = st[0]
            trigramHashFreq[ds] = value


def loadTrigramOpt():
    # with open('./ml_trigramOptions_280418.txt','r',encoding='utf8') as f:
    # with open('./trigram_120918.txt','r',encoding='utf8') as f:
    with open('./splrsc/3gm.txt', 'r', encoding='utf8') as f:
        value = ""
        for line in f:
            line = line.replace('\n', '')
            st = line.split("=>")
            ds = st[0]

            grams = st[1].split(",")

            for gram in grams:
                kk = ds+gram
                allTrigramHashOpt[kk] = 1

            if ds in trigramHashOpt:
                value = trigramHashOpt.get(ds)+","+st[1]
            else:
                value = st[1]

            trigramHashOpt[ds] = value


def readForwardFSA():
    global maxStateFSA

    endstatePattern = '\#\d+'

    with open('./splrsc/f_dfsa.txt', 'r', encoding='utf8') as f:
        for line in f:
            line = line.replace('\n', '')
            splitLine = line.split()

            if (len(splitLine) == 3):
                if re.search(endstatePattern, splitLine[2]):
                    # print(splitLine[2])
                    splitLine[2] = splitLine[2].replace('#', '')
                    endStateDict[splitLine[0]] = splitLine[2]
                else:
                    if splitLine[2] in int2charDict:
                        splitLine[2] = int2charDict[splitLine[2]]
                    else:
                        print(splitLine[2] + "not found")

                    key = ",".join(splitLine[0::2])
                    nextSttt = int(splitLine[1])
                    if (maxStateFSA < nextSttt):
                        maxStateFSA = nextSttt

                    if key in nextStateDict:
                        value = nextStateDict.get(key)
                        value = value + ","+splitLine[1]
                        nextStateDict[key] = value
                    else:
                        nextStateDict[key] = splitLine[1]
            else:

                endStateDict[(splitLine[0])] = 0


def readReverseFSA():
    # with open('./reverseFSA_DFSA_300520.txt','r',encoding='utf8') as f:
    with open('./splrsc/r_dfsa.txt', 'r', encoding='utf8') as f:
        for line in f:
            line = line.replace('\n', '')
            splitLine = line.split()
            if (len(splitLine) == 3):
                if splitLine[2] in int2charDict:
                    splitLine[2] = int2charDict[splitLine[2]]
                else:
                    print(splitLine[2] + "not found")

                key = ",".join(splitLine[0::2])
                if key in nextStateDictReverse:
                    value = nextStateDictReverse.get(key)
                    value = value + ","+splitLine[1]
                    nextStateDictReverse[key] = value
                else:
                    nextStateDictReverse[key] = splitLine[1]
            else:
                endStateDictReverse[(splitLine[0])] = 0


def reverse_array(char_array):
    reverse_char_array = list(char_array)
    reverse_char_array.reverse()

    return reverse_char_array


def traverseForwardFSA(stStart, arrayPosi, checkSymbol, wordLength, wordArray):
    global flagSpellCheck
    global wordFreq
    # print(endStateDict)
    key1 = stStart + "," + checkSymbol
    # print("keysis"+key1)

    if key1 in nextStateDict:
        nextSt = nextStateDict.get(key1)
        #print("Next states are "+str(nextSt))
        nextStates = str(nextSt).split(",")
        nextArrayPosi = arrayPosi+1
        #print("key is in dict  "+str(nextArrayPosi)+"   "+str(wordLength))

        if (nextArrayPosi == wordLength):
            for k in range(len(nextStates)):
                #print("check state--"+str(nextStates[k]))
                checkState = nextStates[k]

                if checkState in endStateDict:
                    #print("Word is correct")
                    flagSpellCheck = 1
                    # print("\nFrequency"+str(endStateDict[checkState]))
                    wordFreq = endStateDict[checkState]
                    # print("\nFrequency"+str(wordFreq))
                else:
                    #print(checkState+" not in endStateDict")
                    checkState = int(checkState)
                    if checkState in endStateDict:
                        #print (str(checkState)+"is there")
                        #print("Word is correct")
                        flagSpellCheck = 1
                        # print("\nFrequency"+str(endStateDict[checkState]))
                        wordFreq = endStateDict[checkState]
                        # print("\nFrequency"+str(wordFreq))
        else:
            for k in range(len(nextStates)):
                traverseForwardFSA(
                    nextStates[k], nextArrayPosi, wordArray[nextArrayPosi], wordLength, wordArray)


def traverseReverseFSA(stStart, arrayPosi, checkSymbol, wordLength, wordArray):
    global flagSpellCheck
    key1 = stStart + "," + checkSymbol

    if key1 in nextStateDictReverse:
        nextSt = nextStateDictReverse.get(key1)
        nextStates = nextSt.split(",")
        nextArrayPosi = arrayPosi+1

        if (nextArrayPosi == wordLength):
            for k in range(len(nextStates)):
                checkState = nextStates[k]
                if checkState in endStateDictReverse:
                    # print("Word is correct")
                    flagSpellCheck = 1
        else:
            for k in range(len(nextStates)):
                traverseReverseFSA(
                    nextStates[k], nextArrayPosi, wordArray[nextArrayPosi], wordLength, wordArray)


def getForwardBlocksPosition(stStart, arrayPosi, checkSymbol, wordLength, wordArray):
    print(stStart, arrayPosi, checkSymbol, wordLength, wordArray)
    key1 = stStart + "," + checkSymbol
    if key1 in nextStateDict:
        nextSt = nextStateDict.get(key1)
        nextStates = str(nextSt).split(",")
        nextArrayPosi = arrayPosi+1

        if (nextArrayPosi == wordLength):
            for k in range(len(nextStates)):
                checkState = int(nextStates[k])
                if checkState in endStateDict:
                    # print("Word is correct")
                    flagSpellCheck = 1

        else:
            for k in range(len(nextStates)):
                getForwardBlocksPosition(
                    nextStates[k], nextArrayPosi, wordArray[nextArrayPosi], wordLength, wordArray)
    else:
        # print("ArrayPOsition"+str(arrayPosi))
        # print("keyInfo"+key1)
        look4ForwardBlocksPosition.append(arrayPosi)
        look4ForwardBlocksKey[arrayPosi] = stStart


def getForwardBlocks(stStart, arrayPosi, checkSymbol, wordLength, wordArray):
    key1 = stStart + "," + checkSymbol
    if key1 in nextStateDict:
        nextSt = nextStateDict.get(key1)
        nextStates = nextSt.split(",")
        nextArrayPosi = arrayPosi+1

        if (nextArrayPosi == wordLength):
            for k in range(len(nextStates)):
                checkState = nextStates[k]
                if checkState in endStateDict:
                    # print("Word is correct")
                    flagSpellCheck = 1
        else:
            for k in range(len(nextStates)):
                getForwardBlocks(
                    nextStates[k], nextArrayPosi, wordArray[nextArrayPosi], wordLength, wordArray)
    else:
        look4ForwardBlocks.append(arrayPosi)


def getReverseBlocks(stStart, arrayPosi, checkSymbol, wordLength, wordArray):
    key1 = stStart + "," + checkSymbol
    if key1 in nextStateDictReverse:
        nextSt = nextStateDictReverse.get(key1)
        nextStates = nextSt.split(",")
        nextArrayPosi = arrayPosi+1

        if (nextArrayPosi == wordLength):
            for k in range(len(nextStates)):
                checkState = nextStates[k]
                if checkState in endStateDictReverse:
                    # print("Word is correct")
                    flagSpellCheck = 1
        else:
            for k in range(len(nextStates)):
                getReverseBlocks(
                    nextStates[k], nextArrayPosi, wordArray[nextArrayPosi], wordLength, wordArray)
    else:
        look4ReverseBlocks.append(arrayPosi)


def wrdsFromDeletion(dummyWrds, nstart, nend):
    global suggestionDict
    global wordFreq

    if (len(dummyWrds) > 2):
        for jj in range(nstart, nend+1):
            wL = len(dummyWrds)
            wL -= 1
            dArray = []

            kji = 0
            for ijk in range(len(dummyWrds)):
                if (ijk != jj):
                    dArray.append(dummyWrds[ijk])

                kji += 1

            wrdN = "".join(dArray)
            res1 = spellchk(wrdN)
            if (res1):
                suggestionDict[wrdN] = wordFreq


def wrdsFromTransposition(dummyWrds, nstart, nend):
    global suggestionDict
    global wordFreq

    if (len(dummyWrds) > nend):
        nnend = nend+1
    else:
        nnend = nend

    for jj in range(nstart, nnend):
        wL = len(dummyWrds)
        dArray = []

        kji = 0
        for ijk in range(len(dummyWrds)):
            if ((ijk == jj) and (kji != 0)):
                temp = dArray[kji-1]
                dArray[kji-1] = dummyWrds[ijk]
                dArray.append(temp)
                kji += 1
            else:
                dArray.append(dummyWrds[ijk])
                kji += 1

        wrdN = "".join(dArray)
        res1 = spellchk(wrdN)

        if (res1):
            suggestionDict[wrdN] = wordFreq


def wrdsFromReplace(dummyWrds, nstart, nend):
    global suggestionDict
    global wordFreq

    if (len(dummyWrds) > nend):
        nnend = nend+1
    else:
        nnend = nend

    for jj in range(nstart, nnend):
        if (jj+2 < len(dummyWrds)):

            key_sgA = dummyWrds[jj]+"_"+dummyWrds[jj+2]
            if (key_sgA in trigramHashOpt):
                optValues = trigramHashOpt.get(key_sgA)

                optLetters = optValues.split(",")

                for kk in range(len(optLetters)):
                    wL = len(dummyWrds)
                    dArray = []

                    kji = 0
                    for ijk in range(len(dummyWrds)):
                        if (ijk == jj+1):
                            dArray.append(optLetters[kk])
                            kji += 1
                        else:
                            dArray.append(dummyWrds[ijk])
                            kji += 1

                    wrdN = "".join(dArray)
                    res1 = spellchk(wrdN)
                    if (res1):
                        suggestionDict[wrdN] = wordFreq

            key_sgA = "_"+dummyWrds[jj]+dummyWrds[jj+1]

            if (key_sgA in trigramHashOpt):

                optValues = trigramHashOpt.get(key_sgA)

                optLetters = optValues.split(",")

                for kk in range(len(optLetters)):
                    wL = len(dummyWrds)
                    dArray = []

                    kji = 0
                    for ijk in range(len(dummyWrds)):
                        if (ijk == jj-1):
                            dArray.append(optLetters[kk])
                            kji += 1
                        else:
                            dArray.append(dummyWrds[ijk])
                            kji += 1

                    wrdN = "".join(dArray)
                    res1 = spellchk(wrdN)
                    if (res1):
                        suggestionDict[wrdN] = wordFreq

            key_sgA = dummyWrds[jj]+dummyWrds[jj+1]+"_"

            if (key_sgA in trigramHashOpt):

                optValues = trigramHashOpt.get(key_sgA)

                optLetters = optValues.split(",")

                for kk in range(len(optLetters)):
                    wL = len(dummyWrds)
                    dArray = []

                    kji = 0
                    for ijk in range(len(dummyWrds)):
                        if (ijk == jj+2):
                            dArray.append(optLetters[kk])
                            kji += 1
                        else:
                            dArray.append(dummyWrds[ijk])
                            kji += 1

                    wrdN = "".join(dArray)
                    res1 = spellchk(wrdN)
                    if (res1):
                        suggestionDict[wrdN] = wordFreq


def wrdsFromAddition(dummyWrds, nstart, nend):
    global suggestionDict
    global wordFreq

    if (len(dummyWrds) > nend):
        nnend = nend+1
    else:
        nnend = nend

    for jj in range(nstart, nnend):
        if (jj+1 < len(dummyWrds)):
            key_sgA = dummyWrds[jj]+"_"+dummyWrds[jj+1]

            if key_sgA in trigramHashOpt:
                optValues = trigramHashOpt.get(key_sgA)
                optLetters = optValues.split(",")

                for kk in range(len(optLetters)):
                    wL = len(dummyWrds)
                    wL += 1
                    dArray = []

                    kji = 0
                    for ijk in range(len(dummyWrds)):
                        if (ijk == jj+1):
                            dArray.append(optLetters[kk])
                            kji += 1

                        dArray.append(dummyWrds[ijk])
                        kji += 1

                    wrdN = "".join(dArray)
                    res1 = spellchk(wrdN)
                    wordFreq = 100
                    if (res1):
                        suggestionDict[wrdN] = wordFreq

            key_sgA = "_"+dummyWrds[jj]+dummyWrds[jj+1]
            if key_sgA in trigramHashOpt:
                optValues = trigramHashOpt.get(key_sgA)
                optLetters = optValues.split(",")

                for kk in range(len(optLetters)):
                    wL = len(dummyWrds)
                    wL += 1
                    dArray = []

                    kji = 0
                    for ijk in range(len(dummyWrds)):
                        if (ijk == jj):
                            dArray.append(optLetters[kk])
                            kji += 1

                        dArray.append(dummyWrds[ijk])
                        kji += 1

                    wrdN = "".join(dArray)
                    res1 = spellchk(wrdN)
                    wordFreq = 100
                    if (res1):
                        suggestionDict[wrdN] = wordFreq

            key_sgA = dummyWrds[jj]+dummyWrds[jj+1]+"_"
            if key_sgA in trigramHashOpt:
                optValues = trigramHashOpt.get(key_sgA)
                optLetters = optValues.split(",")

                optValues1 = optValues
                optValues1 = optValues1.replace(",", ";")

                #keyQAZ = key_sgA+"~!!~"+optValues1+str(jj)
                #suggestionDict[keyQAZ] = 0
                for kk in range(len(optLetters)):
                    wL = len(dummyWrds)
                    wL += 1
                    dArray = []

                    kji = 0
                    for ijk in range(len(dummyWrds)):
                        # for ijk in range(wL):
                        if (ijk == jj+2):
                            dArray.append(optLetters[kk])
                            kji += 1

                        dArray.append(dummyWrds[ijk])
                        kji += 1

                    if (jj+2 == ijk+1):
                        dArray.append(optLetters[kk])
                        kji += 1

                    wrdN = "".join(dArray)
                    res1 = spellchk(wrdN)
                    #wrdN = wrdN + str(res1)
                    #res1 = 1
                    wordFreq = 100
                    if (res1):
                        suggestionDict[wrdN] = wordFreq


def addToFSA(wrd007):
    letterArray1 = split_chars(wrd007)

    startSt = "0"
    flagSpellCheck = 0

    global maxStateFSA
    global look4ForwardBlocksPosition
    global look4ForwardBlocksKey
    global currentWrds
    global maxIndex
    global trigramHashOpt
    global allTrigramHashOpt
    global nextStateDict
    global endStateDict

    currentWrds[wrd007] = 1

    if (len(letterArray1) > 2):
        for i in range(len(letterArray1)-2):
            key = letterArray1[i]+letterArray1[i+1]+"_"

            kk1 = key+letterArray1[i+2]

            if kk1 not in allTrigramHashOpt:
                if key in trigramHashOpt:
                    value = trigramHashOpt.get(key)
                    value = value+","+letterArray1[i+2]
                    trigramHashOpt[key] = value
                else:
                    trigramHashOpt[key] = letterArray1[i+2]

            key = letterArray1[i]+"_"+letterArray1[i+2]
            kk1 = key+letterArray1[i+1]

            if kk1 not in allTrigramHashOpt:
                if key in trigramHashOpt:
                    value = trigramHashOpt.get(key)
                    value = value+","+letterArray1[i+1]
                    trigramHashOpt[key] = value
                else:
                    trigramHashOpt[key] = letterArray1[i+1]

            key = "_"+letterArray1[i+1]+letterArray1[i+2]
            kk1 = key+letterArray1[i]

            if kk1 not in allTrigramHashOpt:
                if key in trigramHashOpt:
                    value = trigramHashOpt.get(key)
                    value = value+","+letterArray1[i]
                    trigramHashOpt[key] = value
                else:
                    trigramHashOpt[key] = letterArray1[i]

    with open('./splrsc/3gm.txt', 'w', encoding='utf8') as f:
        for kk in trigramHashOpt:
            f.write(kk+"=>"+trigramHashOpt[kk]+"\n")
    f.close()

    letterArray1.append('#100')

    # with open('./forwardFSA_dfs_290718.txt','a+',encoding='utf8') as f:
    # 	f.write("\nNewlyAdding --"+ wrd007)
    # f.close()

    look4ForwardBlocksPosition = []
    look4ForwardBlocksKey.clear()

    wS = len(letterArray1)

    getForwardBlocksPosition(startSt, 0, letterArray1[0], wS, letterArray1)

    # print(look4ForwardBlocksPosition)
    # print(look4ForwardBlocksKey)

    if (len(look4ForwardBlocksPosition) > 0):
        maxPosition = max(look4ForwardBlocksPosition)
        # print("MaxPosition----")
        # print(maxPosition)
        # print(letterArray1[maxPosition])
        # print(look4ForwardBlocksKey[maxPosition])

        currentStateNew = look4ForwardBlocksKey[maxPosition]
        # print("CurrentNewState")
        # print(currentStateNew)
        nextStateNew = maxStateFSA+1
        # print(nextStateNew)

        # with open('./forwardFSA_dfs_290718.txt','a+',encoding='utf8') as f:
        # with open('./forwardFSA_dfs_120918.txt','a+',encoding='utf8') as f:
        with open('./splrsc/f_dfsa.txt', 'a+', encoding='utf8') as f:
            for ijk in range(maxPosition, wS):
                # print(ijk)
                # print(letterArray1[ijk])
                # print(str(currentStateNew)+"\t"+str(nextStateNew)+"\t"+letterArray1[ijk])
                # f.write(str(currentStateNew)+"\t"+str(nextStateNew)+"\t"+char2intDict[letterArray1[ijk]]+"\n")

                char2repl = ''
                endstatePattern = '\#\d+'
                if re.search(endstatePattern, letterArray1[ijk]):
                    char2repl = letterArray1[ijk]
                elif letterArray1[ijk] in char2intDict:
                    char2repl = char2intDict[letterArray1[ijk]]
                else:
                    newMaxIndex = int(maxIndex)+1
                    char2repl = newMaxIndex
                    with open('./splrsc/charIndex.txt', 'a+', encoding='utf8') as fo:
                        fo.write(letterArray1[ijk]+"=>"+str(newMaxIndex)+"\n")
                    fo.close()
                    maxIndex = int(maxIndex) + 1

                f.write(str(currentStateNew)+"\t" +
                        str(nextStateNew)+"\t"+str(char2repl)+"\n")
                if re.search(endstatePattern, letterArray1[ijk]):
                    tempContainer = letterArray1[ijk]
                    tempContainer = tempContainer.replace('#', '')
                    endStateDict[currentStateNew] = tempContainer
                    #print("Endstate -"+str(currentStateNew)+"~~~"+str(tempContainer))
                else:
                    neewKeey = str(currentStateNew)+","+letterArray1[ijk]
                    nextStateDict[neewKeey] = nextStateNew
                    #print("Newly added in FSA -- "+str(neewKeey)+"~~~"+str(nextStateNew))
                currentStateNew = nextStateNew
                nextStateNew += 1

            f.write(str(currentStateNew)+"\n")
            maxStateFSA = currentStateNew
        f.close()

        with open('./splrsc/charRsc.txt', 'a+', encoding='utf8') as f:
            letterArray1.insert(0, 'ST')
            letterArray1.append('END')

            if (len(letterArray1) > 2):
                for i in range(len(letterArray1)-1):
                    key1 = letterArray1[i-1]+letterArray1[i]
                    key2 = letterArray1[i]+letterArray1[i+1]
                    key = key1 + key2

                    if key not in charBag:
                        f.write(key)
                        f.write('\n')
                        charBag[key] = 1
        f.close()


def ReverseArray(lst):
    lst.reverse()
    return lst


def suggestionGeneration(letterArray):
    global suggestionDict
    suggestionDict.clear()
    global look4ForwardBlocks
    look4ForwardBlocks = []
    global look4ReverseBlocks
    look4ReverseBlocks = []
    global flagSpellCheck

    wS = len(letterArray)

    normalisedWrd = "".join(letterArray)

    if (spellchk(normalisedWrd)):
        return (normalisedWrd)

    startSt = "0"
    flagSpellCheck = 0

    r_letterArray = reverse_array(letterArray)

    getForwardBlocks(startSt, 0, letterArray[0], wS, letterArray)
    getReverseBlocks(startSt, 0, r_letterArray[0], wS, r_letterArray)

    sugL = ""

    if ((len(look4ForwardBlocks) > 0) and (len(look4ReverseBlocks) > 0)):
        # print look4ForwardBlocks
        # print look4ReverseBlocks

        maxForwardLength = max(look4ForwardBlocks)
        maxReverseLength = max(look4ReverseBlocks)

        minReverseLength = wS-maxReverseLength

        # print("Max Forward:", maxForwardLength)
        # print("Min Reverse:", minReverseLength)

        start = 0
        end = 0

        if (minReverseLength < 0):
            minReverseLength = 0

        if (maxForwardLength < 0):
            maxForwardLength = 0

        if (minReverseLength > maxForwardLength):
            start = maxForwardLength
            end = minReverseLength
        else:
            end = maxForwardLength
            start = minReverseLength

        if (start == end):
            if (start - 2 >= 0):
                # start=start-2
                start = 0
            elif (start-1 >= 0):
                # start=start-1
                start = 0
        elif (start == wS):
            # start=start-2
            start = 0
        elif (start > 0):
            start -= 1

        if (end < (wS-1)):
            end += 1

        if (start+2 == wS):
            start -= 1
            start -= 1

        if (start < 0):
            start = 0

        if (end < 0):
            end = wS

        if ((start == 0) and (end == 0)):
            end = wS
            end -= 1

        # print("Start=",start);
        # print("End=",end);
    else:
        start = 0
        end = len(letterArray)

    wrdsFromDeletion(letterArray, start, end)
    wrdsFromTransposition(letterArray, start, end)
    wrdsFromReplace(letterArray, start, end)
    wrdsFromAddition(letterArray, start, end)

    sgWrds = sorted(suggestionDict, key=suggestionDict.get, reverse=True)

    if (len(sgWrds) == 0):
        start = 0
        end = len(letterArray)

        wrdsFromDeletion(letterArray, start, end)
        wrdsFromTransposition(letterArray, start, end)
        wrdsFromReplace(letterArray, start, end)
        wrdsFromAddition(letterArray, start, end)

        sgWrds = sorted(suggestionDict, key=suggestionDict.get, reverse=True)

    #sgWrdR = ReverseArray(sgWrds)

    sugL = ""
    for sgWrd in sgWrds:
        if (sugL == ""):
            sugL = sgWrd
        else:
            sugL = sugL+","+sgWrd

    #sugL = ""
    #maxiSug = 1000
    # if(len(sgWrds) < maxiSug):
    #    maxiSug = len(sgWrds)

    # if(maxiSug > 0):
    #    for ijk in range(maxiSug):
    #        if(sugL == ""):
    #            sugL = sgWrds[ijk]
    #        else:
    #            sugL = sugL+","+sgWrds[ijk]

    return (sugL)


def loadCiC():
    # with open('./ml_wrdFreq.txt','r',encoding='utf8') as f:
    with open('./splrsc/charRsc.txt', 'r', encoding='utf8') as f1:
        for line in f1:
            line = line.replace('\n', '')
            charBag[line] = 1

def spellchk(inpWrd):
    global flagSpellCheck
    global wordFreq
    global currentWrds

    inpWrd = str(inpWrd)
    # if inpWrd in currentWrds:
    #    return(currentWrds[inpWrd])
    # else:
    ijk123 = 1
    if (ijk123):
        pattern = re.compile('[0-9]+')
        if (pattern.match(inpWrd)):
            currentWrds[inpWrd] = 1
            return (1)

        pattern = re.compile('-')
        if (pattern.match(inpWrd)):
            currentWrds[inpWrd] = 1
            return (1)

        pattern = re.compile(r'^[\)\{\}\(]$')
        if (pattern.match(inpWrd)):
            currentWrds[inpWrd] = 1
            return (1)

        checkWord = split_chars(inpWrd)
        # checkWord = inpWrd

        # r_checkWord = reverse_array(checkWord)

        wordSize = len(checkWord)

        if (wordSize == 0):
            currentWrds[inpWrd] = 1
            flagSpellCheck = 1
        else:
            startSt = "0"
            flagSpellCheck = 0
            NG_flag = 0

            traverseForwardFSA(startSt, 0, checkWord[0], wordSize, checkWord)
        # traverseReverseFSA(startSt,0,r_checkWord[0], wordSize, r_checkWord);

        #flagSpellCheck = wordSize

            if (flagSpellCheck == 0):
                flagSpellCheck = spellchk_NG(inpWrd)

            for lt in checkWord:
                if (lt == '-'):
                    flagSpellCheck = 1

        currentWrds[inpWrd] = flagSpellCheck
        return (flagSpellCheck)
