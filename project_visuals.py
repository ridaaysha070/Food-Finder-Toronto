"""Graphical User Interface for Project 2"""

import tkinter as tk
from tkinter import ttk
import updated_april3

U = updated_april3.User()


class Home:
    """Homepage that will open upon running the program"""
    def __init__(self):
        """Create a home window"""
        self.homepage = tk.Tk()
        self.homepage.geometry("400x400")
        self.homepage.title("Food Finder Home")

        self.hometitle = tk.Label(self.homepage, text="Toronto Food Finder Home", font=('Arial', 20))
        self.hometitle.pack(pady=40)
        self.find_restaurant = tk.Button(self.homepage, text='Find restaurants', font=('Arial', 14),
                                         command=RestaurantFinder)
        self.find_restaurant.pack(pady=10)
        self.find_events = tk.Button(self.homepage, text='See events', font=('Arial', 14))
        self.find_events.pack(pady=10)
        self.create_event = tk.Button(self.homepage, text='Create an event', font=('Arial', 14))
        self.create_event.pack(pady=10)

        self.homepage.mainloop()


class RestaurantFinder:
    """Create a window in which the restaurant finder runs, called when the 'Find restaurants' button is clicked"""
    def __init__(self):
        self.restofinder = tk.Tk()
        self.restofinder.geometry("500x600")
        self.restofinder.title("Restaurant Searcher")

        self.user_address_prompt = tk.Label(self.restofinder, font=("Arial", 14),
                                            text='Enter your address in the form 123 xyz St, Toronto, Ontario')
        self.user_address_prompt.pack(pady=20)
        self.user_address = tk.Entry(self.restofinder, font=("Arial", 12))
        self.user_address.pack(pady=10)

        frame = tk.Frame(self.restofinder)
        l1 = tk.Label(frame, text='Select cuisine')
        l1.grid(row=0, column=0)
        course = updated_april3.get_all_cuisines()
        self.cuisines = tk.ttk.Combobox(frame, value=course, width=10)
        self.cuisines.grid(row=1, column=0)
        frame.pack(pady=20)

        # self.price_range = tk.ttk.Combobox(frame, value=['Under $10', '$11-30', '$31-60', 'Above $61'], width=10)

        frame2 = tk.Frame(self.restofinder)
        l2 = tk.Label(frame2, text='Select price range')
        l2.grid(row=0, column=0)
        self.price_range = tk.ttk.Combobox(frame2, value=['Under $10', '$11-30', '$31-60', 'Above $61'], width=10)
        self.price_range.grid(row=1, column=0)
        frame2.pack(pady=20)

        frame3 = tk.Frame(self.restofinder)
        l3 = tk.Label(frame3, text='Select distance from the given address')
        l3.grid(row=0, column=0)
        self.distance = tk.ttk.Combobox(frame3, value=['Under 1 km', '1-5 km', 'Above 5 km'], width=10)
        self.distance.grid(row=1, column=0)
        frame3.pack(pady=20)

        frame4 = tk.Frame(self.restofinder)
        l4 = tk.Label(frame4, text='Select a Yelp star rating')
        l4.grid(row=0, column=0)
        self.star = tk.ttk.Combobox(frame4, value=['Any', '1 star', ' 2 stars', '3 stars', '4 stars', '5 stars'], width=10)
        self.star.grid(row=1, column=0)
        frame4.pack(pady=20)

        self.search = tk.Button(self.restofinder, text="Search restaurants", command=self.save)
        self.search.pack(pady=20)

        self.restofinder.mainloop()

    def save(self):
        """save the entered addresss"""
        self.user_ad = self.user_address.get()
        self.selected_cuis = self.cuisines.get()
        self.selected_price_range = self.price_range.get()
        self.selected_distance = self.distance.get()
        self.selected_star = self.star.get()
        U.questions = [self.selected_price_range, self.selected_cuis, self.selected_cuis, self.selected_star]
        U.location = self.user_ad
        U.latitude = updated_april3.get_coords(U.location)[0]
        U.longitude = updated_april3.get_coords(U.location)[1]


        if any(x == '' for x in [self.user_ad, self.selected_cuis, self.selected_price_range, self.selected_distance]):
            tk.Label(self.restofinder, text='Please fill all criteria').pack(pady=20)
        else:
            temp = updated_april3.get_user_info(U, location=self.user_ad, distance=self.selected_distance,
                                                cuisine=self.selected_cuis, price=self.selected_price_range, star=
                                                self.selected_star)
            if temp:
                tk.Label(self.restofinder, text='Invalid address').pack()
            else:
                self.show_restaurants()

    def show_restaurants(self):
        """Show the restaurants meeting the user's criteria"""
        self.recommended_restaurants = updated_april3.run_restaurant_finder()

        if len(self.recommended_restaurants) == 0:
            (tk.Label(self.restofinder, text='No restaurants found, please edit your search requirements', font=18)
             .pack(padx=20))
        else:
            tk.Label(self.restofinder, text='Restaurants found:', font=18).pack(padx=20)
            for r in self.recommended_restaurants:
                resto_name = r[12:len(r) - 1]
                tk.Label(self.restofinder, text=resto_name, font=14).pack()
                tk.Button(self.restofinder, text='More Info', font=12, command=self.get_resto_info(resto_name)).pack()

    def get_resto_info(self, name: str):
        """Run the restaurant finder from the backend file"""
        more_info = tk.Tk()
        more_info.title(name)

        l, c, r = tk.IntVar(), tk.IntVar(), tk.IntVar()

        location = tk.Checkbutton(more_info, text='Location', variable=l)
        location.pack()
        contact = tk.Checkbutton(more_info, text='Contact Information', variable=c)
        contact.pack()
        review = tk.Checkbutton(more_info, text='Review Information', variable=r)
        review.pack()

        matches = updated_april3.get_restaurant_info(user=U, restaurant=name, loc=(location == 1), con=(contact == 1),
                                                     review=(review == 1))
        for m in matches[:len(matches) - 1]:
            tk.Label(self.restofinder, text=m[0], font=14).pack()
            for n in m[1]:
                if n:
                    tk.Label(self.restofinder, text=n, font=12).pack()
        if matches[len(matches) - 1]:
            tk.Label(self.restofinder, text=matches[len(matches) - 1], font=14).pack()
