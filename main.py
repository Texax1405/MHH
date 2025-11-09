from BFS import find_reachable_markings
from petri_net_model import parser_petri_net

def main():
    file = 'file.xml'
    petri_net_data = parser_petri_net(file)

    if (petri_net_data):
        petri_net_data.print_summary()

        all_markings = find_reachable_markings(petri_net_data)
        print(f"total reachable markings: {len(all_markings)}")

        for i, marking in enumerate(list(all_markings)[:5]):
            print(f" {i}{set(marking)}")

if __name__ == "__main__":
    main()