# bdd_reachability.py

from dd.autoref import BDD
from petri_net_model import PetriNet

def ordered_place_ids_by_group(net: PetriNet):
    """
    Sắp xếp lại place theo nhóm philosopher 

    - name của place có dạng 'THINK_1', 'WAIT_LEFT_FORK_3', 'FORK_5',...
    - Tách tên theo '_' lấy phần cuối:
        'THINK_1' -> '1'
        'WAIT_RIGHT_3' -> '3'
        'FORK_5' -> '5'
    - Chia thành group index || Nếu k có cho vào group 0

    Kết quả trả về: group 1, group 2, ... (list sorted place_ids)
    """
    groups = {}      # map: int -> list[place_id]

    for pid, place in net.places.items():
        # Lấy tên, nếu không có thì lấy id
        name = getattr(place, "name", pid)

        # Tách tên theo '_' và lấy số ở cuối
        parts = name.split('_')
        last = parts[-1]

        if last.isdigit():
            group_idx = int(last)
        else:
            group_idx = 0

        if group_idx not in groups:
            groups[group_idx] = []
        groups[group_idx].append(pid)

    ordered_place_ids = []
    for g in sorted(groups.keys()):
        # sort theo id in each group
        for pid in sorted(groups[g]):
            ordered_place_ids.append(pid)

    return ordered_place_ids

def symbolic_reachability(net: PetriNet):
    """
    Build BDD

    1. Chọn thứ tự biến bdd (variable ordering) tối ưu:
        - Gom place theo group
        - Xen kẻ p, p'
    2. Xây BDD cho intial marking 
    3. Xây transition relation R(p, p')
    4. Fixpoint: lập frontier cho đến khi không tìm được được trạng thái mới
    """
    bdd = BDD()

    # --- 1. Variable ordering ---
    place_ids = ordered_place_ids_by_group(net)
    # tạo dánh sách theo thứ tự: p1, p1',....
    var_order = []
    for pid in place_ids:
        var_order.append(pid)           # cur : p
        var_order.append(pid + "'")     # next: p'

    bdd.declare(*var_order)

    # cache lại bdd cho tối ưu (tránh overhead)
    x      = {pid: bdd.var(pid) for pid in place_ids}       # x      = p
    x_next = {pid: bdd.var(pid + "'") for pid in place_ids} # x_next = p'

    # --- 2. Initial Marking M0 ---
    init = bdd.true
    for pid in place_ids:
        var = x[pid]
        has_token = net.places[pid].initial_marking > 0

        if has_token:
            # place có token ở M0 -> p = 1
            init &= var
        else:
            # place không có token -> p = 0
            init &= ~var

    # --- 3. Transition Relation R(p, p') ---
    R = bdd.false

    for t in net.transitions.values():
        # rel_t biễu diễn quan hệ của 1 transition cụ thể
        rel_t = bdd.true

        for pid in place_ids:
            p_cur = x[pid]       # p
            p_next = x_next[pid] # p'

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

        # Gộp vào quan hệ tổng quát: R = OR các rel_t
        R |= rel_t

    # --- 4. FIXPOINT: BDD Reachability ---
    
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
