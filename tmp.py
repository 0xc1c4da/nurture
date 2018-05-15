# random thoughts and garbage

person = {
    created: datetime,
    last_touched: datetime.utcnow(), # when referenced in a note, touched
    first_name: '',
    last_name: '', # could be missing
    # contact info,
    # age/birthdate,
    # pictures: []
    # male: True
}

note = {
    location: (string, []),
    note : '',
    tags: [],
    people: [],
    reminder: '',
    created: datetime
}

relationships = [[person1, person2]]

person = {
    name: 'Jarrad',
    age: '31?', # string but attempt parse date
    male: True,
    notes: [
        [datetime.utcnow(), 'How we met?', ['history']],
        [datetime.utcnow(), 'Gift Ideas?', ['gift']],
        [datetime.utcnow(), 'Food Preferences?', ['preferences']],
        [datetime.utcnow(), 'I owe him something', ['debt']],
        [datetime.utcnow(), 'Likes to do?', ['preferences']],
        [datetime.utcnow(), 'What did we talk about and where?', ['contact']],
        [datetime.utcnow(), 'buy him a present', ['gift'], new Reminder('datetime in future', 'recurrance info')]
    ], 
    tags: [],
    contact_info: ['email', 'whatsapp', 'telegram', 'phone'],
    relationships: [
        ['FooPerson', 10 , ['business','friend']],
        ['SomeDog', 7, ['pet']]
    ], # 10 is a rank of relationship importance 0-10
    last_touched: datetime.utcnow(),
    pictures: [] # profile pic/gallery images

}
# foo bar blah blah #monkey #butt with @Turtle @BlahMan @FooPerson; New York, United States
activity = {
    date: datetime.utcnow(),
    location: 'coordinates/address?', # Where I'm at? 
    note: 'what we did?',
    tags: ['hangout'],
    who_involved: ['FooPerson', 'Jarrad'], # I just connected with?
    thoughts: 'how did I feel about this?' # What do I want to remember?
}

# remind when haven't done activity with them in awhile
# votre.me style journal that auto creates notes for people?
# make these as reminders for notes/relationships to fill
age/birthday
how we met?
gift ideas?
how they spend their time?
who is there best friend?
where they live?
where they work?
what they do?
what they need
what they are going throug
what are their pet peeves?
what are their goals/ambitions in life?
# Relationships
# come up with questions for people, to find loves or mentorship
significant other
spouse
date
lover
is in love with
secret lover
ex-boyfriend/ex-girlfriend
father/mother
son/daughter
brother/sister
grand parent
grand child
uncle/aunt
nephew/niece
cousin
godfather/godmother
godson/goddaughter
friend
best friend
colleague
boss
subordinate
mentor
protege
