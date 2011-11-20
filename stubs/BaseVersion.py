#
#
# This file was autogenerated by python_on_wheels.
# But YOU CAN EDIT THIS FILE SAFELY
# It will not be overwtitten by python_on_wheels
# 


from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import mapper
from sqlalchemy.orm import sessionmaker

import sys,os

sys.path.append(os.path.normpath("../lib"))
import powlib
from PowAppObject import PowAppObject

x = PowAppObject()

Base = declarative_base(bind=x.__engine__, metadata = x.__metadata__)
Base.metadata.reflect()

class BaseVersion(Base):
	__table__ = Base.metadata.tables['versions']
	pao = x
	#__mapper_args__ = {}
	session = x.getSession()
	
	def __init__(self):
		self.session = self.pao.getSession()

	def update(self):
		self.session.merge(self)
		self.session.commit()