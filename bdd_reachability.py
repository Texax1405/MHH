# bdd_reachability.py

from dd.autoref import BDD
from petri_net_model import PetriNet


def symbolic_reachability(net: PetriNet):
    bdd = BDD()

    #1 Declare BDD variables for each place
    place_ids = sorted(net.places.keys())
    for pid in place_ids:
        bdd.declare(pid)        # p (current)
        bdd.declare(pid + "'")  # p' (next)

    #2 Initial Marking M0 for BDD
    init = bdd.true
    for pid in place_ids:
        var = bdd.var(pid)
        has_token = net.places[pid].initial_marking > 0
        if has_token:
            # place has a token in the initial marking
            init &= var
        else:
            # place is empty
            init &= ~var

    #3 Build Transition Relation R(p, p')
    R = bdd.false

    for t in net.transitions.values():
        rel_t = bdd.true

        for pid in place_ids:
            p_cur = bdd.var(pid)        # p
            p_next = bdd.var(pid + "'") # p'

            in_pre = pid in t.pre_set
            in_post = pid in t.post_set

            if in_pre and not in_post:
                # Token is consumed:  p = 1, p' = 0
                rel_t &= (p_cur & ~p_next)

            elif (not in_pre) and in_post:
                # Token is produced:  p = 0, p' = 1
                rel_t &= (~p_cur & p_next)

            elif in_pre and in_post:
                # Read-arc (token preserved):  p = 1, p' = 1
                rel_t &= (p_cur & p_next)

            else:
                # Place not affected by this transition:  p' must be equal to p
                rel_t &= ((~p_cur & ~p_next) | (p_cur & p_next))

        # Add to global relation: OR
        R |= rel_t

    #4 Fixpoint loop
    current_vars = list(place_ids)
    # map "next" variables back to "current" names for renaming p' -> p
    rename_next_to_cur = {pid + "'": pid for pid in place_ids}

    reachable = init        # already discoverd
    frontier = init         # not explored yet

    while True:
        #   step(p, p') = frontier(p) ∧ R(p, p')
        step = frontier & R

        #   step(p') = ∃p. step(p, p')
        step = bdd.exist(current_vars, step)

        # Rename p' -> p
        step = bdd.let(rename_next_to_cur, step)

        # Union with the already reached states (OR)
        new_reachable = reachable | step

        # Fixpoint test: if nothing new is found -> fixed point -> stop
        if new_reachable == reachable:
            break
        
        reachable = new_reachable
        frontier = step

    return bdd, reachable
