import gevent
from gevent.pool import Pool
from random import randint, choice

gevent_pool = Pool(30)

sub_type = randint(1, 2)
print('sub_type: {}'.format(sub_type))
five_knigt = [
    {
        "id": 111,
        "sub_type": 1
    },
    {
        "id": 222,
        "sub_type": 2
    },
    {
        "id": 333,
        "sub_type": 3
    },
    {
        "id": 444,
        "sub_type": 4
    },
    {
        "id": 555,
        "sub_type": 5
    }
]
knight_list = [choice(five_knigt) for i in range(10)]
print('before check: {}'.format(knight_list))

def check_bod_knight(knight_id):
    gevent.sleep(0.1)
    return choice((0, 1))

if sub_type in (1, 2):
    bod_flag_list = gevent_pool.map(check_bod_knight ,knight_list)
    gevent_pool.join()
    print(bod_flag_list)
    knight_list = [knight for i,knight in enumerate(knight_list) \
                   if (sub_type==1 and bod_flag_list[i]) \
                   or (sub_type==2 and not bod_flag_list[i])]

print('after check: {}'.format(knight_list))