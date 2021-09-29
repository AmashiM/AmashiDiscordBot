
import pymongo
import os

if os.getenv("URI") is None:
  from dotenv import load_dotenv
  load_dotenv()
  del load_dotenv



client = pymongo.MongoClient(os.getenv("URI"))
db = client.get_database("AmashiBot")

users = db.get_collection("users")
guilds = db.get_collection("users")
queues = db.get_collection("queues")
words = db.get_collection("words")

class Query:
  user = lambda user_id, guild_id: dict(user_id=user_id, guild_id=guild_id)
  guild = lambda guild_id: dict(guild_id=guild_id)
  queue = lambda guild_id: dict(guild_id=guild_id)

class Queue:
  def __init__(self, **kwargs):
    self.songs = []
    self.loop = False
    self.current = None

    for key in kwargs.keys():
      setattr(self, key, kwargs[key])

  def to_dict(self):
    return dict(
      songs=self.songs
    )
