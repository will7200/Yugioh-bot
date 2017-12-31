import sys
sys.path.insert(0,'./bin/Release/net471')
import clr
from win32gui import GetWindowText, GetForegroundWindow, SetForegroundWindow, FindWindow
import lsteam as steam
def test_win32():
    lx = FindWindow(None, "Yugioh Duel Links")

def test_cs_dll():
    steam.MouseSimulator.FindWindow(None, "Yugioh Duel Links")

import sys
sys.path.insert(0,'./bin/Release/net471')
import clr
import psutil
import time

clr.AddReference("System")
clr.AddReference("lsteam")
from System.Drawing import Point
import lsteam as steam
p = Point(5, 5)
from System import Environment
from win32gui import GetWindowText, GetForegroundWindow, SetForegroundWindow, FindWindow
print(FindWindow(None, "Yu-Gi-Oh! DUEL LINKS"))
old = GetForegroundWindow()
steam.ClickOnPointTool.ClickOnPoint(Point(802, 635))
#steam.MouseSimulator.FakeClickLeftButton(Point(802, 635))
time.sleep(1)
"""
import win32gui, win32ui, win32con, win32api
hwin = win32gui.GetDesktopWindow()
width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
hwindc = win32gui.GetWindowDC(hwin)
srcdc = win32ui.CreateDCFromHandle(hwindc)
memdc = srcdc.CreateCompatibleDC()
bmp = win32ui.CreateBitmap()
bmp.CreateCompatibleBitmap(srcdc, width, height)
memdc.SelectObject(bmp)
memdc.BitBlt((0, 0), (width, height), srcdc, (left, top), win32con.SRCCOPY)
bmp.SaveBitmapFile(memdc, 'screenshot.bmp')"""
t = 0
sys.exit(0)
while psutil.virtual_memory().percent < 100:
    print('psutil_virtual_memory:', psutil.virtual_memory().percent)
    time.sleep(1)
    t+=1
    if t == 2:
        break
if __name__ == "__main__":
    import timeit
    print("Pywin32",timeit.timeit(
        "test_win32()", setup="gc.enable\nfrom __main__ import test_win32", number=100000000
    ))
    print("CS DLL", timeit.timeit(
        "test_cs_dll()", setup="gc.enable\nfrom __main__ import test_cs_dll",number=100000000
    ))