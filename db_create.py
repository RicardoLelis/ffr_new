from project import db
from project.models import Recipe, User

# Drop all of the existing database tables
db.drop_all()

# Create the database and the database table
db.create_all()

# Insert user data
user1 = User('patkennedy79@gmail.com', 'password1234')
user2 = User('kennedyfamilyrecipes@gmail.com', 'PaSsWoRd')
user3 = User('blaa@blaa.com', 'MyFavPassword')
admin_user = User(email='ricardo.lelis3@gmail.com', plaintext_password='qweasd', role='admin')
db.session.add(admin_user)
db.session.add(user1)
db.session.add(user2)
db.session.add(user3)

# Insert recipe data
recipe1 = Recipe('Slow-Cooker Tacos', 'Delicious ground beef that has been simmering in taco seasoning and sauce.  Perfect with hard-shelled tortillas!', admin_user.id, False)
recipe2 = Recipe('Hamburgers', 'Classic dish elivated with pretzel buns.', admin_user.id, True)
recipe3 = Recipe('Mediterranean Chicken', 'Grilled chicken served with pitas, hummus, and sauted vegetables.', user1.id, True)
db.session.add(recipe1)
db.session.add(recipe2)
db.session.add(recipe3)

# Commit the changes
db.session.commit()
