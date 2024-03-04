from ctypes import CDLL

dll = CDLL(R'D:\Projects\HackTrick24\dlls\comb.dll')

result = dll.add(2, 3)
print("Result:", result)
