__author__ = 'joshkang'

#this program uses data from the 1984 Congressional Voting Record
#and uses the 'votes.dta' file
#Democrats are the positive class in this implementation and Republicans are negative
import random
import math

class Cond:

    def __init__(self, name=None, value=None, index = None):
        self.name = name
        self.value = value
        self.index = index

class Rule:
    def __init__(self, cond = None):
        self.cond = []

        if cond is not None:
            self.cond.append(cond)

    def addCond(self, cond):
        self.cond.append(cond)

    def removeCond(self):
        self.cond.pop()

    #if all conditions of Rule is met, returns True
    def isPos(self, vote):
        for c in self.cond:
            if vote[c.index] != c.value:
                return False
        return True

    def evaluate(self, posSet, negSet):
        result = []
        posCount = 0.0
        negCount = 0.0

        for vote in posSet:
            if self.isPos(vote):
                posCount +=1
        #rule can only become a rule once it covers no neg examples in growrule
        #therefore the rule should not match any of the neg examples
        #once it has been created
        for vote in negSet:
            if not self.isPos(vote):
                negCount +=1


        posAccuracy = posCount / len(posSet)
        negAccuracy = negCount / len(negSet)
        accuracy = (posCount + negCount) / (len(posSet) + len(negSet))


        result.append(accuracy)
        result.append(posAccuracy)
        result.append(negAccuracy)
        return result

    def __str__(self):
        rule = ""

        for c in self.cond:
            rule += "%s: %s \n" %(c.name, c.value)

        return rule


class Rules:
    def __init__(self, rule = None):
        self.rules = []

        if rule is not None:
            self.rules.append(rule)
    def addRule(self, rule):
        self.rules.append(rule)

    def evaluate(self, test):
        result = []
        accuracy = 0.0
        posCount = 0.0
        negCount = 0.0


        for vote in test.votes:
            pos = None
            for rule in self.rules:

               pos = rule.isPos(vote)

                #if the rules predict positive AND the vote was actually positive set
               if pos == True and vote in test.pos:
                   posCount+=1
                   break
            #if failed every rule (predicted negative) AND vote is in negative set
            if pos == False and vote in test.neg:
                negCount+=1


        accuracy = (posCount + negCount) / len(test.votes)
        result.append(accuracy)
        result.append(posCount / len(test.pos))
        result.append(negCount / len(test.neg))
        return result

    def __str__(self):

        allRules = "RuleSet \n"
        count = 1
        for rule in self.rules:
            allRules += "%r. \n%s" %(count, rule)
            count +=1
        return allRules



class Dataset:

    def __init__(self):
        self.votes = []
        self.pos = []
        self.neg = []

    def addVotes(self, example):
        self.votes.append(example)

    def addPos(self, example):
        self.pos.append(example)

    def addNeg(self, example):
        self.neg.append(example)

    def load(self, filename):

        with open(filename, "r") as f:

            line = f.readline().strip() #name of data set
            line = int(f.readline().strip())

            #passes number of classes & classes
            for i in range(0, line):
                line = f.readline().strip()

            #number of rules
            line = int(f.readline().strip())

            for i in range(0, line):
                line = f.readline().strip()

            #number of values
            line = int(f.readline().strip())

            #passes number of values & values
            for i in range(0, line):
                line = f.readline().strip()


            #number of democrats
            line = int(f.readline().strip())

            #inputs dem votes as pos
            for i in range(0, line):
                line = f.readline().strip().replace(' ', '')
            
                self.addPos(line)
                self.addVotes(line)

            #number of republicans
            line = int(f.readline().strip())

            #inputs rep votes as neg
            for i in range(0, line):
                line = f.readline().strip().replace(' ', '')

                self.addNeg(line)
                self.addVotes(line)




    def split(self, rand):
        train = Dataset()
        test = Dataset()
        partition = []
        count = 0

        for example in self.votes:
            #keep track of all pos/neg examples added to train to help with testing
            if random.random() <= rand:
                if count < len(self.pos):
                    train.addPos(example)
                else:
                    train.addNeg(example)

                train.addVotes(example)
            else:
                if count < len(self.pos):
                    test.addPos(example)
                else:
                    test.addNeg(example)

                test.addVotes(example)
            count +=1

        partition.append(train)
        partition.append(test)
        return partition

def irep(train):

    posSet = []
    negSet = []


    #input pos and neg
    for pos in train.pos:
        posSet.append(pos)

    for neg in train.neg:
        negSet.append(neg)

    ruleSet = Rules()

    while posSet != []:
        
        rule = growRule(posSet, negSet)

        accuracy = rule.evaluate(posSet, negSet)
        error = 1 - accuracy[0]

        if error > 0.5:
            return ruleSet

        else:
            ruleSet.addRule(rule)

            newSet = []
            
            #remove all votes covered by new rule from posSet
            for vote in posSet:
                if (not rule.isPos(vote)):
                    newSet.append(vote)
        
            posSet = newSet
        

    return ruleSet

def generateRules(filename):

    allRules = Rule()
    rules = []

    with open(filename, "r") as f:

            line = f.readline().strip() #name of data set
            line = int(f.readline().strip())

            #passes number of classes & classes
            for i in range(0, line):
                line = f.readline().strip()

            #number of rules
            line = int(f.readline().strip())

            for i in range(0, line):
                line = f.readline().strip()
                rules.append(line)

    #keeps track of index of vote for corresponding voting issue
    index = 0

    #code that generates all 48 conditions possible from 16 rules and 3 values
    for rule in rules:

        for i in range(0, 3):
            if i == 0:
                condition = Cond(rule, 'y', index)
            elif i == 1:
                condition = Cond(rule, 'n', index)
            else:
                condition = Cond(rule, 'u', index)

            allRules.addCond(condition)

        index += 1

    return allRules

def growRule(posSet, negSet):
    newRule = Rule()

    #generates all 48 conditions possible from 16 rules and 3 values
    allRules = generateRules("votes.dta")


    #"everything is positive" therefore all pos and neg examples are covered
    #if the rule is empty
    p0 = len(posSet) * 1.0 #sets p0 to double datatype for log calculations
    n0 = len(negSet) * 1.0


    p1 = 0.0
    n1 = 0.0

    while(True):

        newCond = Cond()
        maxGain = None

        for cond in allRules.cond:

            tempP = 0.0
            tempN = 0.0

            #temporarily adds new condition to rule to calculate p1 and n1
            newRule.addCond(cond)

            #checks how many votes match rule from posSet
            for vote in posSet:

                if (newRule.isPos(vote)):
                    tempP+=1


            #checks how many votes match rule from negSet
            for vote in negSet:

                if (newRule.isPos(vote)):
                    tempN+=1


            #removes the new condition from current rule
            newRule.removeCond()


            #FOIL Information Gain
            gain = tempP * (math.log(((tempP + 1) / (tempP + tempN + 1)), 2) - (math.log(((p0 + 1) / (p0 + n0 + 1)), 2)))


            #found condition with most gain so far
            if gain > maxGain or maxGain is None:
                maxGain = gain
                newCond = cond
                p1 = tempP
                n1 = tempN



        #add the condition that had the max gain
        newRule.addCond(newCond)


        #set p0 and n0 to newest pos / neg examples covered by new rule
        p0 = p1
        n0 = n1

        #once rule no longer covers any negative examples
        if n0 == 0.0:
            break


    return newRule

def foil(rule, posSet, negSet, p0, n0):
    pass

def main():
    #python uses the system clock by default to set the seed
    random.seed()

    data = Dataset()
    data.load("votes.dta")


    partition = data.split(0.75)
    train = partition[0]
    test = partition[1]


    rules = irep(train)

    accuracy = rules.evaluate(test)

    print "ACCURACY: %0.1f" %(accuracy[0] * 100)
    print "POS ACCURACY: %0.1f" %(accuracy[1] * 100)
    print "NEG ACCURACY: %0.1f" %(accuracy[2] * 100)
    print ''
    print rules





if __name__ == '__main__':main()
