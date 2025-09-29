from sqlmodel import Field, SQLModel, Relationship
from typing import Optional


class TeamBase(SQLModel):
    name: str = Field(index=True)

class Team(TeamBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class HeroBase(SQLModel):
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)


class Hero(HeroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    secret_name: str
    team_id: Optional[int] = Field(default=None, foreign_key='team.id')
    team: Optional[Team] = Relationship(back_populates='heroes')


class HeroPublic(HeroBase):
    id: int

class HeroCreate(HeroBase):
    secret_name: str

# not necessarily needed to inherit from HeroBase as we're re-declaring everything
class HeroUpdate(HeroBase):
    secret_name: str | None = None
    name: str | None = None
    age: int | None = None


class TeamWithHeroesCreate(TeamBase):
    heroes: list['HeroCreate'] = Field(default_factory=list)


class TeamWithHeroesRead(TeamBase):
    heroes: list['HeroPublic'] = []
