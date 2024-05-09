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
    fuzzySetsRisks = readFuzzySetsFile("Risks.txt")
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
            low = 0
            medium = 0
            high = 0

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
                    if rule.consequent == "Risk=HighR":
                        high = max(high, rule.strength)
                    if rule.consequent == "Risk=MediumR":
                        medium = max(medium, rule.strength)
                    if rule.consequent == "Risk=LowR":
                        low = max(low, rule.strength)

            fuzzySetsRisks["Risk=LowR"].y *= low
            fuzzySetsRisks["Risk=MediumR"].y *= medium
            fuzzySetsRisks["Risk=HighR"].y *= high

            """
                    for key in fuzzySetsRisks:
                        if rule.consequent == fuzzySetsRisks[key].var + "=" + fuzzySetsRisks[key].label:
                            fuzzySetsRisks[key].memDegree = rule.strength
                            fuzzySetsRisks[key].y *= fuzzySetsRisks[key].memDegree
            """

            #aggreg = np.fmax(fuzzySetsRisks.values[0].y, np.fmax(fuzzySetsRisks.values[1].y, fuzzySetsRisks.values[2].y))
            aggreg = np.fmax(fuzzySetsRisks["Risk=LowR"].y, fuzzySetsRisks["Risk=MediumR"].y)
            aggreg = np.fmax(fuzzySetsRisks["Risk=HighR"].y, aggreg)
            #  aggreg = skf.maxmin_composition(fuzzySetsRisks.values[0].x, fuzzySetsRisks.values[0].y, fuzzySetsRisks.values[0].x, fuzzySetsRisks.values[1].y)
            #  aggreg = skf.maxmin_composition(fuzzySetsRisks.values[0].x, aggreg, fuzzySetsRisks.values[0].x,  fuzzySetsRisks.values[2].y)


            plt.plot(fuzzySetsRisks["Risk=LowR"].x, fuzzySetsRisks["Risk=LowR"].y, label='MF 1')
            plt.plot(fuzzySetsRisks["Risk=MediumR"].x, fuzzySetsRisks["Risk=MediumR"].y, label='MF 2')
            plt.plot(fuzzySetsRisks["Risk=HighR"].x, fuzzySetsRisks["Risk=HighR"].y, label='MF 3')
            plt.plot(fuzzySetsRisks["Risk=LowR"].x, aggreg, label='Aggregated MF', linestyle='--')
            plt.xlabel('x')
            plt.ylabel('Membership degree')
            plt.title('Aggregation using max')
            plt.legend()
            plt.show()



        i += 1

        #  print(data[0], data[1])
    print("\n-----------------------")
    #  fuzzySetsDict.printFuzzySetsDict()


if __name__ == "__main__":
    main()
