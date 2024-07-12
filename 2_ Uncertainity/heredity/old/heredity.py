import csv
import itertools
import sys

PROBS: dict[str, dict | str] = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename) -> dict[str, str | None | bool]:
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people: dict[str], one_gene: set[str], two_genes: set[str], have_trait: set[str]) -> float:
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    ma = 1
    for person in people:
        num_genes = 2 if person in two_genes else 1 if person in one_gene else 0
        ma *= PROBS["gene"][num_genes]

        if people[person]["trait"] is None:
            mother = people[person]["mother"]
            father = people[person]["father"]
            if not mother:
                ma *= PROBS["trait"][num_genes][person in have_trait]
                continue

            # Else: he has parents
            # we know num_genes already, we want to know ...
            father_genes = 2 if father in two_genes else 1 if father in one_gene else 0
            mother_genes = 2 if mother in two_genes else 1 if mother in one_gene else 0
            
            
            continue

        if person in have_trait:
            match people[person]["trait"]:
                case False: return 0
                case True: pass
                # case None: ma *= PROBS["trait"][num_genes][True]
        else:
            match people[person]["trait"]:
                case True: return 0
                case False: pass
                # case None: ma *= PROBS["trait"][num_genes][False]

    return ma

class get_prob():

    @staticmethod
    def wanted(a: bool, b: bool) -> float:
        """ a and b are infected genes of parent"""
        return (((1-PROBS["mutation"]) if a else PROBS["mutation"]) +
                ((1-PROBS["mutation"]) if b else PROBS["mutation"]))/2

    @staticmethod
    def mut(self_genes: int, parent_genes: int):
        assert self_genes in (0, 2)
        """
        for mut 0:
        if father 0:  1-mutation = 0.5*1*(1-mutation) + 0.5*1*(1-mutation)
        if father 1:  0.5*1*(1-mutation) + 0.5*1*mutaion
        if father 2:  mutation = 0.5*1*mutation + 0.5*1*mutaion
        """
        a, b = parent_genes >= 1, parent_genes >= 2
        return get_prob.wanted(not a, not b) if self_genes == 0 else get_prob.wanted(a, b)

    @staticmethod
    def mut1(mother_genes: int, father_genes: int):
        # father and not mother, or viceversa
        pr = 1
        for parent_genes in (mother_genes, father_genes):
            a, b = parent_genes >= 1, parent_genes >= 2
            pr *= get_prob.wanted(a, b)
        return pr

def update(probabilities, one_gene: set[str], two_genes: set[str], have_trait: set[str], p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        num_genes = 2 if person in two_genes else 1 if person in one_gene else 0
        probabilities[person]["gene"][num_genes] += p
        probabilities[person]["trait"][person in have_trait] += p


def normalize(probabilities: dict[str, dict[str, dict]]):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """

    for node in probabilities.values():
        for child in node.values():
            su = sum(child.values())
            for key in child:
                child[key] /= su


if __name__ == "__main__":
    main()

"""def joint_probability(people: dict[str], one_gene: set[str], two_genes: set[str], have_trait: set[str]) -> float:

    ma = 1
    person_prob = 1
    for person in people:
        ma *= person_prob
        person_prob = 1
        num_genes = 2 if person in two_genes else 1 if person in one_gene else 0
        # person_prob *= PROBS["gene"][num_genes]
        person_prob *= PROBS["trait"][num_genes][person in have_trait]
        if people[person]["trait"] is not None:
            # printd("trait",num_genes, people[person]["trait"],sep=" : ")
            if people[person]["trait"] != (person in have_trait):
                return 0
        elif people[person]["trait"] is None and not people[person]["mother"]:
            person_prob *= PROBS["gene"][num_genes]
            person_prob *= PROBS["trait"][num_genes][person in have_trait]
            # printd("parent",num_genes,people[person]["mother"],sep=" : ")
        else:
            mother = people[person]["mother"]
            father = people[person]["father"]

            father_genes = 2 if father in two_genes else 1 if father in one_gene else 0
            mother_genes = 2 if mother in two_genes else 1 if mother in one_gene else 0
            person_prob *= PROBS["gene"][father_genes]
            person_prob *= PROBS["gene"][mother_genes]
            printd(f"no trait, no parent : M:{mother_genes} ,F:{father_genes}")
            if num_genes in [0, 2]:
                # if father 0:  1-mutation = 0.5*1*(1-mutation) + 0.5*1*(1-mutation)
                # if father 1:  0.5*1*(1-mutation) + 0.5*1*mutaion
                # if father 2:  mutation = 0.5*1*mutation + 0.5*1*mutaion
                # muatate and no mutate
                person_prob *= get_prob.mut(num_genes, father_genes)
                person_prob *= get_prob.mut(num_genes, mother_genes)

            elif num_genes == 1:  # yes father no mother
                person_prob *= get_prob.mut1(mother_genes=mother_genes,
                                             father_genes=father_genes)
    ma *= person_prob
    return person_prob


class get_prob():

    @staticmethod
    def wanted(a: bool, b: bool) -> float:
        " a and b are infected genes of parent"
        return (((1-PROBS["mutation"]) if a else PROBS["mutation"]) +
                ((1-PROBS["mutation"]) if b else PROBS["mutation"]))/2

    @staticmethod
    def mut(self_genes: int, parent_genes: int):
        assert self_genes in (0, 2)
        
        a, b = parent_genes >= 1, parent_genes >= 2
        return get_prob.wanted(not a, not b) if self_genes == 0 else get_prob.wanted(a, b)

    @staticmethod
    def mut1(mother_genes: int, father_genes: int):
        # father and not mother, or viceversa
        pr = 0
        for parent_genes in (mother_genes, father_genes):
            a, b = parent_genes >= 1, parent_genes >= 2
            pr += get_prob.wanted(a, b)
        return pr
"""