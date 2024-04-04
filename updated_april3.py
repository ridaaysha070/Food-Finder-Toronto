"""File containing the Tree, Restaurant, and Event classes to be used in the computations"""
from __future__ import annotations
from typing import Any, Optional
from requests.exceptions import MissingSchema
import plotly.express as px
import geopy
from geopy.geocoders import Nominatim
import pandas as pd
import math
import csv
import requests

rawdata = pd.read_csv('trt_rest.csv')

data = rawdata.dropna().drop_duplicates(subset=['Restaurant Address', 'Category'], keep='first')

RESTAURANT_QUESTIONS = [
    'What is your price range?\nUnder $10\n$11-30\n$31-60\nAbove $61',
    'What type of cuisine do you want?',
    'How close do you want the restaurant to be?\nUnder 1 km\n1-5 km\nAbove 5 km',
    'What Yelp star rating would you like the restaurant to have?\nAny\n1 star\n2 stars\n3 stars\n4 stars\n5 stars'
]

all_events = []


class User:
    """
    Stores information about the user (i.e., location, coordinates).
    """
    location: str
    longitude: float
    latitude: float
    questions: list
    recommendations: list[Restaurant]

    def __init__(self) -> None:
        """Initialize a new Tree with the given root value and subtrees.

        If root is None, the tree is empty.

        Preconditions:
            - root is not none or subtrees == []
        """
        self.location = ''
        self.longitude = 0.0
        self.latitude = 0.0
        self.questions = []
        self.recommendations = []


def get_user_info(user: User, location: str, cuisine: str, price: str, distance: str, star: str) -> Optional[str]:
    # adding a location argument, removing the input
    """
    Modify a User object based on the user's input.
    """
    answers = [price, cuisine, distance, star]
    user.questions = [x.capitalize() for x in answers]
    if location:
        geolocator = Nominatim(user_agent="a")
        loc1 = geolocator.geocode(location)
        lat = loc1.raw['lat']
        long = loc1.raw['lon']
        user.location = location
        user.latitude = float(lat)
        user.longitude = float(long)
    else:
        return 'Invalid location'

    # print('loading...')

def get_coords(ad: str) -> tuple[float, float]:
    geolocator = Nominatim(user_agent="a")
    loc1 = geolocator.geocode(ad)
    lat = loc1.raw['lat']
    long = loc1.raw['lon']
    return lat, long


# def get_user_input(questions: list[str]) -> list[str]:
#     """Return the user's answers to a list of questions."""
#     answers_so_far = []
#
#     for question in questions:
#         print(question)
#         s = input()
#         answers_so_far.append(s)
#
#     return answers_so_far

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

    def is_empty(self) -> bool:
        """Return whether this tree is empty.

        >>> t1 = Tree(None, [])
        >>> t1.is_empty()
        True
        >>> t2 = Tree(3, [])
        >>> t2.is_empty()
        False
        """
        return self._root is None

    def _str_indented(self, depth: int) -> str:
        """Return an indented string representation of this tree.

        The indentation level is specified by the <depth> parameter.
        """
        if self.is_empty():
            return ''
        else:
            str_so_far = '  ' * depth + f'{self._root}\n'
            for subtree in self._subtrees:
                # Note that the 'depth' argument to the recursive call is
                # modified.
                str_so_far += subtree._str_indented(depth + 1)
            return str_so_far

    def __str__(self) -> str:
        """Return a string representation of this tree.

        For each node, its item is printed before any of its
        descendants' items. The output is nicely indented.

        You may find this method helpful for debugging.
        """
        return self._str_indented(0).rstrip()

    def __repr__(self) -> str:
        """Return a one-line string representation of this tree.

        >>> t = Tree(2, [Tree(4, []), Tree(5, [])])
        >>> t
        Tree(2, [Tree(4, []), Tree(5, [])])
        """
        return f'Tree({self._root}, {self._subtrees})'

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

    def traverse_dec_tree(self, answers: list[str]) -> [list[Any]]:
        """
        Traverse the decision tree to determine the possible restaurant(s) that match
        the user's inputs.
        """
        current_node = self
        possible_restaurant = []

        for answer in answers[0:3]:
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
    star_rating: Optional[float]
    contact: tuple[str, str]
    coordinates: Optional[tuple[float, float]]  # (latitude, longitude)
    distance: tuple[str, float]

    def __init__(self, name: str, cuisine: str, price_range: tuple[int, int], address: str,
                 star_rating: float, contact: tuple[str, str], coordinates: tuple[float, float],
                 distance: tuple[str, float]):  # , index: int):
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
        self.contact = contact  # phone number and website
        self.price_range = price_range
        self.address = address
        self.star_rating = star_rating
        self.distance = distance  # distance from user

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
    date: str
    time: str
    more_info: list[str]

    def __init__(self, name: str, location: str, time: str, date: str, more_info: list[str]):
        """Initialize a new event with the given information

        Preconditions:
        - name != ''
        - location != ''
        """
        self.time = time
        self.date = date
        self.name = name
        self.location = location
        self.more_info = more_info


def create_event(name: str, location: str, date: str, time: str, more_info: list[str]):
    """Create an event and add it to the list of events"""
    e = Event(name=name, location=location, time=time, date=date, more_info=more_info)
    all_events.append(e)


def load_data(user: User) -> list:
    """
    Load the file data into restaurant objects.
    """
    lst = []
    for i in range(len(data)):
        rest = data.iloc[i]
        address = rest['Restaurant Address']
        lat = rest['Restaurant Latitude']
        long = rest['Restaurant Longitude']
        coordinates = (float(lat), float(long))
        name = rest['Restaurant Name']
        cuisine = rest.Category
        phone = rest['Restaurant Phone']
        pr = rest['Restaurant Price Range']
        web = rest['Restaurant Website']
        # try:
        # star_rating = get_star_rating(rest['Restaurant Yelp URL'])
        # except MissingSchema:
        # star_rating = 'NaN'

        dis = get_distance_from_user(lat, long, (user.latitude, user.longitude))
        new_restaurant = Restaurant(name=name, coordinates=coordinates, cuisine=cuisine, contact=(phone, web),
                                    price_range=pr, address=address, star_rating=0.0, distance=dis)
        lst.append(new_restaurant)
    return lst


def get_all_cuisines():
    """return a set of all the cuisines available"""
    return list(data.Category.unique())


def get_star_rating(yelp: str) -> float:
    """get the star rating from the yelp page"""
    if yelp == '':
        return 0.0
    r = requests.get(yelp)
    t = r.text
    num = t.count('label=')
    while num > 0:
        i = t.index('label=')
        if t[i + 7] in '1234567890':
            if t[i + 8] == '.':
                string = t[i + 7:i + 10]
                return float(string)
            else:
                return float(t[i + 7])
        else:
            num -= 1
            t = t[i + 1:]


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
            if len(row) != 9:
                continue
            data1 = [row[0], row[4], get_distance_from_user_original(row, (0, 0))]
            tree.insert_sequence(data1 + [row[2]])

    return tree


def build_decision_tree2(restaurants: list[Restaurant]) -> Tree:
    """Build a decision tree storing the restaurant data. This function will be used in run_restaurant_finder."""
    tree = Tree('', [])
    for rest in restaurants:
        tree.insert_sequence([rest.price_range, rest.cuisine, rest.distance[0], rest.name])
    return tree


def build_tree_w_rests(rests: list[Restaurant]) -> Tree:
    """Build a decision tree storing the restaurant data, except instead of ending with the restaurant
    name, the leaves are tuples of restaurant objects and that restaurant's index in the data file."""
    tree = Tree('', [])
    for i in range(len(rests)):
        tree.insert_sequence([rests[i].price_range, rests[i].cuisine, rests[i].distance[0], (rests[i], i)])
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


def get_distance_from_user_original(row: list[str], user_coordinates: tuple) -> str:
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


def get_distance_from_user(latitude: float, longitude: float, user_coords: tuple[float, float]) -> tuple[str, float]:
    """
    Calculate the distance from the user's location in km.
    """
    latitude1 = math.radians(latitude)
    longitude1 = math.radians(longitude)
    latitude2 = math.radians(user_coords[0])
    longitude2 = math.radians(user_coords[1])
    distance = (math.acos(math.sin(latitude1) * math.sin(latitude2) + math.cos(latitude1) * math.cos(latitude2) *
                          math.cos(longitude2 - longitude1)) * 6371)
    if distance < 1:
        return ('Under 1 km', round(distance, 4))
    elif 1 <= distance <= 5:
        return ('1-5 km', round(distance, 4))
    else:
        return ('Above 5 km', round(distance, 4))


def is_digit_or_decimal(s: str) -> bool:
    """Filler"""
    if s.startswith('-'):
        s = s[1:]

    return s.replace('.', '', 1).isdigit()





###############################
def run_restaurant_finder_test(user: User) -> list[str]:  # User object must be created first
    """
    Create a user object and find restaurants for that user based on their requirements.
    """
    # if you use the same user object you get duplicate outputs...
    lst = load_data(user)
    tree = build_tree_w_rests(lst)
    possible_rests = tree.traverse_dec_tree(user.questions)  # list[tuple[Restaurant, int]]

    if user.questions[3] != 'Any':
        if len(possible_rests) > 15:
            # for popular cuisines (like Pizza) this can be > 100 and get_star_rating will take too long to run :(
            possible_rests = possible_rests[0:15]

        load_stars(possible_rests)
        r1 = [r for r in possible_rests if r[0].star_rating is not None]
        rests = [rest for rest in r1 if math.floor(rest[0].star_rating) == int(user.questions[3][0])]
    else:
        rests = possible_rests

    # q = 'yes'
    if not rests:
        # q = 'no'
        return []
    elif len(rests) == 1:
        user.recommendations.append(rests[0][0])
        return [f'Restaurant: {rests[0][0].name}']
    else:
        resto_recs = []
        for restaurant in rests:
            user.recommendations.append(restaurant[0])
            resto_recs.append(f'Restaurant: {restaurant[0].name}\n')
            return resto_recs

    # while q == 'yes':
    #     q = input('Would you like information about any of the recommended restaurants?')
    #     if q == 'yes':
    #         get_restaurant_info(user)
    #     else:
    #         continue


def run_restaurant_finder() -> list[str]:  # User object must be created first
    """
    Create a user object and find restaurants for that user based on their requirements.
    """
    user = User()
    get_user_info(user, user.location, user.questions[1], user.questions[0], user.questions[2])
    # if you use the same user object you get duplicate outputs...
    lst = load_data(user)
    tree = build_tree_w_rests(lst)
    possible_rests = tree.traverse_dec_tree(user.questions)  # list[tuple[Restaurant, int]]

    # print('loading...')

    if user.questions[3] != 'Any':
        if len(possible_rests) > 15:
            # for popular cuisines (like Pizza) this can be > 100 and get_star_rating will take too long to run :(
            possible_rests = possible_rests[0:15]

        load_stars(possible_rests)
        r1 = [r for r in possible_rests if r[0].star_rating is not None]
        rests = [rest for rest in r1 if math.floor(rest[0].star_rating) == int(user.questions[3][0])]
    else:
        rests = possible_rests

    # q = 'yes'
    if not rests:
        return []
        # q = 'no'
    elif len(rests) == 1:
        user.recommendations.append(rests[0][0])
        return [f'Restaurant: {rests[0][0].name}']
    else:
        recommend = []
        for restaurant in rests:
            user.recommendations.append(restaurant[0])
            recommend.append(f'Restaurant: {restaurant[0].name}\n')
        return recommend

    # while q == 'yes':
    #     q = input('Would you like information about any of the recommended restaurants?')
    #     if q == 'yes':
    #         get_restaurant_info(user)
    #     else:
    #         continue


def load_stars(rests: list[tuple[Restaurant, int]]) -> None:
    """Helper function for run_restaurant_finder that loads star ratings into the Restaurant objects.
    If the star rating cannot be found, use 0.0 as a placeholder.
    """
    for r in rests:
        if 'adredir' in data.iloc[r[1]]['Restaurant Yelp URL']:
            r[0].star_rating = 0.0
        else:
            try:
                r[0].star_rating = get_star_rating(data.iloc[r[1]]['Restaurant Yelp URL'])
            except MissingSchema:
                r[0].star_rating = 0.0


def get_restaurant_info(user: User, restaurant: str, loc: bool, con: bool, review: bool) -> list:
    """Display information about the restaurant recommended by run_restaurant_finder.

    Preconditions:
    - len(lst) == len(data)
    """
    # rest = input('Enter the name of the recommended restaurant you want more information about\n')
    # location_info = input('Would you like location information? (Enter yes/no)\n')
    # contact_info = input('Would you like contact information? (Enter yes/no)\n')
    # if user.questions[3] != 'Any':
    #     review_info = input('Would you like Yelp review information? (Enter yes/no)\n')
    # else:
    #     review_info = 'no'

    # cuisine_category = user.questions[1]
    # indices = data.index[data['Category'] == cuisine_category].tolist()
    # smaller_list = lst[indices[0]:indices[len(indices) - 1] + 1]

    matches = []

    for i in user.recommendations:
        if i.name == restaurant and i.distance[0] == user.questions[2]:
            clean_ad = i.address.replace("\n", " ")
            loc_info, rev_info, con_info = '', '', ''
            if loc:
                loc_info = f'This restaurant is located {i.distance[1]} km away at {clean_ad}.'
            if con:
                con_info = f"This restaurant's phone number is {i.contact[0]}, and their website is {i.contact[1]}."
            if review:
                rev_info = f"This restaurant's Yelp rating is {i.star_rating}."
            matches.append([i, [loc_info, con_info, rev_info]])

    note = ''
    if len(matches) > 1 and all(x[1].contact[1] == y[1].contact[1] for x in matches for y in matches):
        print('Note: this restaurant has multiple locations that meet your requirements.')
    elif len(matches) > 1:
        print('Note: there are multiple restaurants with the same name that meet your requirements.')
    matches.append(note)

    return matches
    # if len(matches) == 0:
    #     print('The restaurant you provided is not one of your recommended restaurants.')


def display_map_all_rests() -> None:
    """Display an interactive map of all the restaurants in the dataset"""
    # Not sure what to do about the FutureWarning... (the problem is from setting color='Category')

    #  color_scale = [(0, 'orange'), (1, 'red')]

    fig = px.scatter_mapbox(data,
                            lat="Restaurant Latitude",
                            lon="Restaurant Longitude",
                            hover_name="Restaurant Name",
                            hover_data=["Restaurant Name", "Category"],
                            color="Category",
                            # color_continuous_scale=color_scale,
                            # size="Listed",
                            zoom=8,
                            height=800,
                            width=1300)

    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.show()


def display_map_recommended(u: User) -> None:
    """Display an interactive map of the user's recommended restaurants from the dataset."""

    lst = load_data(u)
    tree = build_tree_w_rests(lst)
    rests = tree.traverse_dec_tree(u.questions)
    indices = [restaurant[1] for restaurant in rests]

    new_df = data.iloc[[indices[0]]]

    for i in indices[1:]:
        current_row = data.iloc[[i]]
        new_df = pd.concat([current_row, new_df])

    fig = px.scatter_mapbox(new_df,
                            lat="Restaurant Latitude",
                            lon="Restaurant Longitude",
                            hover_name="Restaurant Name",
                            hover_data=["Restaurant Name", "Category"],
                            color="Category",
                            # color_continuous_scale=color_scale,
                            # size="Listed",
                            zoom=8,
                            height=800,
                            width=1300)

    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.show()


# TEST WITH:
# u = User()
# get_user_info(u)
#
# restaurant_objs = load_data(u)
# x = build_decision_tree2(restaurant_objs)
# x.traverse_dec_tree(u.questions)
#
# get_restaurant_info(restaurant_objs, u)  #the restaurant name you enter must be exactly as it appears in the csv file
#
# run with: run_restaurant_finder(u)

# array = []
# for i in range(15821):
# rest = data.iloc[i]
# if 'adredir' in rest['Restaurant Yelp URL']:
# array.append('NaN')
# else:
# try:
# star_rating = get_star_rating(rest['Restaurant Yelp URL'])
# array.append(star_rating)
# except MissingSchema:
# star_rating = 'NaN'
# array.append(star_rating)

# print(array)
