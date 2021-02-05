import time, win32con, win32api, win32gui, ctypes
import requests
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
from pywinauto import clipboard
import pandas as pd 

kakao_opentalk_name = 'test'
chat_command = '님이 들어왔습니다.'
ban_list = []

PBYTE256 = ctypes.c_ubyte * 256
_user32 = ctypes.WinDLL("user32")
GetKeyboardState = _user32.GetKeyboardState
SetKeyboardState = _user32.SetKeyboardState
PostMessage = win32api.PostMessage
SendMessage = win32gui.SendMessage
FindWindow = win32gui.FindWindow
IsWindow = win32gui.IsWindow
GetCurrentThreadId = win32api.GetCurrentThreadId
GetWindowThreadProcessId = _user32.GetWindowThreadProcessId
AttachThreadInput = _user32.AttachThreadInput

MapVirtualKeyA = _user32.MapVirtualKeyA
MapVirtualKeyW = _user32.MapVirtualKeyW

MakeLong = win32api.MAKELONG
w = win32con

def PostKeyEx(hwnd, key, shift, specialkey):
    if IsWindow(hwnd):

        ThreadId = GetWindowThreadProcessId(hwnd, None)

        lparam = MakeLong(0, MapVirtualKeyA(key, 0))
        msg_down = w.WM_KEYDOWN
        msg_up = w.WM_KEYUP

        if specialkey:
            lparam = lparam | 0x1000000

        if len(shift) > 0:
            pKeyBuffers = PBYTE256()
            pKeyBuffers_old = PBYTE256()

            SendMessage(hwnd, w.WM_ACTIVATE, w.WA_ACTIVE, 0)
            AttachThreadInput(GetCurrentThreadId(), ThreadId, True)
            GetKeyboardState(ctypes.byref(pKeyBuffers_old))

            for modkey in shift:
                if modkey == w.VK_MENU:
                    lparam = lparam | 0x20000000
                    msg_down = w.WM_SYSKEYDOWN
                    msg_up = w.WM_SYSKEYUP
                pKeyBuffers[modkey] |= 128

            SetKeyboardState(ctypes.byref(pKeyBuffers))
            time.sleep(0.01)
            PostMessage(hwnd, msg_down, key, lparam)
            time.sleep(0.01)
            PostMessage(hwnd, msg_up, key, lparam | 0xC0000000)
            time.sleep(0.01)
            SetKeyboardState(ctypes.byref(pKeyBuffers_old))
            time.sleep(0.01)
            AttachThreadInput(GetCurrentThreadId(), ThreadId, False)

        else: 
            SendMessage(hwnd, msg_down, key, lparam)
            SendMessage(hwnd, msg_up, key, lparam | 0xC0000000)

def SendReturn(hwnd):
    win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
    time.sleep(0.01)
    win32api.PostMessage(hwnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)

def open_chatroom(chatroom_name):
    hwndkakao = win32gui.FindWindow(None, "카카오톡")
    hwndkakao_edit1 = win32gui.FindWindowEx( hwndkakao, None, "EVA_ChildWindow", None)
    hwndkakao_edit2_1 = win32gui.FindWindowEx( hwndkakao_edit1, None, "EVA_Window", None)
    hwndkakao_edit2_2 = win32gui.FindWindowEx( hwndkakao_edit1, hwndkakao_edit2_1, "EVA_Window", None)
    hwndkakao_edit3 = win32gui.FindWindowEx( hwndkakao_edit2_2, None, "Edit", None)

    win32api.SendMessage(hwndkakao_edit3, win32con.WM_SETTEXT, 0, chatroom_name)
    time.sleep(1)  
    SendReturn(hwndkakao_edit3)
    time.sleep(1)

def kakao_sendtext(chatroom_name, text):
    hwndMain = win32gui.FindWindow( None, chatroom_name)
    hwndEdit = win32gui.FindWindowEx( hwndMain, None, "RICHEDIT50W", None)

    win32api.SendMessage(hwndEdit, win32con.WM_SETTEXT, 0, text)
    SendReturn(hwndEdit)

def copy_chatroom(chatroom_name):
    hwndMain = win32gui.FindWindow( None, chatroom_name)
    hwndListControl = win32gui.FindWindowEx(hwndMain, None, "EVA_VH_ListControl_Dblclk", None)

    PostKeyEx(hwndListControl, ord('A'), [w.VK_CONTROL], False)
    time.sleep(1)
    PostKeyEx(hwndListControl, ord('C'), [w.VK_CONTROL], False)
    ctext = clipboard.GetData()
    return ctext

def get_ban_list():
    f = open("./blacklist.txt", mode="r", encoding="utf8")
    while True:
        line = f.readline()
        if not line: break
        ban_list.append(line)

def chat_last_save():
    open_chatroom(kakao_opentalk_name) 
    ttext = copy_chatroom(kakao_opentalk_name)  

    a = ttext.split('\r\n') 
    df = pd.DataFrame(a)   

    df[0] = df[0].str.replace('\[([\S\s]+)\] \[(오전|오후)([0-9:\s]+)\] ', '') 

    return df.index[-2], df.iloc[-2, 0]

def chat_chek_command(cls, clst):
    open_chatroom(kakao_opentalk_name)  
    ttext = copy_chatroom(kakao_opentalk_name) 

    a = ttext.split('\r\n') 
    df = pd.DataFrame(a) 

    df[0] = df[0].str.replace('\[([\S\s]+)\] \[(오전|오후)([0-9:\s]+)\] ', '')

    if df.iloc[-2, 0] == clst:
        return df.index[-2], df.iloc[-2, 0]
    else:

        df1 = df.iloc[cls+1 : , 0]  
        found = df1[ df1.str.contains(chat_command)]
        print("found : " + found)

        if 1 <= int(found.count()):
            print("user recognition")
            bl = found.replace(chat_command, "")   

            for bl_ckeck in ban_list:
                if bl_ckeck == bl:
                    print(bl + " confirmation")
                    kakao_sendtext(bl + "님 확인되었습니다.") 
            return df.index[-2], df.iloc[-2, 0]

        else:
            print("user unidentified")
            return df.index[-2], df.iloc[-2, 0]

def main():
    get_ban_list()
    cls, clst = chat_last_save() 

    while True:
        print("working!!")
        cls, clst = chat_chek_command(cls, clst)  
        time.sleep(5)


if __name__ == '__main__':
    main()