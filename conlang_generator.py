#!/usr/bin/python3
import os
import sys
import json
import random
import math
from RandomGen import YuleDistr

words = [] #word list
phonemes = {} #phonemes dictionary: key is a wildcard, and value is a set of phonemes
exceptions = [] #forbidden phonemic sequences
soundChanges = []
phonemeRanks = {}
wordPattern = "" #word pattern like (C)V(n)(CV)(n), (C)(R)V(R)(n) etc.
filename = 'example.json'
yd = YuleDistr()
semes = [] #list of meanings (words from another language)

running = True

def generate_words(sample, phonemes, num=10): 
    global words, yd
    gen = True
    parens = 0
    r = random.random()
    word = ""
    i = 0
    while i < int(num):
        for j in range(0, len(sample)):
            if sample[j] == '(':
                if gen:
                    gen = (random.randint(0,1) == 0)
                if not gen:
                    parens += 1
            elif sample[j] == ')':
                if not gen:
                    parens -= 1
                if parens == 0:
                    gen = True
            elif sample[j] in phonemes.keys():
                for n, phtype in enumerate(phonemes.keys()):
                    if gen and phtype == sample[j]:
                        #k = random.choice(phonemes[phtype])
                        n = yd.randomGen(phonemeRanks[phtype])
                        k = phonemes[phtype][n]
                        word += k
            elif gen:
                word += sample[j]
                    
        if (not word in words) and (not isExceptional(word)):
            words.append(word)

        i += 1
        word = ""

#has the word any forbidden phonemic sequence?
def isExceptional(word):
    global exceptions
    for i in range(0, len(exceptions)):
        if exceptions[i] in word:
            return True
    return False

"""parsing sound changes rule with the notation X>Y/Z, where X is a set of source phonemes
Y - a set of resulting phonemes, Z - a positional condition (optional)"""
def parsePhNotation(inline):
    rule = inline.split('>')
    if (not len(rule) == 2):
        return []

    source = rule[0].split(',')
    final = rule[1].split('/')

    result = final[0].split(',')
    posCond = []
    rule = []
    if (len(final) > 2):
        return False
    elif (len(final) == 2):
        posCond = final[1].split('_')
        if (not len(posCond) == 2):
            return []
        posCond[0] = posCond[0].split('#')
        posCond[1] = posCond[1].split('#')


        
        if (len(posCond[0]) == 2) and len(posCond[0][0]) > 0:
            return []
        elif len(posCond[0]) == 2:
            rule.append(" "+posCond[0][1])
        else:
            rule.append(posCond[0][0])

        if (len(posCond[1]) == 2) and len(posCond[1][1]) > 0:
            return []

        rule.append(posCond[1][0])
        if len(posCond[1]) == 2:
            rule[1] += " "
        
        rule[0] = rule[0].split(",")
        rule[1] = rule[1].split(",")

    final = []
    if len(source) > len(result):
        for i in range(len(result)-1, len(source)-1):
            result.append("")
    elif len(source) < len(result):
        for i in range(len(source)-1, len(result)-1):
            source.append("")

    final.append(source)
    final.append(result)
    if (len(rule)>0):
        final.append(rule)
    return final


#do phonemic sequence follow condition?
def matchCondition(bSeq, eSeq, word, pos, seq):
    wordR = " "+word+" "
    posR = pos + 1
    for i in range(0, len(bSeq)):
        if len(bSeq[i]) == 0:
            bCond = True
            break
        elif posR<len(bSeq[i]):
            bCond = False
        else:
            bCond = matchSequences(bSeq[i]+seq, wordR[posR-len(bSeq[i]):posR-len(bSeq[i])+len(bSeq[i]+seq)])
            if bCond:
                break
    for i in range(0, len(eSeq)):
        if (len(eSeq[i]) == 0):
            eCond = True
            break
        elif posR+len(seq+eSeq[i])>len(wordR):
            eCond = False
        else:
            eCond = matchSequences(seq+eSeq[i], wordR[posR:posR+len(seq+eSeq[i])])
            if eCond:
                break
    return bCond and eCond

#are two phonemic sequences matching?
def matchSequences(seq1, seq2):
    global phonemes
    if not len(seq1) == len(seq2):
        return False
    for i in range(0, len(seq1)):
        #if 65 <= ord(seq1[i]) <= 90:
        if seq1[i] in phonemes.keys():
            #if (65 <= ord(seq2[i]) <= 90) and (seq1[i] == seq2[i]):
            if (seq2[i] in phonemes.keys()) and (seq1[i] == seq2[i]):
                pass
            elif seq2[i] in phonemes.get(seq1[i]):
                pass
            else:
                return False
        #elif 65 <= ord(seq2[i]) <= 90:
        elif seq2[i] in phonemes.keys():
            if seq1[i] in phonemes.get(seq2[i]):
                pass
            else:
                return False
        elif (seq1[i] == seq2[i]):
            pass
        else:
            return False

    return True

#apply sound change to a word 
def proceedChange(word, change):
    resWord = word
    law = parsePhNotation(change)
    if (len(law) < 2):
        return resWord
    elif len(law) == 2:
        for i in range(0, len(law[0])):
            for j in range(0, len(resWord)-len(law[0][i])+1):
                if matchSequences(resWord[j:len(law[0][i])+j], law[0][i]):
                    resSeq = setClearSequence(resWord[j:len(law[0][i])+j], law[0][i], law[1][i])
                    resWord = resWord.replace(resWord[j:len(law[0][i])+j], resSeq)
                    break
    elif len(law) == 3:
        for i in range(0, len(law[0])):
            for j in range(0, len(resWord)-len(law[0][i])+1):
                if matchSequences(resWord[j:len(law[0][i])+j], law[0][i]):
                    if matchCondition(law[2][0], law[2][1], resWord, j, law[0][i]):
                        resSeq = setClearSequence(resWord[j:len(law[0][i])+j], law[0][i], law[1][i])
                        resWord = resWord[:j]+resWord[j:len(law[0][i])+j].replace(resWord[j:len(law[0][i])+j], resSeq)+resWord[len(law[0][i])+j:]
                        
                        break
                
    else:
        return resWord
    return resWord

#to set certain characters of wildcards in resulting sequence
def setClearSequence(srcSeq, srcLaw, resLaw):
    global phonemes
    k = 0
    res = resLaw
    for i in range(0, len(srcLaw)):
        #if 65 <= ord(srcLaw[i]) <= 90:
        if srcLaw[i] in phonemes.keys():
             k = res.find(srcLaw[i])
             if k > -1:
                 res = res.replace(res[k], srcSeq[i])
    return res

#to set meanings from language B to words from language A
def setMeanings(maxHomonyms, dictFile):
    global words, semes, yd
    sw = open(dictFile+".txt", 'wt', encoding='utf-8')
    freqsHoms = []
    for i in range(0, maxHomonyms):
        freqsHoms.append(yd.borodProb(maxHomonyms, i+1))
    #print(freqsHoms)
    for i in range(0, len(words)):
        hs = yd.randomGen(freqsHoms) + 1
        #print(yd.randomGen(freqsHoms))
        homs = []
        sw.write(words[i]+" - ")
        j = 0
        while j < hs:
            k = random.randint(0, len(semes)-1)
            if not semes[k] in homs:
                homs.append(semes[k])
                if j < hs - 1:
                    sw.write(semes[k]+", ")
                else:
                    sw.write(semes[k])
                j += 1
        sw.write('\n')

#command line executer
def command_exec(cmd):
    global words, phonemes, filename, exceptions, soundChanges, yd, phonemeRanks, semes
    params = cmd.split()
    if params == []:
        print("Phonemes:")
        print(phonemes)
        print("\nForbidden clusters:")
        print(exceptions)
        print("\nPhonological rules:")
        print(soundChanges)
        print("\nRanks:")
        print(phonemeRanks)

    elif params[0] == "exit":
        running = False

    elif params[0] == "gen":
        words = []
        if len(params) == 2:
            generate_words(params[1], phonemes)
        elif len(params) == 3:
            generate_words(params[1], phonemes, params[2])
        else:
            print("! Error, can't generate words")

        for i,w in enumerate(words):
            if i==0 or i%10:
                print(w+" ", end='')
            else:
                print(w+"\n", end='')
        print()

    elif params[0] == "set":
        #pars = 0
        if params[1] == "ph" and len(params) == 4:
            phonemes[params[2]] = params[3].split(',')
            phonemeRanks[params[2]] = []
            freq = 0
            i = 0
            while i < len(phonemes[params[2]]):
                freq = yd.borodProb(len(phonemes[params[2]]), random.randint(1, len(phonemes[params[2]])))
                if not freq in phonemeRanks[params[2]]:
                    phonemeRanks[params[2]].append(freq)
                    i += 1
                
        elif params[1] == "ex" and len(params) > 2:
            i = 2
            while i < len(params):
                if not params[i] in exceptions:
                    exceptions.append(params[i])
                else:
                    exceptions.remove(params[i])
                i += 1
        elif params[1] == "rule" and len(params) > 2:
            rule = ""
            for i in range(2, len(params)):
                rule += params[i]
            if not rule in soundChanges:
                soundChanges.append(rule)
            else:
                soundChanges.remove(rule)
        elif params[1] == "words" and len(params) > 2:
            for i in range (2, len(params)):
                if not params[i] in words:
                    words.append(params[i])
                else:
                    words.remove(params[i])
        elif params[1] == "rank" and len(params) == 5:
            phs = params[3].split(',')
            phr = params[4].split(',')
            for i in range(0, len(phr)):
                if int(phr[i]) < 1:
                    print("! Error, ranks must be greater or equal to 1")
                    phr = {}
                    phs = {}
                    break
                else:
                    phr[i] = yd.borodProb(len(phr), int(phr[i]))
            if len(phs) == len(phr):
                phonemes[params[2]] = phs
                phonemeRanks[params[2]] = phr
            else:
                print("! Error, number of phonemes must be equal to number of ranks")
            
        else:
            print("! Error, can't execute a command")

        

    elif params[0] == "savewords":
        if len(params) == 2:
            sw = open(params[1]+".txt", 'wt', encoding="utf-8")
            for i,w in enumerate(words):
                if i==0 or i%10:
                    sw.write(w+' ')
                else:
                    sw.write(w+'\n')
    elif params[0] == "loadwords":
        if len(params) == 2:
            f = open(params[1]+".txt", 'rt', encoding="utf-8")
            inp = f.read()
            words = inp.split()
    elif params[0] == "prwords":
        for i,w in enumerate(words):
            if i==0 or i%10:
                print(w, end=" ")
            else:
                print(w)
        print()

    elif params[0] == "phshift":
        if len(params) == 1:
            for i in range(0, len(words)):
                for j in range(0, len(soundChanges)):
                    words[i] = proceedChange(words[i], soundChanges[j])
        elif len(params) == 2:
            if len(parsePhNotation(params[1])) == 0:
                for i in range(0, len(soundChanges)):
                    params[1] = proceedChange(params[1], soundChange[i])
                if not params[1] in words:
                    words.append(params[1])
                else:
                    words.remove(params[1])
            elif len(parsePhNotation(params[1])) > 1:
                for i in range(0, len(words)):
                    words[i] = proceedChange(words[i], params[1])
        elif len(params) > 2:
            rule = ""
            for i in range(2, len(params)):
                rule += params[i]
            params[1] = proceedChange(params[1], rule)
            if not params[1] in words:
                    words.append(params[i])
            else:
                    words.remove(params[i])

    elif params[0] == "setmeaning":
        if len(params) == 4:
            sr = open(params[1]+".txt", "rt", encoding="utf-8")
            inp = sr.read()
            semes = inp.split()
            setMeanings(int(params[3]), params[2])
        
    elif params[0] == "reset":
        phonemes = {}
        exceptions = []
        soundChanges = []
        phonemeRanks = {}

    elif params[0] == "save":
        if (len(params) == 2):
            filename = params[1]
            with open(filename, 'w') as outfile:
                json.dump([phonemes, exceptions, soundChanges, phonemeRanks], outfile)
        else:
            print("! Error, can't save a file")

    elif params[0] == "load":
        if (len(params)==2):
            
            filename = params[1]
            with open(filename, 'r') as data:    
                file = json.load(data)
                phonemes = file[0]
                exceptions = file[1]
                soundChanges = file[2]
                phonemeRanks = file[3]
        else:
            print("! Error, can't load a file")

    elif params[0] == "help":
        print("set ph <typeOfPhoneme> <phonemes> - set class of phonemes typed with a single string (ranks are randomly generted);")
        print("set ex <exception1> [exception2] [exception3] ... [exceptionN] - add/remove forbidden phonemic sequences;")
        print("set rule <soundChange> - add/remove a phonological rule")
        print("(with notation A>B/X_Y, where A - is a source sound(s), B - is a result sound(s), X - a preceding environment, Y - a following environment)")
        print("set words <word1> [word2] ... [wordN] - add/remove word(s)")
        print("set rank <typeOfPhoneme> <phonemes> <ranks> - set phonemic inventory with certain ranks")
        print("reset - reset phonemic invertory;")
        print("load <filename> - load phonemic inventory, exceptions and sound changes from afile;")
        print("save <filename> - save phonemic inventory, exceptions and sound changes to a file;")
        print("gen <phonemicPattern> [amountOfWords] - generate words;")
        print("phshift [word] [soundChange] - change word list with phonological rules or a certain word with certain rule")
        print("savewords <filename> - save wordlist to file;")
        print("loadwords <filename> - load wordlist from a file")
        print("prwords - show wordlist")
        print("setmeaning - <fileOfWordsFromLangB> <resultingFile> <maxHomonyms>")
        print("exit - close program")
    



print("This is a word generator for your conlang :3\nType 'help' for additional info\n")
while running:
    command = input(">> ")
    command_exec(command)
