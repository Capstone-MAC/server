from database.models import create_table
from database.conn import EngineConn

engine = EngineConn()
create_table(engine)
db_session = engine.session_maker()

session = {}