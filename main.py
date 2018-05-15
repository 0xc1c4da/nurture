# TODO reminders
# https://developers.google.com/calendar/recurringevents

# TODO build graph
# TODO search on location
# TODO search on haven't low interactions
# TODO search on haven't interacted in awhile
# TODO search on graph properties, things like not well connected

# Example
# use @me for me to make social graph connections
# Remind @CarlBennetts about #ethereum in two weeks; Athens, Greece

import os
import re
import geocoder
from datetime import datetime
import shelve
from recurrent import RecurringEvent
from random import sample
from string import ascii_lowercase
import networkx as nx

os.environ['KIVY_METRICS_DENSITY'] = '2'
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.garden.navigationdrawer import NavigationDrawer

# https://networkx.github.io/documentation/networkx-1.10/tutorial/tutorial.html
# https://networkx.github.io/documentation/networkx-1.9/examples/drawing/weighted_graph.html
G = nx.MultiDiGraph() # DiGraph? unsure how this would work, parallels edges could be thoughts?


class Thought:
    ''' Datastructure for a Thought '''
    def __init__(self, thought='', tags=[], people=[], reminder=None, location=None, created=datetime.utcnow(), modified=datetime.utcnow()):
        self.thought = thought
        self.tags = tags
        self.people = people
        self.reminder = reminder
        self.created = created
        self.modified = modified

class Person:
    ''' Datastructure for a Person '''
    def __init__(self, shortname, first_name='', middle_name='', last_name='', is_male=True, birth_date='', info='', created=datetime.utcnow(), modified=datetime.utcnow()):
        self.short_name = shortname
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.is_male = is_male
        self.birth_date = birth_date
        self.info = info
        self.created = created
        self.modified = modified
        if not first_name and not last_name:
            name = re.sub('(?!^)([A-Z][a-z]+)', r' \1', shortname.strip("@")).split()
            self.first_name = name[0]
            try:
                self.last_name = name[1]
            except:
                pass


class AutoCompleteInput(TextInput):
    ''' Custom TextInput that supports autocomplete '''
    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        ''' Add support for tab or spacebar as an 'autocomplete' using the suggestion text. '''
        if self.suggestion_text and (keycode[1] == 'spacebar' or keycode[1] == 'tab'):
            self.insert_text(self.suggestion_text + ' ')
            return True
        elif keycode[1] == 'tab' or keycode[1] == 'enter': # Block tabs and enter from input
            return False
        return super(AutoCompleteInput, self).keyboard_on_key_down(window, keycode, text, modifiers)

class Sidebar(BoxLayout):

    def populate(self, person, db):
        self.ids.short_name.text = person.short_name
        self.ids.first_name.text = person.first_name
        self.ids.middle_name.text = person.middle_name
        self.ids.last_name.text = person.last_name
        self.ids.is_male.active = person.is_male
        self.ids.birth_date.text = person.birth_date
        self.ids.info.text = person.info

        last_touch = None
        for t in db['thoughts']:
            if person.short_name in t.people:
                last_touch = t.created
                break
        delta = datetime.utcnow() - last_touch
        self.ids.last_interaction.text = "{} days\nsince contact".format(delta.days)

    def __init__(self, **kwargs):
        super(Sidebar, self).__init__(**kwargs)

class Nurture(BoxLayout):
    ''' Main screen, lists all thoughts, search and thought input '''
    drawer = None
    sidebar = None
    dbf = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'nurture.shelve')

    def on_search(self, term, tapped):
        ''' Display person screen or search hashtag when tapped '''
        term = term.strip()
        if (len(term)>2):
            self.ids.search_input.text = term
            if term.startswith('@'):
                if tapped:
                    with shelve.open(self.dbf) as db:
                        if term in db:
                            self.drawer.toggle_state()
                            self.sidebar.populate(db[term], db)
                # TODO handle multiple people
                self.populate(term)
            elif term.startswith('#'):
                # TODO support multiple hashtags
                self.populate(hashtags=term)
            elif term.startswith(';'):
                # TODO search for location
                pass
            else:
                self.populate(term) # TODO make general search in note
        else:
            self.populate()

    def on_text(self, txt):
        ''' Search known terms and display suggestion text '''
        with shelve.open(self.dbf) as db:
            value = txt.text
            txt.suggestion_text = ''
            word_list = list(set(
                db.get('known_terms', []) + value[:value.rfind(' ')].split(' ')))
            val = value[value.rfind(' ') + 1:]
            if not val:
                return
            try:
                word = [word for word in word_list
                        if word.startswith(val)][0][len(val):]
                if not word:
                    return
                txt.suggestion_text = word
            except IndexError:
                pass

    def highlight_terms(self, haystack, terms, colour):
        ''' Colour a thought's hashtags and shortnames for display '''
        tmp = haystack.split(' ')
        for t in terms:
            if t in tmp:
                tmp[tmp.index(t)] =  '[ref={0}][b][color={1}]{0}[/color][/b][/ref]'.format(t, colour)
        return ' '.join(tmp)

    def save(self, instance, state):
        if state == 'closed':
            with shelve.open(self.dbf, writeback=True) as db:
                person = db[self.sidebar.ids.short_name.text]
                if person:
                    person.first_name = self.sidebar.ids.first_name.text
                    person.middle_name = self.sidebar.ids.middle_name.text
                    person.last_name = self.sidebar.ids.last_name.text
                    person.birth_date = self.sidebar.ids.birth_date.text
                    person.info = self.sidebar.ids.info.text
                    person.is_male = self.sidebar.ids.is_male.active

    def insert(self, value):
        ''' A new thought to be inserted, parses thought input and extracts hashtags, people, reminder and location '''
        with shelve.open(self.dbf, writeback=True) as db:
            thought = value

            # Get Location
            location = None
            if ';' in value:
                thought, _, location = value.rpartition(';')
                location = location.strip()
                g = geocoder.google(location)
                if g.latlng is None:
                    print('Trying OSM')
                    g = geocoder.osm(location)
                location = (location, g.latlng)

            # Prase Recurring event
            r = RecurringEvent() # read more here https://github.com/kvh/recurrent
            print(r.parse(thought))

            # Colour Hashtags
            hashtags = {tag for tag in thought.split() if tag.startswith("#")}
            thought = self.highlight_terms(thought, hashtags, 'ffdc00')
            # Colour People
            people = {tag for tag in thought.split() if tag.startswith("@")}
            thought = self.highlight_terms(thought, people, '7fdbff')

            # Create People who don't exist
            for person in people:
                if person not in db:
                    db[person] = Person(person)
                    
            # Cleanup
            value = thought
            if location:
                value += '; ' + location

            # Save Thought to DB
            db['known_terms'] = list(set(db.get('known_terms', []) + list(hashtags) + list(people)))
            t = Thought(value, hashtags, people, r, location)
            db['thoughts'] = db.get('thoughts', [])
            db['thoughts'].insert(0, t)
            # Insert into UI
            self.rv.data.insert(0, {'value': value or 'empty thought'})

    def populate(self, term=None, hashtags=None):
        ''' Load any thoughts and populate list '''
        with shelve.open(self.dbf) as db:
            thoughts = db.get('thoughts', [])
            if thoughts:
                if hashtags:
                    # TODO support multiple hashtags
                    self.rv.data = [{'value': t.thought}
                                    for t in thoughts if (hashtags in t.tags)]
                    if len(self.rv.data) == 0:
                        # incomplete hashtag, search as normal
                        self.rv.data = [{'value': t.thought}
                                    for t in thoughts if (hashtags in t.thought)]
                elif term:
                    self.rv.data = [{'value': t.thought}
                                    for t in thoughts if (term in t.thought)]
                else:
                    self.rv.data = [{'value': t.thought}
                                    for t in thoughts]

    def __init__(self, drawer, sidebar, **kwargs):
        super(Nurture, self).__init__(**kwargs)
        self.drawer = drawer
        self.sidebar = sidebar
        self.populate()

    # def sort(self):
    #     self.rv.data = sorted(self.rv.data, key=lambda x: x['value'])

    def clear(self):
        self.rv.data = []

    # def insert(self, value):
    #     self.rv.data.insert(0, {'value': value or 'default value'})

    # def update(self, value):
    #     if self.rv.data:
    #         self.rv.data[0]['value'] = value or 'default new value'
    #         self.rv.refresh_from_data()

    # def remove(self):
    #     if self.rv.data:
    #         self.rv.data.pop(0)


class NurtureApp(App):
    def build(self):
        Window.size = (1200, 1600)

        # Setup Navigation Drawer UI and relationships
        drawer = NavigationDrawer()
        sidebar = Sidebar()
        drawer.anim_type = 'slide_above_anim'    
        drawer.add_widget(sidebar)
        nurture =Nurture(drawer, sidebar)
        drawer.bind(state=nurture.save)
        drawer.add_widget(nurture)

        return drawer

if __name__ == '__main__':
    NurtureApp().run()
