company_set = set()

company_set.add('a')
if 'a' not in company_set:
	company_set.add('b')

print(company_set)

from pprint import pprint

my_dict = {'name': 'Yasoob', 'age': 'undefined', 'personality': 'awesome'}
pprint(my_dict)

from collections import namedtuple

Animal = namedtuple('Animal', 'name age type')
perry = Animal(name="Perry", age=31, type="cat")
dict = perry._asdict()
dict['name'] = 'Philip'
print(dict)