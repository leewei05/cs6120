import sys

def dfa_live():
    print("live")

def dfa_defined():
    print("defined")

def main():
    argc = sys.argv
    if len(argc) < 2:
        print("Usage: python3 dfa.py <live|defined>")
    elif sys.argv[1] == "defined":
        dfa_defined()
    elif sys.argv[1] == "live":
        dfa_live()
    else:
        print("Undefined analysis!")

if __name__ == "__main__":
    main()
