import sys
import shlex
import subprocess
from time import sleep


def main(arg_1, arg_2):
    command = "python test2.py {}".format(arg_2)
    subprocess.Popen(shlex.split(command))
    print("A1: {}, A2: {}".format(type(arg_1), type(arg_2)))
    for i in range(5):
        print("Test1: {} {}".format(arg_1, arg_2))
        sleep(1)


if __name__ == '__main__':
    main(*sys.argv[1:])