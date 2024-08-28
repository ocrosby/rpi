from scipy.stats import kendalltau, spearmanr
from sklearn.metrics import hamming_loss, mean_absolute_error
import numpy as np
import editdistance


def kendalls_tau(list1, list2):
    ranks1 = [rank for rank, _, _ in list1]
    ranks2 = [rank for rank, _ in list2]
    tau, _ = kendalltau(ranks1, ranks2)
    return tau


def spearmans_rank_correlation(list1, list2):
    ranks1 = [rank for rank, _, _ in list1]
    ranks2 = [rank for rank, _ in list2]
    rho, _ = spearmanr(ranks1, ranks2)
    return rho


def hamming_distance(list1, list2):
    ranks1 = [rank for rank, _, _ in list1]
    ranks2 = [rank for rank, _ in list2]
    return hamming_loss(ranks1, ranks2) * len(ranks1)


def borda_count(list1, list2):
    n = len(list1)
    borda1 = {team: n - rank for rank, team, _ in list1}
    borda2 = {team: n - rank for rank, team in list2}
    return sum(abs(borda1[team] - borda2[team]) for team in borda1)


def rank_biased_overlap(list1, list2, p=0.9):
    ranks1 = [team for _, team, _ in list1]
    ranks2 = [team for _, team in list2]
    overlap = 0
    for k in range(1, len(ranks1) + 1):
        overlap += len(set(ranks1[:k]) & set(ranks2[:k])) / k * (p ** (k - 1))
    return (1 - p) * overlap


def spearmans_footrule_distance(list1, list2):
    ranks1 = {team: rank for rank, team, _ in list1}
    ranks2 = {team: rank for rank, team in list2}
    return sum(abs(ranks1[team] - ranks2[team]) for team in ranks1)


def permutation_distance(list1, list2):
    ranks1 = [team for _, team, _ in list1]
    ranks2 = [team for _, team in list2]
    return sum(1 for i, team in enumerate(ranks1) if team != ranks2[i])


def mean_absolute_error_in_ranks(list1, list2):
    ranks1 = [rank for rank, _, _ in list1]
    ranks2 = [rank for rank, _ in list2]
    return mean_absolute_error(ranks1, ranks2)


def levenshtein_distance(list1, list2):
    ranks1 = [team for _, team, _ in list1]
    ranks2 = [team for _, team in list2]
    return editdistance.eval(ranks1, ranks2)


def normalized_kendalls_tau_distance(list1, list2):
    tau = kendalls_tau(list1, list2)
    return (1 - tau) / 2


if __name__ == '__main__':
    # Example usage
    list1 = [(1, 'Team A', 0.5), (2, 'Team B', 0.3), (3, 'Team C', 0.2)]
    list2 = [(1, 'Team B'), (2, 'Team A'), (3, 'Team C')]

    print("Kendall's Tau:", kendalls_tau(list1, list2))
    print("Spearman's Rank Correlation:", spearmans_rank_correlation(list1, list2))
    print("Hamming Distance:", hamming_distance(list1, list2))
    print("Borda Count:", borda_count(list1, list2))
    print("Rank Biased Overlap:", rank_biased_overlap(list1, list2))
    print("Spearman's Footrule Distance:", spearmans_footrule_distance(list1, list2))
    print("Permutation Distance:", permutation_distance(list1, list2))
    print("Mean Absolute Error in Ranks:", mean_absolute_error_in_ranks(list1, list2))
    print("Levenshtein Distance:", levenshtein_distance(list1, list2))
    print("Normalized Kendall's Tau Distance:", normalized_kendalls_tau_distance(list1, list2))
