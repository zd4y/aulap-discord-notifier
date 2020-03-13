import os
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, BigInteger, ForeignKey, Table


DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///homeworks.db'

engine = create_engine(DATABASE_URI, echo=False)
Base = declarative_base()


guild_students = Table(
    'guild_students', Base.metadata,
    Column('guild_id', BigInteger, ForeignKey('guilds.id')),
    Column('student_id', Integer, ForeignKey('students.id'))
)


class Guild(Base):
    __tablename__ = 'guilds'

    id = Column(BigInteger, primary_key=True, autoincrement=False)
    students = relationship('Student', secondary=guild_students, back_populates='guilds')
    prefix = Column(String, default='.')
    homework_cache = relationship('CachedHomework', backref='guild', cascade='save-update, merge, delete, delete-orphan')


student_homeworks = Table(
    'student_homeworks', Base.metadata,
    Column('student_id', Integer, ForeignKey('students.id')),
    Column('homework_id', Integer, ForeignKey('homeworks.id'))
)


class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True, autoincrement=False)
    username = Column(String, nullable=False, unique=True)
    alias = Column(String)
    guilds = relationship('Guild', secondary=guild_students, back_populates='students')
    homeworks = relationship('Homework', secondary=student_homeworks, back_populates='students')
    homework_cache = relationship('CachedHomework', backref='student', cascade='save-update, merge, delete, delete-orphan')


class Homework(Base):
    __tablename__ = 'homeworks'

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    creation_date = Column(DateTime)
    due_date = Column(DateTime)
    teacher = Column(String)
    students = relationship('Student', secondary=student_homeworks, back_populates='homeworks')
    cache = relationship('CachedHomework', backref='homework', cascade='save-update, merge, delete, delete-orphan')

    def __str__(self):
        return f'Homework<{self.id} name={self.name!r}>'

    def __repr__(self):
        return f'Homework<{self.id} name={self.name!r}>'


class CachedHomework(Base):
    __tablename__ = 'cached_homeworks'

    id = Column(Integer, primary_key=True)
    homework_id = Column(Integer, ForeignKey('homeworks.id'))
    guild_id = Column(BigInteger, ForeignKey('guilds.id'))
    student_id = Column(Integer, ForeignKey('students.id'))


def create_all():
    Base.metadata.create_all(engine)


session = sessionmaker(bind=engine)()


async def get(model, **kwargs):
    if kwargs is None:
        raise TypeError('You must provide at least one key word argument')
    return session.query(model).filter_by(**kwargs).first()
