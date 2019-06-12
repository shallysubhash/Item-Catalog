from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from database_setup import Category, Item, Base

engine = create_engine('sqlite:///itemcatalog.db')

# Clear database
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()


# Books for Tolstoy
category1 = Category(name="Tolstoy")

session.add(category1)
session.commit()

item1 = Item(name="War and Peace",  description="year_written: 1865,",
             category=category1, user_name="Shallysubhash")

session.add(item1)
session.commit()

item2 = Item(name="Anna Karenina",   description="year_written: 1875",
             category=category1, user_name="Shallysubhash")

session.add(item2)
session.commit()

item3 = Item(name="The Death of Ivan Ilyich",
             description="Another of Tolstoy’s celebrated novellas",
             category=category1, user_name="Shallysubhash")

session.add(item3)
session.commit()

item3 = Item(name="The Cossacks",
             description="Originally entitled ‘Young Manhood’"
             "this short novel follows nobleman Dmitri Olenin who",
             category=category1,
             user_name="Shallysubhash")

session.add(item3)
session.commit()

item3 = Item(name="The Kingdom of God Is Within You",
             description="Tolstoy’s 1894 philosophical treatise",
             category=category1, user_name="Shallysubhash")

session.add(item3)
session.commit()


# books for Woolf, Virginia
category2 = Category(name="Woolf, Virginia")

session.add(category2)
session.commit()

item1 = Item(name="Mrs. Dalloway",
             description="Mrs. Dalloway is one of the best books to start with"
             "for those who are only just encountering"
             " Virginia Woolf’s writing",
             category=category2,
             user_name="Shallysubhash")

session.add(item1)
session.commit()

item2 = Item(name="Orlando: A Biography",
             description="Orlando is an enthralling yet accessible read."
             "It starts with a male protagonist, an aristocratic poet"
             "who frequents Queen Elizabeth’s court.",
             category=category2,
             user_name="Shallysubhash")

session.add(item2)
session.commit()

item3 = Item(name="To the Lighthouse",
             description="The story of three members of the Ramsay family,"
             " told from their varying perspectives",
             category=category2,
             user_name="Shallysubhash")

session.add(item3)
session.commit()


categories = session.query(Category).all()
for category in categories:
    print ("Category: " + category.name)
