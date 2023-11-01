from database.conn import EngineConn
from database.models import create_table

engine = EngineConn()
create_table(engine)
db_session = engine.session_maker()