from sqlalchemy import create_engine, Integer, Text, Select, BigInteger, Delete
from sqlalchemy.dialects.postgresql import Insert
from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy.orm import Mapped, mapped_column

from config import db_user, db_host, db_name, db_pass, db_port

engine = create_engine(f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}", echo=True)


class AbstractClass:
    @classmethod
    async def select(cls, **kwargs):
        with engine.connect() as conn:
            res = conn.execute(Select(cls))
            conn.commit()
            return res

    @classmethod
    async def filter(cls, *criteria):
        with engine.connect() as conn:
            res = conn.execute(Select(cls).filter(*criteria))
            conn.commit()
            return res

    @classmethod
    async def create(cls, **kwargs):
        with engine.connect() as conn:
            conn.execute(Insert(cls).values(**kwargs))
            conn.commit()

    @classmethod
    async def delete(cls, id):
        with engine.connect() as conn:
            conn.execute(Delete(cls).where(cls.id==id))
            conn.commit()


class Base(DeclarativeBase, AbstractClass):
    @declared_attr
    def __tablename__(self):
        result = self.__name__[0].lower()
        for i in self.__name__[1:]:
            if i.isupper():
                result += f'_{i.lower()}'
                continue
            result += i
        return result


class Audios(Base):
    id: Mapped[str] = mapped_column(Integer, primary_key=True)
    audio_location: Mapped[str] = mapped_column(Text)
    text: Mapped[str] = mapped_column(Text)


def create_table():
    Base.metadata.create_all(engine)