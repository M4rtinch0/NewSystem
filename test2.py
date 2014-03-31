import sys
from time import sleep


def main(arg_1):
    print("A1: {}".format(type(arg_1)))
    for i in range(10):
        print("Test2: {!r}".format(arg_1))
        sleep(2)
    return


if __name__ == '__main__':
    main(*sys.argv[1:])