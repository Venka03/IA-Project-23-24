from MFIS_Read_Functions import *


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


def main():
    fuzzySetsDict = readFuzzySetsFile("InputVarSets.txt")
    fuzzySetsRisks = readFuzzySetsFile("Risks.txt")
    rules = readRulesFile()
    applicationList = readApplicationsFile()  # store for each member it's value and compute their risk
    with open("Results.txt", "w") as file:  # open file using with is more save, as it closes automatically after exiting
        for request in applicationList:  # take every request
            for data in request.data:  # go through their data to calculate risk
                for key in fuzzySetsDict.keys():
                    if data[0] == fuzzySetsDict[key].var:
                        fuzzySetsDict[key].memDegree = fuzzyValue(data[1], fuzzySetsDict[
                            key])  # set membership degree for each fuzzy set

            scaling_coefficients = {key: 0 for key in fuzzySetsRisks.keys()}  # strengths of certain risk fuzzy set

            for rule in rules:
                # compute strength of each rule, even if it is 0, meaning that it is not applicable
                # they will not affect anyway, since later for coefficients the max is taken
                strength = 1
                for antecedent in rule.antecedent:
                    strength = min(fuzzySetsDict[antecedent].memDegree, strength)
                rule.strength = strength
                # compute coefficient for scaling for each risk
                scaling_coefficients[rule.consequent] = max(scaling_coefficients[rule.consequent], rule.strength)

            # get the composition using aggregation
            # if only one risk fuzzy set, then composition is just this risk scaled
            # else in is max values of each risk set
            first = True
            for key in fuzzySetsRisks.keys():
                if first:
                    # to have Xs values to use it later for computing centroid(Xs of each risk set are the same)
                    x = fuzzySetsRisks[key].x
                    composition = fuzzySetsRisks[key].y * scaling_coefficients[key]
                    first = False
                else:
                    composition = np.fmax(fuzzySetsRisks[key].y * scaling_coefficients[key], composition)

            area = np.trapz(composition, x=x)
            if not area:
                raise "Error in execution or fuzzy logic"
            centroid_x = np.trapz(x * composition, x=x) / area
            file.write(f"{request.appId}, {centroid_x}\n")

        print("Saved to filed")


if __name__ == "__main__":
    main()
