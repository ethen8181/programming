import heapq
import numpy as np


def calib_recommend_celf(items, interacted_distr, topn, lmbda=0.5):
    # python's heap is a min-heap
    upper_bounds = []
    for item in items:
        utility, total_score, kl_div = compute_utility([item], interacted_distr, lmbda=0.5)
        heapq.heappush(upper_bounds, (-utility, item))

    utility, item = heapq.heappop(upper_bounds)
    calib_reco = [item]
    utility = -utility
    utilities = [utility]

    while len(calib_reco) < topn and upper_bounds:

        matched = False
        while not matched:

            _, current_item = heapq.heappop(upper_bounds)
            new_utility, total_score, kl_div = compute_utility(
                calib_reco + [current_item], interacted_distr, lmbda=0.5)
            utility_gain = new_utility - utility
            heapq.heappush(upper_bounds, (-utility_gain, current_item))

            _, item = upper_bounds[0]
            matched = item == current_item

        utility_gain, item = heapq.heappop(upper_bounds)
        utility -= utility_gain
        utilities.append(utility)
        calib_reco.append(item)

    return {'reco': calib_reco, 'utilities': utilities}


def calib_recommend_greedy(items, interacted_distr, topn, lmbda=0.5):
    """
    start with an empty recommendation list,
    loop over the topn cardinality, during each iteration
    update the list with the item that maximizes the utility function.
    """
    utilities = []
    total_scores = []
    kl_divs = []

    calib_reco = []
    for _ in range(topn):
        best_utility = -np.inf
        for item in items:
            if item in calib_reco:
                continue

            utility, total_score, kl_div = compute_utility(
                calib_reco + [item], interacted_distr, lmbda)
            if utility > best_utility:
                best_total_score = total_score
                best_kl_div = kl_div
                best_utility = utility
                best_item = item

        kl_divs.append(best_kl_div)
        total_scores.append(best_total_score)
        utilities.append(best_utility)

        calib_reco.append(best_item)

    return {'reco': calib_reco, 'utilities': utilities,
            'total_scores': total_scores, 'kl_divs': kl_divs}


def compute_utility(reco_items, interacted_distr, lmbda=0.5):
    """
    Our objective function for computing the utility score for
    the list of recommended items.

    lmbda : float, 0.0 ~ 1.0, default 0.5
        Lambda term controls the score and calibration tradeoff,
        the higher the lambda the higher the resulting recommendation
        will be calibrated. Lambda is keyword in Python, so it's
        lmbda instead ^^
    """
    if not len(reco_items):
        return 0.0

    reco_distr = compute_genre_distr(reco_items)
    kl_div = compute_kl_divergence(interacted_distr, reco_distr)

    total_score = 0.0
    for item in reco_items:
        total_score += item.score

    # kl divergence is the lower the better, while score is
    # the higher the better so remember to negate it in the calculation
    utility = (1 - lmbda) * total_score - lmbda * kl_div
    return utility, total_score, kl_div


def compute_kl_divergence(interacted_distr, reco_distr, alpha=0.01):
    """
    KL (p || q), the lower the better.

    alpha is not really a tuning parameter, it's just there to make the
    computation more numerically stable.
    """
    kl_div = 0.
    for genre, score in interacted_distr.items():
        reco_score = reco_distr.get(genre, 0.)
        reco_score = (1 - alpha) * reco_score + alpha * score
        kl_div += score * np.log2(score / reco_score)

    return kl_div


def compute_genre_distr(items):
    """Compute the genre distribution for a given list of Items."""
    distr = {}
    for item in items:
        for genre, score in item.genres.items():
            genre_score = distr.get(genre, 0.)
            distr[genre] = genre_score + score

    # we normalize the summed up probability so it sums up to 1
    # and round it to three decimal places, adding more precision
    # doesn't add much value and clutters the output
    for item, genre_score in distr.items():
        normed_genre_score = round(genre_score / len(items), 3)
        distr[item] = normed_genre_score

    return distr
