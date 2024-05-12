C:\Users\nadja\AppData\Local\Programs\Python\Python311\python.exe D:\source\PREN\src\common.py
analyzed video: D:\source\PREN\testdata\pren_cube_01.mp4
expected:   {1: 'red', 2: 'blue', 3: 'red', 4: 'yellow', 5: '', 6: '', 7: 'yellow', 8: 'red'}
end_result: {1: 'red', 2: 'blue', 3: 'red', 4: 'yellow', 5: '', 6: '', 7: 'yellow', 8: 'red'}
find_best_path, provided positions: {1: 'red', 2: 'blue', 3: 'red', 4: 'yellow', 5: '', 6: '', 7: 'yellow', 8: 'red'}
commands: [4, 3, 1, 1, 1, 3, 4, 2, 3, 2, 4, 3]
end position: 25
path: [4, 3, 1, 1, 1, 3, 4, 2, 3, 2, 4, 3]
correct!



analyzed video: D:\source\PREN\testdata\pren_cube_02.mp4
expected:   {1: 'yellow', 2: 'red', 3: '', 4: 'blue', 5: 'yellow', 6: 'red', 7: '', 8: 'blue'}
end result: {1: 'yellow', 2: 'red', 3: '', 4: 'blue', 5: 'yellow', 6: 'red', 7: '', 8: 'blue'}
find_best_path, provided positions: {1: 'yellow', 2: 'red', 3: '', 4: 'blue', 5: 'yellow', 6: 'red', 7: '', 8: 'blue'}
commands: [3, 2, 4, 3, 4, 1, 1, 2, 4, 3, 4, 1]
end position: 75
path: [3, 2, 4, 3, 4, 1, 1, 2, 4, 3, 4, 1]
!issue here!!
should probably become [3, 2, 4, 3, 4, 1, --4--, 2, 4, 3, 4, 1]


analyzed video: D:\source\PREN\testdata\pren_cube_03.mp4
expected:   {1: 'blue', 2: 'blue', 3: 'yellow', 4: 'red', 5: 'red', 6: 'red', 7: 'blue', 8: 'yellow'}
end result: {1: 'blue', 2: 'blue', 3: 'yellow', 4: 'red', 5: 'red', 6: 'red', 7: 'blue', 8: 'yellow'}
find_best_path, provided positions: {1: 'blue', 2: 'blue', 3: 'yellow', 4: 'red', 5: 'red', 6: 'red', 7: 'blue', 8: 'yellow'}
commands: [4, 1, 1, 1, 4, 2, 4, 3, 4, 3, 4, 1, 4, 2, 4, 3]
end position: 0
path: [4, 1, 1, 1, 4, 2, 4, 3, 4, 3, 4, 1, 4, 2, 4, 3]
!issue here again - probably the same issue as before - somehow get now red 3 times at te same spot
should probably become [4, 1, 1, 1, 4, 2, 4, 3, --1--, 3, 4, 1, 4, 2, --1--, 3]




