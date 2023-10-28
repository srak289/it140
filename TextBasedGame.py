# Copyright © 2023 Spencer Rak <spencer.rak@snhu.edu>
# SPDX-License-Header: MIT
#
# Assignment 7-3
# Project Two

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

    def __init__(self, msg):
        self.msg = msg
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


    def move(self, direction: str) -> 'Room':
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
            if self.locked:
                raise LockedRoomError(self)
            return getattr(self, direction)
        except AttributeError as e:
            raise NoRoomAdjacentError(f"There is no room in the {direction} direction")


    def move_with_key(self, inventory,  direction) -> None:
        # this might want to decorate....
        for i in inventory:
            if i.name == f"{self.name}_key":
                self.locked = False
        # let this raise
        return self.move(direction)


    @property
    def short_text(self):
        if "(" in self.text:
            # assumes there is a <space> before the '('
            return self.text[:self.text.index("(")-1]
        elif "," in self.text:
            # assumes there is no <space> before the ','
            return self.text[:self.text.index(",")]


    def display(self):
        """Print directional information for the player
        'you are in <a room> and you see <attribute of room>'
        e.g. 'You see the X room to the <direction>' or
        'You see a <item> on the floor.
        """
        s = f"You are in {self.text}.\n"
        # s += self.text if "(" not in self.text else self.text[:self.text.index("(")-1]
        s += f"You see {len(self.connections)} "
        s += "doorway.\n" if len(self.connections) == 1 else "doorways.\n"

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
        raise NoSuchItemError(s)


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
                # unsure if we should use internal errors for this
                # or if we should let the map handle adjacent room movements
                # I think it might make sense for the player to just track the room its in
                # and accept errors from the Room object
                # e.g. 'get item' -> Room raises 'no  such item'
                # or 'go west' -> Room raises 'cannot go west'
                # This almost invalidates the existence of the map
                # as the rooms are effectively a node graph with edges to each other
                try:
                    self.room = self.room.move(c.direction)
                except NoRoomAdjacentError as e:
                    e.display()
                except LockedRoomError as e:
                    e.display()
                    try:
                        # TODO Still have to look at lock mechanism
                        self.room = self.room.move_with_key(inventory, c.direction)
                        print(f"You unlock the room with theenter the room with the  key")
                    except LockedRoomError as e:
                        e.display()


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
        print(f"\nInventory: [{s}]\n")


def main():
    # upon entering the mold room the mold should consume each item with an effect
    # each item will couter the effect unless the player has failed to collect the
    # item that would couter said effect.
    # this will present different scenarios of loss to the player
    # e.g. "the mold has entered your eyes because you forgot goggles"
    # or "The mold has slowly suffocated you because you forgot your respirator"
    # except that it should be way more visceral

    GAME_RUN = True

    game_map = Map(MAPDATA)
    player = Player(game_map, game_map.get_room("your room"))

    while GAME_RUN:
        print("-"*30)
        player.room.display()
        player.display_inventory()

        try:
            cmd = Command.parse(input("Enter your command:\n"))
            print()
        except InvalidCommandError as e:
            e.display()
            continue
        try:
            player.command(cmd)
        except InvalidDirectionError as e:
            e.display()
        except CannotGetItemError as e:
            e.display()
        except QuitGameError as e:
            GAME_RUN = False
            print("Thanks for playing!")


if __name__ == "__main__":
    print(f"Starting game...\n")
    main()
