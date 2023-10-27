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
  - name: Cleaning Gloves
    attr: protect_hands
    text: heavy gloves that cover your hands

  - name: Swimming Goggles
    attr: protect_eyes
    text: thick goggles that seal your eyes

  - name: Respirator
    attr: protect_lungs
    text: a face-mask that can filter the air

  - name: Trash Bags
    attr: protect_torso
    text: a thick bag that could cover your body

  - name: Bleach
    attr: destroy_mold
    text: a toxic liquid known for removing mold

  - name: Plastic Scraper
    attr: destroy_mold
    text: a flexible tool for scraping surfaces clean

  - name: Garage Key
    attr: unlock_garage
    text: a key that goes to the garage door

  - name: Basement Key
    attr: unlock_basement
    text: a key that goes to the basement door

rooms:
  - name: Downstairs Bathroom
    connections:
      - east: Dining Room
      - south: Kitchen
    items:
      - Cleaning Gloves
    text: the downstairs bathroom

  - name: Dining Room
    connections:
      - west: Downstairs Bathroom
      - south: Downstairs Hallway
    text: the dining room

  - name: Kitchen
    connections:
      - north: Downstairs Bathroom
      - east: Downstairs Hallway
    items:
      - Trash Bags
    text: the kitchen

  - name: Downstairs Hallway
    connections:
      - north: Dining Room
      - east: Stairwell First Floor
      - west: Kitchen
      - south: Coatroom
    text: the downstairs hallway

  - name: Coatroom
    connections:
      - north: Downstairs Hallway
      - east: Garage
    items:
      - Garage Key
    text: the coatroom

  - name: Garage
    connections:
      - north: Stairwell Basement
      - west: Coatroom
    items:
      - Plastic Scraper
    text: the garage
    locked: True

  - name: Basement
    connections:
      - south: Stairwell Basement
    text: the basement
    locked: True
    villian: True

  - name: Master Bathroom
    connections:
      - west: Parents Room
    items:
      - Bleach
    text: your parent's bathroom (ew)

  - name: Parents Room
    connections:
      - east: Master Bathroom
      - west: Storage Room
    items:
      - Basement Key
    text: your parent's room (you shouldn't stay long)

  - name: Storage Room
    connections:
      - east: Parents Room
    items:
      - Respirator
    text: your parent's closet (are you sure you want to look here?)

  - name: Sisters Room
    connections:
      - south: Upstairs Hallway
    items:
      - Swimming Goggles
    text: your sister's room (don't look too closely)

  - name: Your Room
    connections:
      - east: Upstairs Hallway
    text: your room, home sweet home
    start: True

  - name: Upstairs Hallway
    connections:
      - north: Sisters Room
      - east: Stairwell Second Floor
      - south: Parents Room
      - west: Your Room
    text: the upstairs hallway

  - name: Stairwell Basement
    connections:
      - up: Stairwell First Floor
      - north: Basement
      - south: Garage
    text: the basement stairwell

  - name: Stairwell First Floor
    connections:
      - up: Stairwell Second Floor
      - down: Stairwell Basement
      - west: Downstairs Hallway
    text: the first floor stairwell

  - name: Stairwell Second Floor
    connections:
      - down: Stairwell First Floor
      - west: Upstairs Hallway
    text: the second floor stairwell
""")


class TextBasedGameError(Exception):

    def __init__(self, msg):
        super().__init__(msg)


    def display(self):
        print(f"\nE: {s}\n")


class CannotGetItemError(TextBasedGameError): pass
class InvalidCommandError(TextBasedGameError): pass
class InvalidDirectionError(TextBasedGameError): pass
class QuitGameError(TextBasedGameError): pass


@dataclasses.dataclass
class Item:
    name: str
    description: str

    def display(self):
        print()


class Command:
    _valid_cmd = set({"go", "get", "exit", "quit"})

    def __init__(self, cmd: str, **kwargs):
        self.cmd = cmd

        # add additional attributes provided in kwargs
        for k, v in kwargs.items():
            setattr(self, k, v)


    @classmethod
    def parse(cls, raw_cmd):
        raw_cmd = raw_cmd.lower().split()
        if raw_cmd[0] not in cls._valid_cmd:
            raise InvalidCommandError(f"{raw_cmd} is not one of {cls._valid_cmd}")
        elif raw_cmd[0] == "go":
            return cls(raw_cmd[0], direction=raw_cmd[1])
        elif raw_cmd[0] == "get":
            return cls(raw_cmd[0], item=raw_cmd[1])
        elif raw_cmd[0] == "exit":
            return cls(raw_cmd[0])
        elif raw_cmd[0] == "quit":
            return cls(raw_cmd[0])
        assert False,"Failed parsing command!"


@dataclasses.dataclass
class Room:
    name: str
    items: typing.List[Item] = dataclasses.field(default_factory=lambda: list())
    _adjacent_rooms: dict = dataclasses.field(default_factory=lambda: dict())

    def __post_init__(self):
        self._valid_directions = set({"Up", "Down"})

    def _add_adjacent_room(self, room):
        # if room.coupling in self._adjc
        # self._adjacent_rooms
        pass


    def move(self, direction):
        print(f"Moving {direction}")


    def _direction(self, direction):
        # try:
        #     return sel
        # if direction not in self.adjacent:
        #     raise KeyError("No direction")
        # return self.adjecan
        pass


    def lookaround(self):
        """Print directional information for the player
        'you are in <a room> and you see <attribute of room>'
        e.g. 'You see the X room to the <direction>' or
        'You see a <item> on the floor.
        """
        pass


    def locked(self):
        # this could decorate a property
        # or we could declare a direction as locked
        # we should probably mark ourselves as locked and inform the peer
        pass

    
    def display(self):
        print(f"You are in the {self.name}")

    # @property
    # def north(self):
    #     return self.get_direction("north")


    # @east.setter
    # def east(self, room):
    #     if self._east:
    #         raise RoomAlreadyS
    #     else:
    #         self._east = room


    # def east(self):
    #     return self._rooms["east"]
    #     pass


    # def south(self):
    #     pass


    # def west(self):
    #     pass


@dataclasses.dataclass
class Stairwell(Room):
    def __post_init__(self):
        self._valid_directions = set({"Up", "Down", "North", "South", "East", "West"})


class Map:

    def __init__(self, mapdata):
        # construct the map
        self._room_dict = {}
        for k, v in mapdata:
            self._room_dict.update({k: v})
            Room(**v)



    def get_room(self, s: str) -> Room:
        """Return a :class:Room or raise an exception
        Args:
            s: The name of the room
        """
        for r in self.room_list:
            if r.name == s:
                return r
        raise NoSuchRoomError(s)


@dataclasses.dataclass
class Player:
    room: Room = None
    room_map: Map = None
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
                self.room = self.room.move(c.direction)
            except InvalidDirectionError as e:
                raise

        elif c.cmd == "get":
            assert hasattr(c, "item"),f"Command {c} did not specify an item!"
            try:
                self.inventory.append(self.room.get(c.item))
            except CannotGetItemError as e:
                raise

        elif c.cmd == "exit":
            self.room = self.map.get_room("Stairwell First Floor")
            # perhaps this loop wants to exist in the game run loop
            while cmd := input("You can type 'go outside' to leave the game\nor 'go inside' to reenter the house\n").lower():
                if cmd not in ("go outside", "go inside"):
                    raise InvalidCommandError(f"{cmd} is not one of 'go outside' or 'go inside'")
                    continue
                if cmd == "go outside":
                    break
                elif cmd == "go inside":
                    break
                assert False,"Error in player exit command loop"


    def display_inventory(self):
        print(f"Inventory: {self.inventory}")




def configure_map() -> Room:
    """Generates map and returns a pointer to the starting room
    """
    return Room(name="Great Hall")


def main():
    # upon entering the mold room the mold should consume each item with an effect
    # each item will couter the effect unless the player has failed to collect the
    # item that would couter said effect.
    # this will present different scenarios of loss to the player
    # e.g. "the mold has entered your eyes because you forgot goggles"
    # or "The mold has slowly suffocated you because you forgot your respirator"
    # except that it should be way more visceral

    GAME_RUN = True
    room = configure_map()
    player = Player(room)
    del(room)
    assert player.room,"PLAYER.room cannot be 'None' at this point"
    VALID_CMDS = set({"go", "get", "exit", "quit"})


    while GAME_RUN:
        player.room.display()
        player.display_inventory()

        try:
            cmd = Command.parse(input("Enter your command:\n"))
        except InvalidCommandError as e:
            print(e)
            continue
        try:
            player.command(cmd)
        except InvalidDirectionError as e:
            print(e)
        except CannotGetItemError as e:
            print(e)
        except QuitGameError as e:
            GAME_RUN = False
            print("Thanks for playing!")


if __name__ == "__main__":
    print(f"Starting game...\n")
    main()
