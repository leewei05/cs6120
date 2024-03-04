def leibniz_pi():
    denom = 1
    pi = 0

    for i in range(1, 1000000):
        if (i % 2 == 0):
            pi -= 1 / denom
        else:
            pi += 1 / denom

        denom += 2

    pi *= 4
    print(pi)

if __name__ == '__main__':
    leibniz_pi()
