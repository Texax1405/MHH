# main.py

import time
import tracemalloc

from bfs import find_reachable_markings
from petri_net_model import parser_petri_net
from bdd import symbolic_reachability
from deadlock import check_deadlock


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
    # for i, place in enumerate(net.places.values()):
    #     if i >= 5:
    #         break
    #     print(f"  ({i}, {place})")

    # Transitions
    print(f"Total Transitions: {len(net.transitions)}")
    # for i, trans in enumerate(net.transitions.values()):
    #     if i >= 5:
    #         break
    #     print(f"  ({i}, {trans})")

    # Arcs
    print(f"Total Arcs: {len(net.arcs)}")
    # for i, arc in enumerate(net.arcs):
    #     if i >= 5:
    #         break
    #     print(f"  ({i}, {arc})")

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

    # reachable_list = list(reachable_markings)
    # for i, marking in enumerate(reachable_list[:5]):
    #     # each marking is a frozenset of place ids
    #     print(f" {i}{set(marking)}")

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

    # place_ids = sorted(net.places.keys())
    # print("Some reachable markings (decoded from BDD):")
    # max_examples = 5
    # for idx, model in enumerate(bdd.pick_iter(reachable_bdd)):
    #     active_places = {pid for pid in place_ids if model.get(pid, False)}
    #     print(f" {idx}{active_places}")
    #     if idx + 1 >= max_examples:
    #         break

    # --- Task 4 --- 
    print("--- Task 4: Deadlock Detection (ILP + BDD) ---")

    t0_dead = time.time()

    deadlock_result, deadlock_count = check_deadlock(net, bdd, reachable_bdd)

    t1_dead = time.time()

    if deadlock_result is None:
        print("RESULT: NO DEADLOCK FOUND!")
    else:
        print("RESULT: DEADLOCK FOUND!")
        print(f"Total deadlocks: {deadlock_count}")
        print(" Deadlock marking:")
        print(f" {deadlock_result}")
        print(f"Time taken: {t1_dead - t0_dead: .6f} seconds")
    


if __name__ == "__main__":
    main()
