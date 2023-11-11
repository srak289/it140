# Copyright © 2023 Spencer Rak <spencer.rak@snhu.edu>
# SPDX-License-Header: MIT
#
# Assignment 7-3
# Project Two
#
# Note the use of `assert` statements to denote internal failures that *MUST NOT* occur
# The use of `raise` to signal internal errors is for communication between objects

import dataclasses
# Use typing to conform to standards prior to 3.11
import typing
import yaml


MAPDATA = yaml.safe_load("""\
items:
  - name: cleaning gloves
    attr: protect_hands
    text: heavy gloves that cover your hands
    room: downstairs bathroom

  - name: swimming goggles
    attr: protect_eyes
    text: thick goggles that seal your eyes
    room: sisters room

  - name: respirator
    attr: protect_lungs
    text: a face-mask that can filter the air
    room: storage room

  - name: trash bags
    attr: protect_torso
    text: a thick bag that could cover your body
    room: kitchen

  - name: bleach
    attr: destroy_mold
    text: a toxic liquid known for removing mold
    room: master bathroom

  - name: plastic scraper
    attr: destroy_mold
    text: a flexible tool for scraping surfaces clean
    room: garage

  - name: garage key
    attr: unlock_garage
    text: a key that goes to the garage door
    room: coatroom

  - name: basement key
    attr: unlock_basement
    text: a key that goes to the basement door
    room: parents room

rooms:
  - name: downstairs bathroom
    connections:
      east: dining room
      south: kitchen
    text: the downstairs bathroom

  - name: dining room
    connections:
      west: downstairs bathroom
      south: downstairs hallway
    text: the dining room

  - name: kitchen
    connections:
      north: downstairs bathroom
      east: downstairs hallway
    text: the kitchen

  - name: downstairs hallway
    connections:
      north: dining room
      east: stairwell first floor
      west: kitchen
      south: coatroom
    text: the downstairs hallway

  - name: coatroom
    connections:
      north: downstairs hallway
      east: garage
    text: the coatroom

  - name: garage
    connections:
      north: stairwell basement
      west: coatroom
    text: the garage
    locked: True

  - name: basement
    connections:
      south: stairwell basement
    text: the basement
    locked: True
    villian: True

  - name: master bathroom
    connections:
      west: parents room
    text: your parent's bathroom (ew)

  - name: parents room
    connections:
      north: upstairs hallway
      east: master bathroom
      west: storage room
    text: your parent's room (you shouldn't stay long)

  - name: storage room
    connections:
      east: parents room
    text: your parent's closet (are you sure you want to look here?)

  - name: sisters room
    connections:
      south: upstairs hallway
    text: your sister's room (don't look too closely)

  - name: your room
    connections:
      east: upstairs hallway
    text: your room, home sweet home
    start: True

  - name: upstairs hallway
    connections:
      north: sisters room
      east: stairwell second floor
      south: parents room
      west: your room
    text: the upstairs hallway

  - name: stairwell basement
    connections:
      up: stairwell first floor
      north: basement
      south: garage
    text: the basement stairwell
    stairwell: True

  - name: stairwell first floor
    connections:
      up: stairwell second floor
      down: stairwell basement
      west: downstairs hallway
    text: the first floor stairwell
    stairwell: True

  - name: stairwell second floor
    connections:
      down: stairwell first floor
      west: upstairs hallway
    text: the second floor stairwell
    stairwell: True
""")


class TextBasedGameError(Exception):
    """A base class for internal game error handling
    Args:
        msg: The text to display
        **kwargs: Extra key=value attributes to add to the raised error
    """

    def __init__(self, msg, **kwargs):
        self.msg = msg
        for k, v in kwargs.items():
            setattr(self, k, v)
        super().__init__(msg)


    def display(self):
        print(f"\nE: {self.msg}\n")


class InvalidCommandError(TextBasedGameError): pass
class InvalidDirectionError(TextBasedGameError): pass
class LockedRoomError(TextBasedGameError): pass
class NoRoomAdjacentError(TextBasedGameError): pass
class CannotGetItemError(TextBasedGameError): pass
class QuitGameError(TextBasedGameError): pass
class NoSuchRoomError(TextBasedGameError): pass
class NoSuchItemError(TextBasedGameError): pass


@dataclasses.dataclass
class Base:
    """A base class for other object types to inherit from
    Args:
        name: The object's name
        text: The text to display for the object in-game
    """
    name: str
    text: str

    @classmethod
    def from_dict(cls, **kwargs) -> 'Base':
        return cls(**kwargs)


    def display(self) -> None:
        print(self.text)


@dataclasses.dataclass
class Item(Base):
    """An object for representing item pickups
    Args:
        attr: The attribute of the item
        room: The room the item should be placed in
    """
    attr: str
    room: str


class Command:
    """An object for representing valid commands
    """
    _valid_cmd = set({"go", "get", "quit"})

    def __init__(self, cmd: str, **kwargs):
        self.cmd = cmd
        # add additional attributes provided in kwargs
        for k, v in kwargs.items():
            setattr(self, k, v)


    @classmethod
    def parse(cls, raw_cmd: str) -> 'Command':
        """Parse a raw string and return an instance of :class:Command
        Args:
            raw_cmd: The string to parse, usually user input
        Raises:
            InvalidCommandError
        """
        raw_cmd = raw_cmd.lower().split()
        if len(raw_cmd) == 0:
            raise InvalidCommandError(f"You must enter one of {cls._valid_cmd}!")
        elif raw_cmd[0] not in cls._valid_cmd:
            raise InvalidCommandError(f"{raw_cmd} is not one of {cls._valid_cmd}")
        elif raw_cmd[0] == "go":
            # valid use of the go command is `go <valid-direction>`
            # valid direction is up to the current room as stairwells
            # also allow you to move up and down
            if len(raw_cmd) < 2:
                raise InvalidCommandError(f"'go' command requires argument <direction>")
            return cls(raw_cmd[0], direction=raw_cmd[1])
        elif raw_cmd[0] == "get":
            # valid use of the get command is `get <item>`
            # whether you can get the item is up to the current room
            if len(raw_cmd) < 2:
                raise InvalidCommandError(f"'get' command requires argument <item>")
            return cls(raw_cmd[0], item=" ".join(raw_cmd[1:]))
        elif raw_cmd[0] == "quit":
            # valid use of the get command is `quit`
            return cls(raw_cmd[0])
        assert False,"Failed parsing command!"


@dataclasses.dataclass
class Room(Base):
    """An object for representing a room in the game
    Args:
        connections: A dict of {:str:, :class:Room}
        items: A list of :class:Item
        start: If the player starts here
        locked: If the room is locked
        villian: If there is a villian in the room
        stairwell: If the room is a stairwell
    """
    connections: typing.Dict[str, 'Room']
    items: typing.Dict[str, Item] = dataclasses.field(default_factory = lambda: dict())
    start: bool = False
    locked: bool = False
    villian: bool = False
    stairwell: bool = False

    def __post_init__(self) -> None:
        self._valid_directions = set({"north", "east", "south", "west"})
        if self.stairwell:
            # if we are a stairwell then valid directions include "up" and "down"
            self._valid_directions |= {"up", "down"}


    def _add_item(self, item: Item) -> None:
        """Add an item to the room
        """
        self.items[item.name] = item


    def _add_adjacent_room(self, direction: str, room: 'Room') -> None:
        """Create a unidirectional edge between `self` and `room`
        Args:
            room: The room to create an edge to
        """
        assert direction in self._valid_directions,f"{direction} is invalid"
        self.connections[direction] = room


    def get(self, item: str) -> Item:
        """Return an item from the room to the player
        Args:
            s: The name of the item
        Raises:
            CannotGetItemError if the item is not in the room
        """
        if item not in self.items:
            raise CannotGetItemError(f"There is no {item} in {self.short_text}")
        return self.items.pop(item)


    def move(self, direction: str, keys: list = None) -> 'Room':
        """Move the player in 'direction'
        Args:
            direction: The string name of the direction to move
        Raises:
            NoRoomAdjacentError
            LockedRoomError
        """
        if direction not in self._valid_directions:
            raise InvalidDirectionError(f"{direction} is not one of {self._valid_directions}")
        try:
            # we need to check if the target room is locked, not if we are locked
            target = getattr(self, direction)
            if keys and target.locked:
                for k in keys:
                    if k.attr == f"unlock_{target.name}":
                        target.locked = False
            if target.locked:
                raise LockedRoomError(f"The {target.text} is locked", room=target)
            return target
        except AttributeError as e:
            raise NoRoomAdjacentError(f"There is no room in the {direction} direction")


    @property
    def short_text(self) -> str:
        """:class:Room.text without additional information
        """
        if "(" in self.text:
            # assumes there is a <space> before the '('
            return self.text[:self.text.index("(")-1]
        elif "," in self.text:
            # assumes there is no <space> before the ','
            return self.text[:self.text.index(",")]
        return self.text


    def fight(self, inventory: list) -> None:
        """Run the fight sequence if self.villian is True
        """
        if not self.villian:
            return
        else:
            # construct a dictionary of items without including keys
            pinv = [i.name for i in inventory if not i.name.endswith(" key")]

            text = "You enter the basement and see the mold.\n"
            win = True
            injured = False

            if "plastic scraper" in pinv:
                text += "You scrape at the mold with your plastic scraper.\n"
            else:
                text += "You claw at the mold with your hands but fail to remove most of it.\n"
                win = False

            if "cleaning gloves" in pinv:
                text += "Your cleaning gloves prevent the mold from touching your skin.\n"
            else:
                text += "The mold builds up beneath your fingernails and stains your hands.\n"
                win = False
                injured = True

            if "swimming goggles" in pinv:
                text += "You can see clearly as you clean because of your sister's goggles.\n"
            else:
                text += "The mold begins to build up in your eyes and your vision blurs.\n"
                win = False
                injured = True

            if "respirator" in pinv:
                text += "Your respirator prevents the mold spores from entering your lungs.\n"
            else:
                text += "You begin to cough as the mold spores build up in your lungs.\n"
                win = False
                injured = True

            if "trash bags" in pinv:
                text += "The mold does not stick to the trash bags you wear like a poncho.\n"
            else:
                text += "The mold stains your clothing and your skin.\n"
                win = False
                injured = True

            if "bleach" in pinv:
                text += "You spray bleach on the moldy surfaces.\n"
            else:
                text += "You hope the mold will not return.\n"
                win = False

            print(text)

            if win:
                print("Your collection of items protected you from the dangers of the mold!\nYou even bleached the mold after you cleaned and it shall never return!\nYou should be able to move into the basement soon enough after it airs out!\nCongratulations, YOU WON!\n")
            else:
                if injured:
                    print("You succumb to the mold after a long day cleaning in the basement.\nInitially you felt fine but mold is a slow killer and you forgot some life-saving protective equipment.\nBetter luck next time...\n")
                else:
                    print("You wait several days for the dust to settle and check back on the basement.\nUnfortunately you did not bleach the walls and the mold has returned stronger than before.\nBetter luck next time...\n")

            raise QuitGameError("QUIT")


    def display(self):
        """Print information for the player
        'you are in <room> and you see <attribute of room>'
        e.g. 'You see the X room to the <direction>' or
        'You see a <item> on the floor.
        """
        s = f"You are in {self.text}.\n"
        if hasattr(self, "up"):
            s += "You see stairs leading to the floor above.\n"
        if hasattr(self, "down"):
            s += "You see stairs leading to the floor below.\n"
        if hasattr(self, "north"):
            s += "You see a doorway to the north.\n"
        if hasattr(self, "east"):
            s += "You see a doorway to the east.\n"
        if hasattr(self, "south"):
            s += "You see a doorway to the south.\n"
        if hasattr(self, "west"):
            s += "You see a doorway to the west.\n"

        if len(self.items) > 0:
            for k, v in self.items.items():
                if v.name.endswith("key"):
                    pname = f"the {v.name}"
                elif v.name.endswith("s"):
                    pname = v.name
                else:
                    pname = f"a {v.name}"
                s += f"You see {pname}: {v.text}.\n"
        print(s)


class Map:
    """An object that loads the game environment from a YAML document
    """
    def __init__(self, mapdata):
        # construct the items
        self._items = {v["name"]: Item.from_dict(**v) for v in mapdata["items"]}
        # construct the map
        # all rooms must be initialized before connections can be made
        self._rooms = {v["name"]: Room.from_dict(**v) for v in mapdata["rooms"]}

        # add the items to their respective rooms
        for _, i in self._items.items():
            self._rooms[i.room].items = dict()
            self._rooms[i.room]._add_item(i)


        # assign directional attributes for each room connection
        for _, r in self._rooms.items():
            for k, v in r.connections.items():
                setattr(r, k, self.get_room(v))


    def get_item(self, s: str) -> Item:
        """Return a :class:Item
        Args:
            s: The name of the item
        Raises:
            NoSuchItemError
        """
        if s in self._items:
            return self._items[s]
        raise NoSuchItemError(f"There is no such item '{s}'")


    def get_room(self, s: str) -> Room:
        """Return a :class:Room
        Args:
            s: The name of the room
        Raises:
            NoSuchRoomError
        """
        if s in self._rooms:
            return self._rooms[s]
        raise NoSuchRoomError(s)


@dataclasses.dataclass
class Player:
    room_map: Map
    room: Room = None
    inventory: typing.List[Item] = dataclasses.field(default_factory=lambda: list())

    def command(self, c: Command):
        if c.cmd == "go":
            try:
                assert hasattr(c, "direction"),f"Command {c} did not specify a direction!"
                try:
                    self.room = self.room.move(c.direction)
                except NoRoomAdjacentError as e:
                    e.display()
                except LockedRoomError as e:
                    print(f"It appears that {e.room.text} is locked.")
                    try:
                        keys = []
                        for i in self.inventory:
                            if i.name.endswith(" key"):
                                keys.append(i)
                        self.room = self.room.move(c.direction, keys)
                        print(f"You unlock {e.room.text} and proceed through the door.")
                    except LockedRoomError as e:
                        print(f"You do not appear to have the key.")
            except InvalidDirectionError as e:
                raise

        elif c.cmd == "get":
            assert hasattr(c, "item"),f"Command {c} did not specify an item!"
            try:
                _ = self.room_map.get_item(c.item)
            except NoSuchItemError as e:
                raise
            try:
                self.inventory.append(self.room.get(c.item))
            except CannotGetItemError as e:
                raise

        elif c.cmd == "inspect":
            self.room.inspect()

        elif c.cmd == "quit":
            raise QuitGameError("QUIT")


    def display_inventory(self):
        s = ', '.join([x.name for x in self.inventory])
        print(f"Inventory: [{s}]\n")


def main():
    GAME_RUN = True

    print("You wake up at noon like usual and decide today is the day you move to the basement.\nYour parents and sister are sick of you staying up until 3am playing video games\nlike the responsible 27 year old man that you are.\nThe most logical thing for you to do is clean out the basement and\nmove down there to pursue your illustrious video game career.\nFirst you need to gather six items to protect yourself from the mold down there while you are cleaning.\nKnow that if you find any keys they do not count towards the six items you need.\n")

    # We initialize the Map and create a Player
    game_map = Map(MAPDATA)
    player = Player(game_map, game_map.get_room("your room"))

    while GAME_RUN:
        print("-"*30)
        player.room.display()
        player.display_inventory()
        try:
            player.room.fight(player.inventory)
        except QuitGameError:
            GAME_RUN = False
            print("Thanks for playing!")
            break

        try:
            cmd = Command.parse(input("Enter your command:\n"))
            print()
        except InvalidCommandError as e:
            e.display()
            continue
        try:
            player.command(cmd)
        except (
            InvalidDirectionError,
            CannotGetItemError,
            NoSuchItemError,
        ) as e:
            e.display()
        except QuitGameError as e:
            GAME_RUN = False
            print("Thanks for playing!")
            break


if __name__ == "__main__":
    main()
