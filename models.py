from sqlmodel import Field, SQLModel, Relationship


class HeroBase(SQLModel):
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)


class Hero(HeroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    secret_name: str


class HeroPublic(HeroBase):
    id: int

class HeroCreate(HeroBase):
    secret_name: str

# not necessarily needed to inherit from HeroBase as we're re-declaring everything
class HeroUpdate(HeroBase):
    secret_name: str | None = None
    name: str | None = None
    age: int | None = None



class Team(SQLModel, table=True):
    name: str = Field(index=True)
    heroes: list[Hero] = Relationship(back_populates='team')