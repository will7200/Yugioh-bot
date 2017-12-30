import sys
sys.path.insert(0,'./bin/Release/net471')
import clr
from win32gui import GetWindowText, GetForegroundWindow, SetForegroundWindow, FindWindow
import lsteam as steam
def test_win32():
    lx = FindWindow(None, "Yugioh Duel Links")

def test_cs_dll():
    steam.MouseSimulator.FindWindow(None, "Yugioh Duel Links")


if __name__ == "__main__":
    import timeit
    print("Pywin32",timeit.timeit(
        "test_win32()", setup="gc.enable\nfrom __main__ import test_win32", number=100000000
    ))
    print("CS DLL", timeit.timeit(
        "test_cs_dll()", setup="gc.enable\nfrom __main__ import test_cs_dll",number=100000000
    ))