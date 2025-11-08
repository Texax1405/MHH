import xml.etree.ElementTree as ET 

class Place:
    def __init__(self, id, initial_marking=0):
        self.id = id
        self.initial_marking = initial_marking
    
    def __repr__(self):
        return f"Place(id='{self.id}', initial_marking={self.initial_marking})"
    
class Transition:
    def __init__(self, id):
        self.id = id
    
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
        print("--- Summary Petri Net ---")
        print(f"Total Places: {len(self.places)}")
        for p in self.places.values():
            print(f"  {p}")
        print(f"\nTotal Transitions: {len(self.transitions)}")
        for t in self.transitions.values():
            print(f"  {t}")
        print(f"\nTotal Arcs: {len(self.arcs)}")
        for a in self.arcs:
            print(f"  {a}")
        print("---------------------------")

def parse_petri_net(file):
    namespace = {'pnml': 'http://www.pnml.org/version-2009/grammar/pnml'}
    tree = ET.parse(file)
    root = tree.getroot()
    
    net = PetriNet()

    for place_node in root.findall('.//pnml:place', namespace):
        place_id = place_node.get('id')
        marking = 0 # set default marking to 0
        marking_text = None
        
        marking_node = place_node.find('pnml:initialMarking', namespace)
        
        if marking_node is not None:
            text_node = marking_node.find('pnml:text', namespace)
            marking_text = text_node.text

        if marking_text:
            marking = int(marking_text)

        net.places[place_id] = Place(place_id, marking)

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
    print("Reading file is done!!!")
    return net

file = "./parser-tool/include/file.xml"

petri_net_data = parse_petri_net(file)

if (petri_net_data):
    petri_net_data.print_summary()
        

