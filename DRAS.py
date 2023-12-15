import PyPDF2
import string
import time
from num2words import num2words
from hyphen import Hyphenator


pdfFileObj = open('LSE.pdf', 'rb')
pdfReader = PyPDF2.PdfReader(pdfFileObj)


class Reader:

    # def __init__(self, pdf_path):
        # self.pdfReader = PdfReader(pdf_path)
        # pdfFileObj = open(pdf_path, 'rb')
        # pdfReader = PyPDF2.PdfReader(pdfFileObj)
    
    def putInMap(self):
        mem = {}
        f = open("dictionary.csv", "r")
        for x in f:
            commaIndex = self.findComma(x)
            mem[x[0:commaIndex]] = x[commaIndex+1:len(x)]
        return mem
    
    def findComma(self, words):
        for i in range(len(words)):
            if words[i] == ',':
                return i
        return -1

    
    def overAllDocWords(self):
        start = 0
        end = len(pdfReader.pages)
        # print(end)
        totalWords = 0

        for i in range(end):
            pageObj = pdfReader.pages[i]
            text = pageObj.extract_text()
            totalWords += len(text.split())
            # print(totalWords)
        pdfFileObj.close()

        return totalWords

    def countWords(self, start, end):
        length = (end - start) + 1
        start -= 1
        pageCount = start
        totalWords = 0
        
        for i in range(length):
            pageObj = pdfReader.pages[pageCount]
            text = pageObj.extract_text()
            # print(text)
            pageCount += 1

            totalWords += len(text.split())

        return totalWords
        
    def getInput(self, question):
        while True:
            inp = input(question)
            if self.can_convert_to_int(inp):
                inp = int(inp)
                return inp
        

    def main(self):
        t = time.time()

        startCM = self.getInput("Input chairmans statement starting point")
        endCM = self.getInput("Input chairmans statement ending point")
        startPH = self.getInput("Input Performance Highlights starting point")
        endPH = self.getInput("Input Performance Highlights ending point")
        startCG = self.getInput("Input Corporate Governments starting point")
        endCG = self.getInput("Input Corporate GOvernments ending point")
        startESG = self.getInput("Input ESG section starting point")
        endESG = self.getInput("Input ESG section ending point")
        
        print("\nChairmans statment words = " + str(self.countWords(startCM, endCM)))
        print("performance highlights words = " + str(self.countWords(startPH, endPH)))
        print("Corporate Governments words = " + str(self.countWords(startCG, endCG)))
        print("ESG words = " + str(self.countWords(startESG, endESG)))
        print("Overall Document words = " + str(self.overAllDocWords()))

        print("\nSentiment of all file:")
        self.sentiment()

        print("\nGunning Fox:")
        print("Gunning Fox for Chairman = " + str(self.gunningFox(startCM, endCM)))
        print("Gunning Fox for Performance Highlights = " + str(self.gunningFox(startPH, endPH)))
        print("Gunning Fox for Corporate Governemnts = " + str(self.gunningFox(startCG, endCG)))
        print("Gunning Fox for ESG = " + str(self.gunningFox(startESG, endESG)))


        t = time.time() - t
        print("\nTime taken to run = " + str(t))

    def gunningFox(self, start, end):
        length = (end - start) + 1
        start -= 1
        pageCount = start
        totalWords = 0
        totalSentences = 0
        compWords = 0
        
        for i in range(length):
            pageObj = pdfReader.pages[pageCount]
            text = pageObj.extract_text()
            textArray = text.split()
            totalWords += len(textArray)
            totalSentences += self.findSentences2(textArray)
            compWords += self.findCompWords(textArray)
            print("Page " + str(pageCount+1) + ": total words = " + str(totalWords) + " total sentences = " + str(totalSentences) + " comp words = " + str(compWords))

            pageCount += 1
            
        if totalSentences > 0 and totalWords > 0:
            return 0.4*((totalWords/totalSentences)+(100*(compWords/totalWords)))
        return -1


    def findSentences2(self, textArray):
        sentences = 0
        for words in range(len(textArray)):
            index = self.findMarks(textArray[words])
            if index != -1 and (index == len(textArray[words]) - 1 or (textArray[words][index+1] != None and not self.can_convert_to_int(textArray[words][index+1]))):
                sentences += 1
                # print(textArray[words])
        return sentences

    def findMarks(self, word):
        for letter in range(len(word)):
            if word[letter] == "." or word[letter] == "!":
                return letter
        return -1

    def can_convert_to_int(self, s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    def can_convert_to_float(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

        
    def findCompWords(self, textArray):
        textArray2 = [None] * len(textArray)
        compWords = 0
        translator = str.maketrans('', '', string.punctuation)
        for i in range(len(textArray)):
            textArray2[i] = textArray[i].translate(translator).lower()
            textArray2[i] = ''.join(textArray2[i].split())
            if self.count_syllables5(textArray2[i]) >= 3:
                compWords += 1
                # print(textArray2[i])
        return compWords


    def count_syllables5(self, word):
        if self.can_convert_to_int(word) or self.can_convert_to_float(word):
            word = num2words(word)
        if len(word) > 50:
            return 3
        h = Hyphenator('en_US')
        syllables = h.syllables(word)
        return len(syllables)
        
    def sentiment(self):
        mem = self.putInMap()
        posWords = 0
        negWords = 0
        uncWords = 0
        strongMWords = 0
        weakMWords = 0
        litWords = 0
        conWords = 0
        
        translator = str.maketrans('', '', string.punctuation)

        for i in range(len(pdfReader.pages)):
            pageObj = pdfReader.pages[i]
            text = pageObj.extract_text()
            textArray = text.split()
            for word in range(len(textArray)):
                textArray[word] = textArray[word].translate(translator).lower()
                textArray[word] = ''.join(textArray[word].split())
                if textArray[word] in mem:
                    # cat = mem[textArray[word]]
                    cat = ''.join(mem[textArray[word]].split())
                    # print(textArray[word] + " cat = " + cat)
                    match cat:
                        case "Negative":
                            negWords += 1
                        case "Positive":
                            posWords += 1
                        case "Uncertainty":
                            uncWords += 1
                        case "Litigious":
                            litWords += 1
                        case "StrongModal":
                            strongMWords += 1
                        case "WeakModal":
                            weakMWords += 1
                        case "Constraining":
                            conWords += 1
                    
                            
        print("Positive words = " + str(posWords))
        print("Negative words = " + str(negWords))
        print("Uncertainty words = " + str(uncWords))
        print("Strong Modal words = " + str(strongMWords))
        print("Weak Modal words = " + str(weakMWords))
        print("Litigious words = " + str(litWords))
        print("Constraining words = " + str(conWords))
        # print(textArray)
                        
                    
    

r = Reader()
r.main()