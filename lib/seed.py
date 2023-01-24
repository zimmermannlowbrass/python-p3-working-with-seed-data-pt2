#!/usr/bin/env python3

from random import choice as rc

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Game, Review, User

engine = create_engine('sqlite:///seed_db.db')
Session = sessionmaker(bind=engine)
session = Session()

def create_records():
    games = [Game() for i in range(100)]
    reviews = [Review() for i in range(1000)]
    users = [User() for i in range(500)]
    session.add_all(games + reviews + users)
    session.commit()
    return games, reviews, users

def delete_records():
    session.query(Game).delete()
    session.query(Review).delete()
    session.query(User).delete()
    session.commit()

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
