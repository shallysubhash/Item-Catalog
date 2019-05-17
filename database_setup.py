import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()

 
class Category(Base):
    __tablename__ = 'Category'
   
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
       
           return {
               'id'    : self.id,
               'name'  : self.name
           }
 
 
class Item(Base):
    __tablename__ = 'Item'


    name =Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    description = Column(String(250))
    Category_id = Column(Integer,ForeignKey('Category.id'))
    category  = relationship(Category, cascade="save-update, merge, delete") 
    user_name = Column(String(250), nullable=False)
    

#We added this serialize function to be able to send JSON objects in a serializable format
    @property
    def serialize(self):
       
       return {
           'category'         : self.category.name,
           'description'      : self.description,
           'name'             : self.name
       }
 

engine = create_engine('sqlite:///itemcatalog.db')
 

Base.metadata.create_all(engine)