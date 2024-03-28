"""File containing the Tree, Restaurant, and Event classes to be used in the computations"""

from __future__ import annotations

import math
from typing import Any, Optional


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
    
