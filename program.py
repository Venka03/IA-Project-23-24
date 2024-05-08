from MFIS_Read_Functions import *
import skfuzzy as skf
import copy


def fuzzyValue(val: int, fuzzyset: FuzzySet) -> int:
    if val > fuzzyset.x[-1]:
        return fuzzyset.y[-1]
    index = np.where(fuzzyset.x == val)
    if index[0].size == 0:
        print(val, fuzzyset.var)
        raise "ERROR: wrong fuzzy input variable"
    return fuzzyset.y[index[0][0]]


def main():
    fuzzySetsDict = readFuzzySetsFile("InputVarSets.txt")
    rules = readRulesFile()
    applicationList = readApplicationsFile()  # store for each member it's value and compute their risk
    i = 0
    for applicant in applicationList:  # take every application
        variables = []
        for data in applicant.data:  # go through their data to calculate risk
            for key in fuzzySetsDict.keys():
                if data[0] == fuzzySetsDict[key].var:
                    fuzzySetsDict[key].memDegree = fuzzyValue(int(data[1]), fuzzySetsDict[key])
                    if fuzzySetsDict[key].memDegree:  # not zero
                        variables.append([fuzzySetsDict[key].var + "=" + fuzzySetsDict[key].label,
                                          fuzzySetsDict[key].memDegree])     # not zero]
        userRules = []
        if i == 1:
            # fuzzySetsDict.printFuzzySetsDict()
            for rule in rules:
                strength = 1
                validRule = 1
                for elem in rule.antecedent:    # check which rules are satisfied
                    found = 0
                    for var in variables:
                        if elem == var[0]:      # decrease the strength of the rule if necessary
                            found = 1
                            strength = min(strength, var[1])
                            break
                    if found == 0:
                        validRule = 0
                        break
                if validRule == 1:
                    rule.strength = strength
                    userRules.append(rule)
                    rule.printRule()
        i += 1

        #  print(data[0], data[1])
    print("\n-----------------------")
    #  fuzzySetsDict.printFuzzySetsDict()


if __name__ == "__main__":
    main()
