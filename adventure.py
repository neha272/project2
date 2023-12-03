import json
import sys
import random
import difflib  # Import difflib for string matching


class TextAdventure:
    def __init__(self, map_filename, win_condition=None, lose_condition=None):
        self.load_map(map_filename)
        self.current_room_id = 0
        self.inventory = []
        self.game_over = False
        self.turn_count = 0
        self.win_condition_func = win_condition
        self.lose_condition_func = lose_condition

    def load_map(self, map_filename):
        with open(map_filename, 'r') as file:
            self.rooms = json.load(file)

    def print_room(self):
        room = self.rooms[self.current_room_id]
        print(f"> {room['name']}\n\n{room['desc']}\n")
        exits = ', '.join(room['exits'])
        print(f"Exits: {exits}\n")

    def process_player_input(self, command):
        parts = command.lower().split()

        if not parts:
            print("Sorry, you need to enter a command.")
            return

        verb = self.find_closest_match(parts[0], ['go', 'get', 'look', 'inventory', 'quit', 'help'])
        if verb:
            if verb == 'go':
                self.go(self.find_closest_match(parts[1] if len(parts) > 1 else '', self.get_valid_exits()))
            elif verb == 'get':
                self.get(self.find_closest_match(parts[1] if len(parts) > 1 else '', self.get_valid_items()))
            elif verb == 'look':
                self.print_room()
            elif verb == 'inventory':
                self.show_inventory()
            elif verb == 'quit':
                print("Goodbye!")
                sys.exit()
            elif verb == 'help':
                self.show_help()
        else:
            print(f"Sorry, '{parts[0]}' is not a valid command.")

    def find_closest_match(self, input_str, valid_options):
        matches = difflib.get_close_matches(input_str, valid_options)
        if matches:
            return matches[0]
        return None

    def get_valid_exits(self):
        room = self.rooms[self.current_room_id]
        return list(room['exits'].keys())

    def get_valid_items(self):
        room = self.rooms[self.current_room_id]
        return room.get('items', [])


    def talk_to_npc(self, npc):
        print(f"{npc.name}: {npc.dialogue}")

        if npc.trade_item:
            trade_item = input(f"Do you want to trade? Type 'yes' to trade {npc.trade_item}: ").lower()
            if trade_item == 'yes':
                self.inventory.append(npc.trade_item)
                print(f"You trade with {npc.name} and receive {npc.trade_item}.")

    def handle_random_event(self):
        event_chance = random.random()
        if event_chance < 0.2:
            print("A random event occurs!")

    def go(self, direction):
        room = self.rooms[self.current_room_id]
        exits = room['exits']

        if direction in exits:
            self.current_room_id = exits[direction]
        elif direction:
            possible_directions = [d for d in exits if d.startswith(direction)]
            if len(possible_directions) == 1:
                self.current_room_id = exits[possible_directions[0]]
            elif len(possible_directions) > 1:
                print(f"Did you want to go {' or '.join(possible_directions)}?")
            else:
                print(f"There's no way to go {direction}.")
        else:
            print("Please specify a valid direction.")



    def search(self):
        if self.current_room.hidden:
            self.current_room.hidden = False
            print("You search the area and discover a hidden room!")
            self.print_room()

    def run_game(self):
        while not self.game_over:
            self.update_dynamic_items()
            self.handle_random_event()
            self.process_player_input()
            if self.win_condition_func and self.win_condition_func(self):
                print("Congratulations! You won the game!")
                self.game_over = True
            elif self.lose_condition_func and self.lose_condition_func(self):
                print("Sorry, you lost the game.")
                self.game_over = True

    def get(self, item):
        room = self.rooms[self.current_room_id]

        if 'items' in room and item in room['items']:
            self.inventory.append(item)
            room['items'].remove(item)
            print(f"You pick up the {item}.")
        else:
            print(f"There's no {item} anywhere.")

    def show_inventory(self):
        if self.inventory:
            print("Inventory:")
            for item in self.inventory:
                print(f"  {item}")
        else:
            print("You're not carrying anything.")

    def show_help(self):
        verbs = ['go', 'get', 'look', 'inventory', 'quit', 'help']
        print("You can run the following commands:")
        for verb in verbs:
            print(f"  {verb} ...")

    def win_condition(self, player):
        return "key" in player.inventory

    def lose_condition(self, player):
        return player.current_room['name'] == "Boss Room" and "sword" not in player.inventory


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 adventure.py [map filename]")
        sys.exit(1)

    map_filename = sys.argv[1]

    game = TextAdventure(map_filename, win_condition=TextAdventure.win_condition, lose_condition=TextAdventure.lose_condition)

    while True:
        game.print_room()
        command = input("What would you like to do? ").strip()
        game.process_player_input(command)


if __name__ == "__main__":
    main()
