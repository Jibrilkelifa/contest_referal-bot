import dataset

db = dataset.connect('sqlite:///contest.db')
contests = db['contests']
participants = db['participants']
invitations = db['invitations']
