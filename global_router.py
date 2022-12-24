#!/usr/bin/env python3
from GlobalRouter import GlobalRouter
        


def main():
    global_router = GlobalRouter()
    netlist = global_router.parse_input("testcase/example.txt")
    



if __name__ == "__main__":
    main()