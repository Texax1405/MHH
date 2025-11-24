from petri_net_model import PetriNet
from dd.autoref import BDD

def check_deadlock(net, bdd, reachable_bdd):
    # Dead = all transition are Disabled
    # Disabled = ~Enabled
    deadlock_condition = bdd.true 

    all_place_ids = list(net.places.keys())

    for t in net.transitions.values():
        # Enabled(t) = AND(p) with all p belong to pre_set(t)
        t_enabled = bdd.true

        if not t.pre_set:
            t_enabled = bdd.true
        else:
            for pid in t.pre_set:
                t_enabled &= bdd.var(pid)
        
        t_disabled = ~t_enabled
        deadlock_condition &= t_disabled


    # Finding deadlock
    deadlock_set = reachable_bdd & deadlock_condition

    if deadlock_set == bdd.false:
        return None, 0
    else:
        deadlock_count = int(bdd.count(deadlock_set))
        solution = bdd.pick(deadlock_set, care_vars = all_place_ids)

        dead_marking_places = [pid for pid, val in solution.items() if val == 1]
        
        return sorted(dead_marking_places), deadlock_count


