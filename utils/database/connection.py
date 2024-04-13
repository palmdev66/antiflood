import aiomysql
from config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER


async def connect():
    conn = await aiomysql.connect(host=DB_HOST, port=DB_PORT,
                                       user=DB_USER, password=DB_PASSWORD,
                                       db=DB_NAME)

    return conn
