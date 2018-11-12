import getopt,sys

optlist, args = getopt.getopt(sys.argv[1:], 'e:j:', ['env=','job='])
opt_dict = dict(optlist)
print(opt_dict)
try:
    if opt_dict['--env']:
        print(opt_dict['--env'], opt_dict['--job'])
    else:
        print('[ERROR] lack env config')
except Exception as e:
    print('[ERROR] lack env config: {}'.format(e))