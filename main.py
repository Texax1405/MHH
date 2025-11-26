# main.py

import time
import tracemalloc

from BFS import find_reachable_markings
from petri_net_model import parser_petri_net
from bdd import symbolic_reachability
from deadlock import check_deadlock
from optimization import optimize_reachable

def get_place_names(net, place_ids):
    names = []
    for pid in place_ids:
        names.append(net.places[pid].name)
    return sorted(names)


def main():
    file = "file.xml"
    net = parser_petri_net(file)

    if not net:
        print("Error: cannot parse Petri net.")
        return

    # --- Task 1: Summary of the Petri Net
    print("--- Task 1: Summary Petri Net ---")
    # Places
    print(f"Total Places: {len(net.places)}")
    # Transitions
    print(f"Total Transitions: {len(net.transitions)}")
    # Arcs
    print(f"Total Arcs: {len(net.arcs)}")

    # --- Task 2: Explicit BFS reachability ---
    tracemalloc.start()
    t0 = time.time()

    reachable_markings = find_reachable_markings(net)

    t1 = time.time()
    current_exp, peak_exp = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print("--- Task 2: BFS is done! ---")
    print(f"total reachable markings (explicit BFS): {len(reachable_markings)}")
    print(f"Explicit BFS time: {t1 - t0:.6f} seconds")
    print(f"Explicit BFS peak memory (approx): {peak_exp / (1024 * 1024):.4f} MB")

    reachable_list = list(reachable_markings)
    for i, marking in enumerate(reachable_list[:5]):
        # each marking is a frozenset of place ids
        names = get_place_names(net, marking)
        print(f"{i+1}: {names}")

    # --- Task 3: Symbolic reachability using BDDs ---
    tracemalloc.start()
    t0 = time.time()

    bdd, reachable_bdd = symbolic_reachability(net)

    t1 = time.time()
    current_sym, peak_sym = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Marking count
    total_bdd = int(bdd.count(reachable_bdd))

    print("--- Task 3: BDD reachability is done! ---")
    print(f"total reachable markings (symbolic BDD): {total_bdd}")
    print(f"Symbolic BDD time: {t1 - t0:.6f} seconds")
    print(f"Symbolic BDD peak memory (approx): {peak_sym / (1024 * 1024):.4f} MB")
    print("Some reachable markings (decoded from BDD):")

    place_ids = sorted(net.places.keys())
    max_examples = 5
    for idx, model in enumerate(bdd.pick_iter(reachable_bdd)):
        if idx >= max_examples:
            break
        
        active_ids = {pid for pid in place_ids if model.get(pid, 0) == 1}
        names = get_place_names(net, active_ids)
        print(f"{idx+1}: {names}")

    # --- Task 4: Deadlock detection --- 
    print("--- Task 4: Deadlock Detection (ILP + BDD) ---")

    t0_dead = time.time()

    deadlock_result, deadlock_count = check_deadlock(net, bdd, reachable_bdd)

    t1_dead = time.time()

    if deadlock_result is None:
        print("RESULT: NO DEADLOCK FOUND!")
    else:
        print(f"RESULT: DEADLOCK FOUND! (Total deadlocks: {deadlock_count})")
        print(f"Time taken: {t1_dead - t0_dead: .6f} seconds")
        print("Deadlock marking:")
        deadlock_names = get_place_names(net, deadlock_result)
        print(f"Deadlock sample: {deadlock_names}")
        
    # --- Task 5: Optimization over reachable markings --- 

    print("--- Task 5: Optimization ---")
    tracemalloc.start()
    t0_opt = time.time()

    max_val, best_ids, weights_used = optimize_reachable(net, bdd, reachable_bdd)

    t1_opt = time.time()

    curr_opt, peak_opt = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"Optimization Result:")
    print(f"Maximum Objective Value: {max_val}")    
    print(f"Time taken: {t1_opt - t0_opt:.6f} seconds")
    print(f"Optimization peak memory: {peak_opt / (1024 * 1024):.4f} MB")
        
    best_names = get_place_names(net, best_ids)
    print(f"Optimal Marking: {best_names}")


if __name__ == "__main__":
    main()
