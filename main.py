from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from middleware.middleware import HiByeMiddleware
from models import Hero, HeroCreate, HeroPublic, HeroUpdate, Team, TeamWithHeroesCreate, TeamWithHeroesRead
from db import create_db_and_tables, engine, get_session


SessionDep = Annotated[Session, Depends(get_session)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield
    engine.dispose()


app = FastAPI(lifespan=lifespan)
app.add_middleware(HiByeMiddleware)


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


@app.post('/team', response_model=TeamWithHeroesRead)
def create_team_with_heroes(team: TeamWithHeroesCreate, session: SessionDep):
    heroes_input = team.pop('heroes', [])
    try:
        team = Team(name=team.name)
        session.add(team)
        # flush() sends the INSERT for Team so team.id is populated, while still inside the transaction.
        session.flush()

        heroes = [
            HeroCreate(
                name=h.name,
                secret_name=h.secret_name,
                team_id=team.id
            )
            for h in heroes_input
        ]
        session.add_all(heroes)
        session.commit()
    except IntegrityError as e:
        session.rollback()
        # map DB constraint messages to a friendly 400
        raise HTTPException(status_code=400, detail="Integrity error creating team/heroes")


    persisted_team  = session.exec(
        select(Team).where(Team.id==team.id).options(selectinload=Team.heroes)
    ).one()

    return TeamWithHeroesRead(
        id=persisted_team.id,
        name=persisted_team.name,
        heroes=[HeroPublic(id=h.id, name=h.name) for h in persisted_team.heroes]
    )

