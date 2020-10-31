import sqlalchemy as sq
from sqlalchemy import ForeignKey, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# username = 'postgres'
# password = 'gfhfif777'
# db_name = 'VK'
from TOKENS import username, password, db_name

engine = sq.create_engine(f'postgresql+psycopg2://{username}:{password}@localhost:5432/{db_name}')
connection = engine.connect()
Session = sessionmaker(bind=engine)
Session.configure(bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = sq.Column(sq.INTEGER, primary_key = True)
    name = sq.Column(sq.String)
    second_name = sq.Column(sq.String)
    age = sq.Column(sq.INTEGER)
    age_range_from = sq.Column(sq.INTEGER)
    age_range_to = sq.Column(sq.INTEGER)
    sex = sq.Column(sq.String)
    city = sq.Column(sq.String)
    dating_user = relationship('DatingUser', backref='user')

class DatingUser(Base):
    __tablename__ = 'datingUser'
    id = sq.Column(sq.INTEGER, primary_key=True, unique=True)
    name = sq.Column(sq.String)
    second_name = sq.Column(sq.String)
    age = sq.Column(sq.INTEGER)
    user_id = sq.Column(sq.INTEGER, ForeignKey('user.id'))
    photo = relationship('Photo', backref='datingUser')

class Photo(Base):
    __tablename__ = 'photo'
    id = sq.Column(sq.INTEGER, primary_key=True)
    link = sq.Column(sq.String)
    likes_count = sq.Column(sq.INTEGER)
    dating_id = sq.Column(sq.INTEGER, ForeignKey('datingUser.id'))

Base.metadata.create_all(engine)

session = Session()
def add_f(obj):
    session.add(obj)
    session.commit()
