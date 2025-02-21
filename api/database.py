from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Numeric,
    Index,
    or_,
    select,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from .env import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    edition = Column(String(50))
    price = Column(Numeric(10, 2))
    file = Column(String(255))
    category_id = Column(Integer, nullable=False)

    __table_args__ = (
        Index(
            "ix_title_ngram",
            "title",
            mysql_prefix="FULLTEXT",
            mysql_with_parser="ngram",
        ),
        Index(
            "ix_author_ngram",
            "author",
            mysql_prefix="FULLTEXT",
            mysql_with_parser="ngram",
        ),
    )


def init_db():
    Base.metadata.create_all(bind=engine)


def get_book_orm(db: Session, book_id: int):
    return db.execute(select(Book).where(Book.id == book_id)).first()[0]


def create_book_orm(db: Session, book: Book):
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def update_book_orm(db: Session, book: Book, updated_data: dict):
    if book:
        for key, value in updated_data.items():
            setattr(book, key, value)
        db.commit()
        db.refresh(book)
    return book


def delete_book_orm(db: Session, book_id: int):
    book = get_book_orm(db, book_id)
    if book:
        db.delete(book)
        db.commit()
    return book


def create_category_orm(db: Session, category: Category):
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def get_categories_orm(db: Session):
    return [category[0] for category in db.execute(select(Category)).all()]


def search_books_orm(
    db: Session, title: str = None, author: str = None, add_or: bool = False
):
    query = select(Book)
    conditions = []

    if title:
        conditions.append(Book.title.match(f"+{title}*", boolean=True))
    if author:
        conditions.append(Book.author.match(f"+{author}*", boolean=True))

    if conditions:
        if add_or:
            query = query.where(or_(*conditions))
        else:
            query = query.where(*conditions)
        return [book[0] for book in db.execute(query).all()]
    return []
