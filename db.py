from sqlmodel import Session, SQLModel, create_engine

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

