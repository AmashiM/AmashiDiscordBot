

import re
from random import shuffle
import itertools



val = [
  ['hello', 'hi', 'yo'],
  ["how are you", ["how you", ['been', 'doing']]]
]

def get_all_strings(values: list) -> list[str]:
  txt = []
  for i in values:
    if type(i) == str:
      txt.append(i)
    elif type(i) == list:
      txt += get_all_strings(i)
  return txt


def get_type_list(values: list):
  return [type(t) for t in values]


def build_regex(values: list):
  regex = []

  def make_or_regex(values):

    def make_sub_regex(values):
      u = []
      for e in values:
        if type(e) == str:
          u.append(e)
        elif type(e) == list:
          u.append(make_or_regex(e))
      return f'({" ".join(u)})'

    tmp = []
    for x in values:
      if type(x) == str:
        tmp.append(x)
      elif type(x) == list:
        types = get_type_list(x)
        if list in types and str in types:
          tmp.append(make_sub_regex(x))
        elif list not in types and str in types:
          tmp.append(make_or_regex(x))
    return f'({"|".join(tmp)})'

  for i in values:
    if type(i) == str:
      regex.append(i)
    elif type(i) == list:
      if len(i) > 1:
        regex.append(make_or_regex(i))
      else:
        regex += i[0]
  return re.compile(" ".join(regex), flags=re.IGNORECASE)

def make_strings(values):
  res = []
  return res

def pros(values: list):
  strings = get_all_strings(values)

  regex = build_regex(values)

  print(strings)

  print(regex)

  tests = []

  res = []

  combos = [" ".join(list(i)) for i in list(itertools.combinations(strings, len(values)))]

  combos = [ c for c in combos if regex.fullmatch(c) != None]

  print(combos)

res = pros(val)

print(res)
