import json
import time
import io
import random
import sys
import os.path
import base64
import datetime
import math
import fileinput
import traceback
from PIL import Image, ImageOps, ImageDraw, ImageChops, ImageFilter
from math import ceil, radians, cos, sin, asin, sqrt
import re
import win32gui
import subprocess
import logging
import inspect
root = logging.getLogger('bot')

# Rotate a python list


def Tap(x, y):
    curframe = inspect.currentframe()
    calframe = inspect.getouterframes(curframe, 2)
    #print('caller name:', calframe[1][3])
    root.debug("Tapping at location ({},{})".format(x, y))
    Command = "bin\\adb.exe shell input tap %d %d" % (x, y)
    os.system(Command)

# TODO add -s to shell to specifiy device
def Swipe(x1, y1, x2, y2):
    Command = "bin\\adb.exe shell input swipe %d %d %d %d " % (x1, y1, x2, y2)
    os.system(Command)


def SwipeTime(x1, y1, x2, y2, t):
    Command = "bin\\adb.exe shell input swipe %d %d %d %d %d" % (
        x1, y1, x2, y2, t)
    os.system(Command)


def KeyEscap():
    Command = "bin\\adb.exe shell input keyevent 4"
    os.system(Command)


def TakePngScreenshot():
    while True:
        try:
            Command = "bin\\adb.exe shell \"screencap -p | busybox base64\""
            PngScreenshotData = os.popen(Command).read()
            PngScreenshotData = base64.b64decode(PngScreenshotData)
            break
        except KeyboardInterrupt:
            sys.exit(0)
        except:
            print("[!] Failed to get screen")
    return PngScreenshotData


def IsColorInCeil(ColorToCheck, RefColor, Ceil):
    if (RefColor[0] + (255 * Ceil)) > ColorToCheck[0] > (RefColor[0] - (255 * Ceil)):
        if (RefColor[1] + (255 * Ceil)) > ColorToCheck[1] > (RefColor[1] - (255 * Ceil)):
            if (RefColor[2] + (255 * Ceil)) > ColorToCheck[2] > (RefColor[2] - (255 * Ceil)):
                return True
    return False


def GetMeanColor(img, x, y, size=10):
    MeanColor = [0, 0, 0]
    pixdata = img.load()
    for xr in range(x - (size / 2), x + (size / 2)):
        for yr in range(y - (size / 2), y + (size / 2)):
            MeanColor[0] = MeanColor[0] + pixdata[xr, yr][0]
            MeanColor[1] = MeanColor[1] + pixdata[xr, yr][1]
            MeanColor[2] = MeanColor[2] + pixdata[xr, yr][2]
    MeanColor[0] = MeanColor[0] / (size**2)
    MeanColor[1] = MeanColor[1] / (size**2)
    MeanColor[2] = MeanColor[2] / (size**2)
    return MeanColor


def GetImgFromScreenShot():
    Screenshot = TakePngScreenshot()
    img = Image.open(io.BytesIO(Screenshot))
    img = img.convert("RGB")
    return img


def OnlyPureWhite(img1):
    pixdata1 = img1.load()
    output = img1.copy()
    pixdataout = output.load()
    for xr in range(img1.size[0]):
        for yr in range(img1.size[1]):
            if pixdata1[xr, yr] != (255, 255, 255):
                pixdataout[xr, yr] = (255, 255, 255)
            else:
                pixdataout[xr, yr] = (0, 0, 0)
    return output


def ImgToString(img, CharSet=None):
    img.save("tmp\\ocr.png")
    Command = "bin\\tess\\tesseract.exe --tessdata-dir bin\\tess\\tessdata tmp\\ocr.png tmp\\ocr "
    if CharSet != None:
        Command += "-c tessedit_char_whitelist=" + CharSet + " "
    Command += "-psm 7 "
    Command += "> nul 2>&1"
    # print Command
    os.system(Command)
    # Get the largest line in txt
    with open("tmp\\ocr.txt") as f:
        content = f.read().splitlines()
    OutputLine = ""
    for line in content:
        line = line.strip()
        if len(line) > len(OutputLine):
            OutputLine = line
    return OutputLine


def ZoomOut():
    ZoomOutFix()
    Command = "bin\\adb.exe push bin\\Zoomout.txt /sdcard/Zoomout.txt"
    os.system(Command)
    Command = "bin\\adb.exe shell sh /sdcard/Zoomout.txt"
    os.system(Command)

# Check the correct input


def GetEvent():
    Command = "bin\\adb.exe shell cat /proc/bus/input/devices >tmp\\inputs.log"
    os.system(Command)
    a = 'N: Name="Android Input"'
    line_num = 0
    x = 0
    with open("tmp\\inputs.log") as f:
        content = f.read().splitlines()
        for line in content:
            line_num += 1
            if a in line:
                x = line_num + 4
            elif line_num == x:
                m = re.search("(event[0-9])", line)
                result = m.group(1)
                return result

# Change the file whit the correct event number


def ZoomOutFix():
    x = GetEvent()
    array = []
    array.append("#!/bin/sh")
    with open("bin\\Zoomout.txt") as f:
        content = f.read().splitlines()
        for line in content:
            if "event" in line:
                line = re.sub(r"event[0-9]", x, line)
                array.append(line)
    f.close()
    array.append("exit")
    g = open("bin\\Zoomout.txt", 'w')
    g.write("\n".join(array))
    g.close()

# Check Nox process is running


def IsNoxRunning():
    try:
        if win32gui.FindWindow(None, "Nox"):
            return True
    except:
        return False


def StartNoxProcess(NoxPath):
    try:
        root.info("Starting Nox...")
        process = subprocess.Popen(NoxPath, shell=True, stdout=subprocess.PIPE)
    except:
        root.error("The program can't run Nox")


def KillNoxProcess():
    try:
        if IsNoxRunning():
            os.system("taskkill /im Nox.exe /f")
    except:
        root.error("The program could not be killed")


def LevenshteinDistance(first, second):
    """Find the Levenshtein distance between two strings."""
    if len(first) > len(second):
        first, second = second, first
    if len(second) == 0:
        return len(first)
    first_length = len(first) + 1
    second_length = len(second) + 1
    distance_matrix = [[0] * second_length for x in range(first_length)]
    for i in range(first_length):
        distance_matrix[i][0] = i
    for j in range(second_length):
        distance_matrix[0][j] = j
    for i in range(1, first_length):
        for j in range(1, second_length):
            deletion = distance_matrix[i - 1][j] + 1
            insertion = distance_matrix[i][j - 1] + 1
            substitution = distance_matrix[i - 1][j - 1]
            if first[i - 1] != second[j - 1]:
                substitution += 1
            distance_matrix[i][j] = min(insertion, deletion, substitution)
    return distance_matrix[first_length - 1][second_length - 1]


def WriteAppend(Filename, Content):
    f = open(Filename, "a")
    f.write(Content)
    f.close()


def DiffImgPercent(img1, img2):
    pixdata1 = img1.load()
    pixdata2 = img2.load()
    DiffCount = 0
    for xr in range(img1.size[0]):
        for yr in range(img1.size[1]):
            if pixdata1[xr, yr] != pixdata2[xr, yr]:
                DiffCount += 1

    return (DiffCount * 1.0) / (img1.size[0] * img1.size[1])


class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
