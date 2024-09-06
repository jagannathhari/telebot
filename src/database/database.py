
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    user_name = Column(String, nullable=False)
    groups= relationship('Group', back_populates='user')

class Group(Base):
    __tablename__ = 'groups'

    group_id= Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    group_name = Column(String, nullable=False)
    total_members = Column(Integer)

    user = relationship('User', back_populates='groups')
def user_exists_by_id(session, user_id):
    if get_user_by_id(session,user_id):
        return True
    return False

def get_group(session,user_id):
    user = session.query(User).filter_by(user_id=user_id).one()
    return [i.group_name for i in user.groups]

def get_user_by_id(session,user_id):
    return session.query(User).filter_by(user_id=user_id).first()


engine = create_engine('sqlite:///users.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
