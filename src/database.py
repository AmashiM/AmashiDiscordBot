

import json
import os

save_file = "F:/ai-models/data.db"

def init():
  if not os.path.isfile(save_file):

    init_data = dict(
      words=[]
    )


    with open(save_file, 'a') as a:
      a.write(init_data)

def read():
  with open(save_file, 'r') as r:
    data = json.load(r)
  return data









