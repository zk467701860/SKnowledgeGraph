
if __name__ == '__main__':

    with open('data/fel evaluation/log-new.txt', 'r') as f:
        index = 0
        real = 0
        total = 0
        row = 1
        line = f.readline()
        while line:
            if line.startswith('current_pair_index'):
                total += 1
                alias = f.readline()
                row += 1
                f.readline()
                row += 1
                result = f.readline()
                row += 1
                if result == 'do not have alias\n':
                    index += 1
                    if '.' in alias:
                        real += 1
                    else:
                        print row
                        print alias
            line = f.readline()
            row += 1

    print real
    print index
    print total
    print row
