import math


class SummarizeCoco():
    def __init__(self):
        saya = "Wkwkwkwkw"
        print(saya)

    def computeTF(self, wordDict, Bow):
        tfDict = {}
        bowCount = len(Bow)
        for word, count in wordDict.items():
            tfDict[word] = count / float(bowCount)
        return tfDict

    def computeIDF(self, docList, inDict):
        idfDict = inDict
        N = len(docList)
        idfDict = dict.fromkeys(docList[0].keys(), 0)
        for doc in docList:
            for word, val in doc.items:
                if val > 0:
                    idfDict[word] += 1

        for word, val in idfDict.items():
            idfDict[word] = math.log10(N / float(val))
        return idfDict

    def computeTFIDF(self, tfBow, idfs):
        tfidf = {}
        for word, val in tfBow.items:
            tfidf[word] = val * idfs[word]
        return tfidf
