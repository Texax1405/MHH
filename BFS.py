from petri_net_model import PetriNet

from collections import deque

def find_reachable_markings(net: PetriNet):
    queue = deque()

    visited = set()

    initial_marking_set = {pid for pid, place in net.places.items() if place.initial_marking > 0}
    initial_marking_frozen = frozenset(initial_marking_set)

    queue.append(initial_marking_frozen)
    visited.add(initial_marking_frozen)

    while queue:
        curr_marking = queue.popleft()

        for trans in net.transitions.values():
            if trans.pre_set.issubset(curr_marking):

                # turning from frozen set to set 
                next_marking_set = set(curr_marking)
                next_marking_set.difference_update(trans.pre_set)
                next_marking_set.update(trans.post_set)

                next_marking_frozen = frozenset(next_marking_set)

                if next_marking_frozen not in visited:
                    visited.add(next_marking_frozen)
                    queue.append(next_marking_frozen)

    print("--- Task 2: BFS is done! ---")
    return visited



