from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Item, db_User, Base

def createData():

    engine = create_engine('postgresql:///blanks')
    # Bind the engine to the metadata of the Base class so that the
    # declaratives can be accessed through a DBSession instance
    Base.metadata.bind = engine

    DBSession = sessionmaker(bind=engine)
    # A DBSession() instance establishes all conversations with the database
    # and represents a "staging zone" for all the objects loaded into the
    # database session object. Any change made against the objects in the
    # session won't be persisted into the database until you call
    # session.commit(). If you're not happy about the changes, you can
    # revert all of them back to the last commit by calling
    # session.rollback()
    session = DBSession()

    #create User 1

    Johnny = db_User(name = 'Johnny J', email = 'johnnyjannetto@icloud.com', experience = 'Just a dreamer')


    # create intial categories...

    Shortboards = Category(name = 'Shortboards', description = 'little rippers, happy hacking', user_id = 1)

    Longboards = Category(name = 'Longboards', description = 'For most beautiful sliding', user_id = 1)

    Fish = Category(name = 'Fish', description = 'Not a marine invertebrate', user_id = 1)

    MiniSimmons = Category(name = 'MiniSimmons', description = 'possibly not invented by Simmons', user_id = 1)


    # create shortboard example

    fivesix = Item(name = 'FiveSix', description = 'A short thin little guy', price = '$12.00', category_id = 1, user_id = 1)

    session.add(Johnny)
    session.add(Shortboards)
    session.add(Longboards)
    session.add(Fish)
    session.add(MiniSimmons)
    session.add(fivesix)
    session.commit()

    print "added some blanks and categories!"