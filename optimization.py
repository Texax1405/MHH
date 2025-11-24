# We assume each action with one score:
# EAT = +100
# THINK = +10
# FORK = +1
# WAIT = -50

def get_obj_weights(net):
    # Max c^T * M

    weights = {}
    for pid, place in net.places.items():
        name = place.name

        if "EAT" in name:
            weights[pid] = 100
        elif "THINK" in name:
            weights[pid] = 10
        elif "FORK" in name:
            weights[pid] = 1
        elif "WAIT" in name:
            weights[pid] = -50
        else:
            weights[pid] = 0
    return weights

def optimize_reachable(net, bdd, reachable_bdd):
    weights = get_obj_weights(net)
    all_place_ids = list(net.places.keys())

    max_value = -float('inf')
    best_marking_ids = []

    for model in bdd.pick_iter(reachable_bdd, care_vars = all_place_ids):
        curr_value = 0
        curr_ids = []

        for pid, val in model.items():
            if val == 1:
                curr_value += weights.get(pid, 0)
                curr_ids.append(pid)

        if curr_value > max_value:
            max_value = curr_value
            best_marking_ids = curr_ids

    return max_value, sorted(best_marking_ids), weights
