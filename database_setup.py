import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import backref

Base = declarative_base()


### setup tables

class db_User(Base):

    __tablename__ = 'db_user'

    id = Column(Integer, primary_key = True)
    name = Column(String(250), nullable = False)
    email = Column(String(250), nullable = False)
    experience = Column(String(80), nullable = False)

    @property
    def serialize(self):
        return {
        'id' : self.id,
        'name' : self.name,
        'email' :  self.email,
        'experience' :  self.experience
        }




class Category(Base):

    __tablename__ = 'category'

    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    description = Column(String(250), nullable = False)
    user_id = Column(Integer, ForeignKey('db_user.id'))
    user = relationship(db_User)


    @property
    def serialize(self):
        return {
        'id' : self.id,
        'name' : self.name,
        'description' :  self.description,
        'user_id ':  self.user_id
        }


class Item(Base):

    __tablename__ = 'catalog_items'

    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    description = Column(String(250))
    price = Column(String(80))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category, single_parent=True, backref=backref("catalog-items", cascade="all,delete"))
     # show = db.relationship('Show',
     #                       backref=db.backref('episodes', cascade="all, delete-orphan"),
     #                       lazy='joined')
    user_id = Column(Integer, ForeignKey('db_user.id'))
    user = relationship(db_User)

    @property
    def serialize(self):
        return {
        'id' : self.id,
        'name' : self.name,
        'desciption' :  self.description,
        'price':  self.price,
        'category_id' : self.category_id,
        'user_id' : self.user_id
        }


##### ending
engine = create_engine('postgresql:///blanks')
#Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)