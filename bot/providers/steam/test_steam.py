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

t = 0
sys.exit(0)
while psutil.virtual_memory().percent < 100:
    print('psutil_virtual_memory:', psutil.virtual_memory().percent)
    time.sleep(1)
    t+=1
    if t == 2:
        break
