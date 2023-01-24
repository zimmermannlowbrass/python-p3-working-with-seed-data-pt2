# Working with Seed Data, Part 2

## Learning Goals

- Use seed data to populate a database containing one-to-many and many-to-many
  relationships.

***

## Key Vocab

- **Schema**: the blueprint of a database. Describes how data relates to other
  data in tables, columns, and relationships between them.
- **Persist**: save a schema in a database.
- **Engine**: a Python object that translates SQL to Python and vice-versa.
- **Session**: a Python object that uses an engine to allow us to
  programmatically interact with a database.
- **Transaction**: a strategy for executing database statements such that
  the group succeeds or fails as a unit.
- **Migration**: the process of moving data from one or more databases to one
  or more target databases.
- **Seed**: to fill a database with an initial set of data.

***

## Introduction

What good is a database without any data? In the previous module, we learned
how to create fake data using Faker and the SQLAlchemy ORM in Python scripts.
Remember that we refer to the process of adding sample data to the database as
**"seeding"** the database. In the previous lesson on seeding, we focused on
simple, unrelated data. In this lesson, we will focus on populating databases
with one-to-many and many-to-many relationships.

This lesson is set up as a code-along, so make sure to fork and clone the
lesson. Then run these commands to set up the dependencies and set up the
database:

```console
$ pipenv install; pipenv shell

# => Installing dependencies from Pipfile.lock (xxxxxx)...
# =>   🐍   ▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉ X/X — XX:XX:XX
# => To activate this projects virtualenv, run pipenv shell.
# => Alternatively, run a command inside the virtualenv with pipenv run.
# => Launching subshell in virtual environment...
# =>  . /python-p3-working-with-seed-data-pt2/.venv/bin/activate
# => $  . /python-p3-working-with-seed-data-pt2/.venv/bin/activate

$ cd lib
$ alembic upgrade head
```

In this application, we have two migrations: one for our declarative `Base`,
and a second for three tables: `games`, `reviews`, and `users`. Due to the
added complexity of the relationships, we're keeping these tables as simple as
possible- this means we won't be using Faker, but it's available to you in your
pipenv if you want to build out your database a bit more on your own.

```py
# models.py

class Game(Base):
    __tablename__ = 'games'

    id = Column(Integer(), primary_key=True)

    reviews = relationship('Review', backref='game')
    users = association_proxy('reviews', 'user',
        creator=lambda us: Review(user=us))

    def __repr__(self):
        return f'Game(id={self.id})'

class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer(), primary_key=True)

    game_id = Column(Integer(), ForeignKey('games.id'))
    user_id = Column(Integer(), ForeignKey('users.id'))

    def __repr__(self):
       return f'Review(id={self.id})'

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer(), primary_key=True)

    reviews = relationship('Review', backref='user')
    games = association_proxy('reviews', 'games',
        creator=lambda gm: Review(game=gm))

    def __repr__(self):
       return f'User(id={self.id})'

```

***

## Creating Our Records

We're going to start off our seed file just as we did in the last module:
by creating records. To keep our code organized, let's break the functionality
into separate functions:

```py
#!/usr/bin/env python3

from random import choice as rc

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Game, Review, User

engine = create_engine('sqlite:///seed_db.db')
Session = sessionmaker(bind=engine)
session = Session()

def create_games():
    games = [Game() for i in range(100)]
    session.add_all(games)
    session.commit()
    return games

def create_reviews():
    reviews = [Review() for i in range(1000)]
    session.add_all(reviews)
    session.commit()
    return reviews

def create_users():
    users = [User() for i in range(500)]
    session.add_all(users)
    session.commit()
    return users

if __name__ == '__main__':
    games = create_games()
    reviews = create_reviews()
    users = create_users()

```

Here, we create a session object and use it to generate different nnumbers of
records. It's usually a good idea to keep this realistic- there will probably
be more reviews than users and more users than games. With that in mind, we
created 1000, 500, and 100, respectively.

Each set of creations is broken into a separate function here. These are very
simple functions and could be refactored into a single function if desired,
but this may negatively impact readability and scalability. The choice is
ultimately yours!

```py

...

def create_records():
    games = [Game() for i in range(100)]
    reviews = [Review() for i in range(1000)]
    users = [User() for i in range(500)]
    session.add_all(games + reviews + users)
    session.commit()
    return games, reviews, users

if __name__ == '__main__':
    games, reviews, users = create_records()

```

Run `python seed.py` and navigate to `seed_db.db`. You should see records in all
three tables!

### Clearing the Database

Let's make one last change before we continue. When we seed a database, we want
the database to contain new data _and only new data_. This means that we need to
delete all records before we begin seeding.

```py

...

def delete_records():
    session.query(Game).delete()
    session.query(Review).delete()
    session.query(User).delete()
    session.commit()

if __name__ == '__main__':
    delete_records()
    games, reviews, users = create_records()

```

***

## Building Relationships

In the models provided, there are two one-to-many relationships (games and
reviews, users and reviews) and one many-to-many relationship (games and users).
Building out one-to-many relationships is simple: just add one to the other.
Remember that the "one" will contain a `list` attribute of the many, where the
"many" will simply contain a reference to the "one" object.

### One-to-Many

We can use the `random.choice()` method (aliased as `rc`) to assign users and
games to reviews:

```py

...

def relate_one_to_many(games, reviews, users):
    for review in reviews:
        review.user = rc(users)
        review.game = rc(games)
    
    session.add_all(reviews)
    session.commit()
    return games, reviews, users

if __name__ == '__main__':
    delete_records()
    games, reviews, users = create_records()
    games, reviews, users = relate_one_to_many(games, reviews, users)

```

Run `python seed.py` and reopen `seed_db.db` (you may need to close it first),
and you should see that the `reviews` table now has `user_id`s and `game_id`s
associated with each review!

### Many-to-Many

We've just added 

<details>
  <summary>
    <em>What do we call the syntax that we used to create the <code>games</code>
        variable?</em>
  </summary>

  <h3>List Interpretation.</h3>
  <p>Interpretations allow us to create lists without using loops. They're a
     powerful staple of Python code, so make sure you don't forget!</p>
</details>
<br/>

***

## Conclusion

In this lesson, we learned the importance of having a seed file along with our
database migrations in order for ourselves and other developers to quickly set
up the database with sample data. We also learned how to use the Faker library
to quickly generate randomized seed data.

***

## Resources

- [SQLAlchemy ORM Documentation][sqlaorm]
- [Faker Documentation][faker]
- [random — Generate pseudo-random numbers - Python](https://docs.python.org/3/library/random.html)

[faker]: https://faker.readthedocs.io/en/master/index.html]
[sqlaorm]: https://docs.sqlalchemy.org/en/14/orm/
