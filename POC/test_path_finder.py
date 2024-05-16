from src.path_finder.path_finder import find_best_path, color_mapping

# given config is as defined on the IF-File, could still change...
# test_set: (positions, expected_path)
test_set = [
    # config 1 values
    ({1: 'red', 2: 'blue', 3: 'red', 4: 'yellow', 5: '', 6: '', 7: 'yellow', 8: 'red'},
     [4, 3, 1, 1, 1, 3, 4, 2, 3, 2, 4, 3, 3, 0]),
    # expected startpos = 50, was 75
    # config 2 values
    ({1: 'yellow', 2: 'red', 3: '', 4: 'blue', 5: 'yellow', 6: 'red', 7: '', 8: 'blue'},
     [3, 2, 4, 3, 4, 1, 4, 2, 4, 3, 4, 1, 1, 0]),
    # expected startpos = 75, was 75
    ## now ok
    # config 3 values
    ({1: 'blue', 2: 'blue', 3: 'yellow', 4: 'red', 5: 'red', 6: 'red', 7: 'blue', 8: 'yellow'},
     [4, 1, 1, 1, 4, 2, 4, 3, 1, 3, 4, 1, 4, 2, 1, 3, 1, 0]),
    # expected startpos = 25, was 25
    ## now ok
]


def print_path_beautifully(path):
    for i in range(len(path)):
        if i % 2 == 0:
            if path[i] == 4:
                print(end='stay, ')
            elif path[i] == 1:
                print(end='forward 1, ')
            elif path[i] == 2:
                print(end='forward 2, ')
            elif path[i] == 3:
                print(end='backwards 1, ')
        else:
            for color, value in color_mapping.items():
                if value == path[i]:
                    print(color, end=', ')
    print('')


for i, (positions, expected_path) in enumerate(test_set):
    print(f'item {i}')
    path = find_best_path(positions)

    if path == expected_path:
        print('SUCCESS')
    else:
        print('ERROR')

    print(f'expected path: {expected_path}')
    print_path_beautifully(expected_path)
    print(f'actual path: {path}')
    print_path_beautifully(path)
    print('--------------------------------------------------------------------')
