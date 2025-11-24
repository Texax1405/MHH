import xml.etree.ElementTree as ET 

class Place:
    def __init__(self, id, initial_marking=0, name=None):
        self.id = id
        self.initial_marking = initial_marking
        self.name = name or id

    def __repr__(self):
        return (
            f"Place(id='{self.id}', name='{self.name}', "
            f"initial_marking={self.initial_marking})"
        )
    
class Transition:
    def __init__(self, id):
        self.id = id
        self.pre_set = set()
        self.post_set = set()
    
    def __repr__(self):
        return f"Transition(id='{self.id}')"

class Arc:
    def __init__(self, id, source, target):
        self.id = id
        self.source = source
        self.target = target
    
    def __repr__(self):
        return f"Arc(id='{self.id}', source='{self.source}', target='{self.target}')"
    
class PetriNet:
    def __init__(self):
        self.places = {}
        self.transitions = {}
        self.arcs = []
    
    
    def print_summary(self):
        print("--- Task 1: Summary Petri Net ---")
        print(f"Total Places: {len(self.places)}")
        for p in enumerate(list(self.places.values())[:5]):
            print(f"  {p}")
        print(f"\nTotal Transitions: {len(self.transitions)}")
        for t in enumerate(list(self.transitions.values())[:5]):
            print(f"  {t}")
        print(f"\nTotal Arcs: {len(self.arcs)}")
        for a in enumerate(list(self.arcs)[:5]):
            print(f"  {a}")

def parser_petri_net(file):
    namespace = {'pnml': 'http://www.pnml.org/version-2009/grammar/pnml'}
    tree = ET.parse(file)
    root = tree.getroot()
    
    net = PetriNet()

    for place_node in root.findall('.//pnml:place', namespace):
        place_id = place_node.get('id')
        
        # --- đọc tên place từ <name><text>THINK_1</text> ---
        place_name = place_id       # default nếu không đọc được
        name_text_node = place_node.find('pnml:name/pnml:text', namespace)
        if name_text_node is not None and name_text_node.text:
            place_name = name_text_node.text.strip()

        # --- read intial marking ---
        marking = 0
        marking_text = None

        marking_node = place_node.find('pnml:initialMarking', namespace)
        if marking_node is not None:
            text_node = marking_node.find('pnml:text', namespace)
            if text_node is not None and text_node.text:
                marking_text = text_node.text
        
        if marking_text:
            marking = int(marking_text.strip())

        # tạo Place với id + name + initial marking 
        net.places[place_id] = Place(place_id, marking, place_name)
    
    for trans_node in root.findall('.//pnml:transition', namespace):
        trans_id = trans_node.get('id')
        net.transitions[trans_id] = Transition(trans_id)

    all_node = set(net.places.keys()) | set(net.transitions.keys()) # we delete duplicate id

    for arc_node in root.findall('.//pnml:arc', namespace):
        arc_id = arc_node.get('id')
        source_id = arc_node.get('source')
        target_id = arc_node.get('target')

        if source_id not in all_node:
            print(f"Source '{source_id}' is not exit!")
            continue
        
        if target_id not in all_node:
            print(f"Target '{target_id}' is not exit!")
            continue
    
        net.arcs.append(Arc(arc_id, source_id, target_id))

    for arc in net.arcs:
        if arc.target in net.transitions and arc.source in net.places:
            net.transitions[arc.target].pre_set.add(arc.source)
        elif arc.source in net.transitions and arc.target in net.places:
            net.transitions[arc.source].post_set.add(arc.target)
            
    return net
        

