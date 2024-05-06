import json, sys


def main():
    prog = json.load(sys.stdin)
    json.dump(prog, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
