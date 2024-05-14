from MFIS_Read_Functions import *
import skfuzzy as skf
import copy
'''
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('TkAgg')  # for pycharm on mac
'''


def fuzzyValue(val: int, fuzzySet: FuzzySet) -> float:
    """
    compute membership degree having fuzzy set and input variable
    """
    if val > fuzzySet.x[-1]:
        return fuzzySet.y[-1]
    index = np.where(fuzzySet.x == val)
    if index[0].size == 0:
        print(val, fuzzySet.var)
        raise "ERROR: wrong fuzzy input variable"
    return fuzzySet.y[index[0][0]]


def computeScalingCoef(rules: RuleList, fuzzySets: FuzzySet) -> tuple[int, int, int]:
    low = 0
    medium = 0
    high = 0
    for rule in rules:
        strength = 1
        validRule = True
        for antecedent in rule.antecedent:  # check which rules are satisfied
            found = 0
            for set in fuzzySets:
                print(set)
                if antecedent == set[0]:  # if fuzzy set is in antecedent
                    found = 1
                    strength = min(strength, set[1])  # the strength is the minimum value of antecedent of rule
                    break
            if found == 0:  # if none of applicants non zero fuzzy sets are in antecedent, then rule is not applicable
                validRule = False
                break
        if validRule:
            rule.strength = strength
            if rule.consequent == "Risk=HighR":
                high = max(high, rule.strength)  # compute coefficient for scaling rule of hight risk
            if rule.consequent == "Risk=MediumR":
                medium = max(medium, rule.strength)  # compute coefficient for scaling rule of medium risk
            if rule.consequent == "Risk=LowR":
                low = max(low, rule.strength)  # compute coefficient for scaling rule of low risk
    


def main():
    fuzzySetsDict = readFuzzySetsFile("InputVarSets.txt")
    fuzzySetsRisks = readFuzzySetsFile("Risks.txt")
    rules = readRulesFile()
    applicationList = readApplicationsFile()  # store for each member it's value and compute their risk
    print(len(fuzzySetsRisks))
    print(fuzzySetsRisks.keys())
    file = open("Results.txt", "w")

    for applicant in applicationList:  # take every application
        nonZeroFuzzySets = []
        for data in applicant.data:  # go through their data to calculate risk
            for key in fuzzySetsDict.keys():
                if data[0] == fuzzySetsDict[key].var:
                    fuzzySetsDict[key].memDegree = fuzzyValue(int(data[1]), fuzzySetsDict[key])
                    if fuzzySetsDict[key].memDegree:  # not zero
                        nonZeroFuzzySets.append([fuzzySetsDict[key].var + "=" + fuzzySetsDict[key].label,
                                          fuzzySetsDict[key].memDegree])
        
        scaling_coefficients = {key: 0 for key in fuzzySetsRisks.keys()}

        for rule in rules:
            strength = 1
            validRule = True
            for antecedent in rule.antecedent:  # check which rules are satisfied
                found = False
                for set in nonZeroFuzzySets:
                    if antecedent == set[0]:  # if fuzzy set is in antecedent
                        found = True
                        strength = min(strength, set[1])  # the strength is the minimum value of antecedent of rule
                        break
                if not found:  # if none of applicants non zero fuzzy sets are in antecedent, then rule is not applicable
                    validRule = False
                    break
            if validRule:
                rule.strength = strength
                # compute coefficient for scaling for each risk
                scaling_coefficients[rule.consequent] = max(scaling_coefficients[rule.consequent], rule.strength)

        # get the aggregation
        # if only one risk fuzzy set, then aggregation is just this risk scaled
        # else in is max values of each risk set
        first = True
        
        for key in fuzzySetsRisks.keys():
            if first:
                # to have at least one key to use it later for computing centroid, since size of Xs of each risk set is the same
                k = key
                aggregation = fuzzySetsRisks[key].y * scaling_coefficients[key]
                first = False
            else:
                aggregation = np.fmax(fuzzySetsRisks[key].y * scaling_coefficients[key], aggregation)

        area = np.trapz(aggregation, x=fuzzySetsRisks[k].x)
        centroid_x = np.trapz(fuzzySetsRisks[k].x * aggregation, x=fuzzySetsRisks[k].x) / area
        file.write(f"{applicant.appId}, {centroid_x}\n")

    print("\nSaved to filed")
    file.close()


if __name__ == "__main__":
    main()
