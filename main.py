from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Session, SQLModel, create_engine, select

from models import Hero, HeroCreate, HeroPublic, HeroUpdate

sqlite_file_name = "database.db"
sqlite_url = f'sqlite:///{sqlite_file_name}'

connect_args = {'check_same_thread': False}
engine = create_engine(sqlite_url, connect_args=connect_args) # this is what holds the connection to the db
# only need one db in this case so we only have one engine

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# the session allows to store the objects in memory
# this will be injected as a dependency so that each request has a session to communicate with the db through the engine
def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

def lifespan():
    create_db_and_tables()

app = FastAPI(lifespan=lifespan)


@app.post('/heroes/', response_model=HeroPublic)
def create_hero(hero: HeroCreate, session: SessionDep) -> Hero:
    db_hero = Hero.model_validate(hero)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero


@app.get('/heroes/', response_model=list[HeroPublic])
def read_heroes(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100
):
    heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
    return heroes

@app.get('/heroes/{hero_id}', response_model=HeroPublic)
def read_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail='Hero not found')
    return hero


@app.patch('/heroes/{hero_id}', response_model=HeroPublic)
def update_hero(hero_id: int, session: SessionDep, hero: HeroUpdate):
    hero_db = session.get(Hero, hero_id)
    if not hero_db:
        raise HTTPException(status_code=404, detail='Hero not found')
    hero_data = hero.model_dump(exclude_unset=True)
    hero_db.sqlmodel_update(hero_data)
    session.add(hero_db)
    session.commit()
    session.refresh(hero_db)
    return hero_db
