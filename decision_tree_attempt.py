"""File containing the Tree, Restaurant, and Event classes to be used in the computations"""

from __future__ import annotations

import math
from typing import Any, Optional

import csv


class Tree:
    """A recursive tree data structure.

    Note the relationship between this class and RecursiveList; the only major
    difference is that _rest has been replaced by _subtrees to handle multiple
    recursive sub-parts.

    Representation Invariants:
        - self._root is not None or self._subtrees == []
        - all(not subtree.is_empty() for subtree in self._subtrees)
    """
    # Private Instance Attributes:
    #   - _root:
    #       The item stored at this tree's root, or None if the tree is empty.
    #   - _subtrees:
    #       The list of subtrees of this tree. This attribute is empty when
    #       self._root is None (representing an empty tree). However, this attribute
    #       may be empty when self._root is not None, which represents a tree consisting
    #       of just one item.
    _root: Optional[Any]
    _subtrees: list[Tree]

    def __init__(self, root: Optional[Any], subtrees: list[Tree]) -> None:
        """Initialize a new Tree with the given root value and subtrees.

        If root is None, the tree is empty.

        Preconditions:
            - root is not none or subtrees == []
        """
        self._root = root
        self._subtrees = subtrees

    def insert_sequence(self, items: list) -> None:
        """Insert the given items into this tree.

        The inserted items form a chain of descendants, where:
            - items[0] is a child of this tree's root
            - items[1] is a child of items[0]
            - items[2] is a child of items[1]
            - etc.

        Do nothing if items is empty.

        The root of this chain (i.e. items[0]) should be added as a new subtree within this tree, as long as items[0]
        does not already exist as a child of the current root node. That is, create a new subtree for it
        and append it to this tree's existing list of subtrees.

        If items[0] is already a child of this tree's root, instead recurse into that existing subtree rather
        than create a new subtree with items[0]. If there are multiple occurrences of items[0] within this tree's
        children, pick the left-most subtree with root value items[0] to recurse into.

        Hints:

        To do this recursively, you'll need to recurse on both the tree argument
        (from self to a subtree) AND on the given items, using the "first" and "rest" idea
        from RecursiveLists. To access the "rest" of a built-in Python list, you can use
        list slicing: items[1:len(items)] or simply items[1:], or you can use a recursive helper method
        that takes an extra "current index" argument to keep track of the next move in the list to add.

        Preconditions:
            - not self.is_empty()

        >>> t = Tree(111, [])
        >>> t.insert_sequence([1, 2, 3])
        >>> print(t)
        111
          1
            2
              3
        >>> t.insert_sequence([1, 3, 5])
        >>> print(t)
        111
          1
            2
              3
            3
              5
        """

        if not items:
            return
        child_exists = False
        existing_subtree = None
        for tree in self._subtrees:
            if tree._root == items[0]:
                child_exists = True
                existing_subtree = tree
                break
        if not child_exists:
            new_subtree = Tree(items[0], [])
            self._subtrees.append(new_subtree)
            existing_subtree = new_subtree
        existing_subtree.insert_sequence(items[1:])

    def traverse_dec_tree(self, answers: list[str]) -> list[str]:
        """
        Traverse the decision tree to determine the possible restaurant(s) that match
        the user's inputs.
        """
        current_node = self
        possible_restaurant = []

        for answer in answers:
            found = None
            for child in current_node._subtrees:
                if child._root == answer:
                    found = child
                    break
            if found:
                current_node = found
            else:
                return []

        if current_node._subtrees:
            for child in current_node._subtrees:
                possible_restaurant.append(child._root)

        return possible_restaurant


class Restaurant:
    """A tree node containing information about the restaurant
    """
    name: str
    cuisine: str
    price_range: Optional[tuple[int, int]]
    address: str
    star_rating: float
    phone: Optional[str]
    coordinates: Optional[tuple[float, float]]  # (latitude, longitude)
    distance_from_user: Optional[float]

    def __init__(self, name: str, cuisine: str, price_range: tuple[int, int], address: str,
                 star_rating: float, phone: str, coordinates: tuple[float, float]):
        """Initalize a new Restaurant with the given information

        Preconditions:
            - 0 <= star_rating <= 5.0
            - name != ''
            - address != ''
            - cuisine != ''
            - price_range[0] < price_range[1]
        """
        self.name = name
        self.coordinates = coordinates
        self.cuisine = cuisine
        self.phone = phone
        self.price_range = price_range
        self.address = address
        self.star_rating = star_rating

    def calculate_distance(self, user_lat: float, user_long: float) -> Optional[float]:
        """Calculate the distance between the user and the restaurant"""
        if self.coordinates is None:
            return None
        else:
            lat1 = math.radians(self.coordinates[0])
            lat2 = math.radians(user_lat)
            long1 = math.radians(self.coordinates[1])
            long2 = math.radians(user_long)

            return (math.acos(math.sin(lat1) * math.sin(lat2) + math.cos(lat1) * math.cos(lat2) *
                              math.cos(long2 - long1)) * 6371)

    def in_price_range(self, low: int, high: int) -> Optional[bool]:
        """Check if self is in the user's price range"""
        if self.price_range is None:
            return None
        else:
            return self.price_range[0] <= low < self.price_range[1] or self.price_range[0] < high <= self.price_range[1]


class Event:
    """A tree node containing information about user-inputted events
    """
    name: str
    location: str
    time: str
    coordinates: tuple[int, int]
    distance_from_user: float

    def __init__(self, name: str, location: str, time: str, coordinates: tuple[int, int]):
        """Initialize a new event with the given information

        Preconditions:
        - name != ''
        - location != ''
        """
        self.time = time
        self.coordinates = coordinates
        self.name = name
        self.location = location

    def calculate_distance(self, user_lat: float, user_long: float) -> float:
        """Calculate the distance between the user and the event location"""
        lat1 = math.radians(self.coordinates[0])
        lat2 = math.radians(user_lat)
        long1 = math.radians(self.coordinates[1])
        long2 = math.radians(user_long)

        return (math.acos(math.sin(lat1) * math.sin(lat2) + math.cos(lat1) * math.cos(lat2) *
                          math.cos(long2 - long1)) * 6371)


def build_decision_tree(file: str) -> Tree:
    """Build a decision tree storing the restaurant data from the given file.

    Preconditions:
        - file is the path to a csv file in the format of the provided restaurant.csv
    """
    tree = Tree('', [])  # The start of a decision tree
    with open(file, 'r', encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        next(reader)  # skip the header row

        for row in reader:
            # row is a list[str] containing the data in the file.
            # Your task is to process this list so that you can insert it into tree.
            # Note: if PyCharm gives you a warning about mixing bool and str types in a list,
            # you can safely ignore the warning.
            if 'Unit' in row[0]:
                continue
            if len(row) >= 3:
                restaurant_name = row[2]
            else:
                restaurant_name = 'No Name Available'
            data = [row[0], get_price_range(row), get_distance_from_user(row, (0, 0))]
            tree.insert_sequence(data + [restaurant_name])

    return tree


def get_price_range(row: list[str]) -> str:
    """
    FILLER
    """
    for item in row:
        if item == '$11-30':
            return item
        if item == 'Under $10':
            return item
        if item == 'Above $61':
            return item
        if item == '$31-60':
            return item
    return 'No price range available'


def get_distance_from_user(row: list[str], user_coordinates: tuple) -> str:
    """
    FILLER
    """
    latitude = None
    longitude = None
    for item in row:
        if is_digit_or_decimal(item):
            if latitude is None:
                latitude = float(item)
            else:
                longitude = float(item)
    if latitude is None or longitude is None:
        return "Invalid coordinate"
    latitude2 = math.radians(user_coordinates[0])
    longitude2 = math.radians(user_coordinates[1])
    distance = (math.acos(math.sin(latitude) * math.sin(latitude2) + math.cos(latitude) * math.cos(latitude2) *
                          math.cos(longitude2 - longitude)) * 6371)
    if distance < 1:
        return "Under 1km"
    elif 1 <= distance <= 5:
        return "1-5 km"
    else:
        return 'Above 5km'


def is_digit_or_decimal(s: str) -> bool:
    """Filler"""
    if s.startswith('-'):
        s = s[1:]

    return s.replace('.', '', 1).isdigit()


RESTAURANT_QUESTIONS = [
    'What type of cuisine do you want?',
    'What is your price range?\nUnder $10\n$11-30\n$31-60\nAbove $61',
    'How close do you want the restaurant to be?\nUnder 1km\n1-5 km\nAbove 5km'
]


def get_user_input(questions: list[str]) -> list[str]:
    """Return the user's answers to a list of questions."""
    answers_so_far = []

    for question in questions:
        print(question)
        s = input()
        answers_so_far.append(s)  # Any other input is interpreted as False

    return answers_so_far


def run_restaurant_finder(toronto_file: str) -> None:
    """
    Filler
    """
    tree = build_decision_tree(toronto_file)
    answers = get_user_input(RESTAURANT_QUESTIONS)
    restaurants = tree.traverse_dec_tree(answers)
    if not restaurants:
        print('No restaurants')
    elif len(restaurants) == 1:
        print(f'Restaurant: {restaurants[0]}')
    else:
        for restaurant in restaurants:
            print(f'Restaurant: {restaurant}\n')
