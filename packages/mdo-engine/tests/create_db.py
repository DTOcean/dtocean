# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 15:31:18 2015

@author: Mathew Topper
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Float, Integer, String

if os.path.isfile("test.db"): os.remove("test.db")
engine = create_engine('sqlite:///test.db', echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Ship(Base):
    
     __tablename__ = 'ships'

     id = Column(Integer, primary_key=True)
     name = Column(String)
     length = Column(Float)
     beam = Column(Float)
     draft = Column(Float)
     tonnage = Column(Float)

     def __repr__(self):
        return ("<User(name='{}', length='{}', beam='{}', "
                "draft ='{}', tonnage='{}')>").format(self.name,
                                                      self.length,
                                                      self.beam,
                                                      self.draft,
                                                      self.tonnage)
                                                      
Base.metadata.create_all(engine) 
                                                      
def add_ships():
    
    session = Session()
    
    big_ship = Ship(name='Titanic',
                    length=269.1,
                    beam=28.0,
                    draft=10.5,
                    tonnage=46328.
                    )
                
    little_ship = Ship(name='Maid of the Loch',
                    length=58.2,
                    beam=8.6,
                    draft=1.37,
                    tonnage=555.
                    )
                    
    session.add(big_ship)
    session.add(little_ship)
    session.commit()
    
    return 

