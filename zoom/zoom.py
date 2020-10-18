import calendar
import os
import re
import time
from datetime import date, datetime

import pandas as pd
import pyautogui


def go_to_element_by_text(element):
    btn = pyautogui.locateCenterOnScreen(f"zoom/{element}.png")
    pyautogui.moveTo(btn)


def get_meeting_id_from_url(meeting_id):
    return "".join(re.findall(r'\d+', meeting_id))


def click_on_element():
    pyautogui.click()
    time.sleep(3)


def write_to_element(text):
    pyautogui.write(text)
    time.sleep(3)


def signIn(meeting_id, password):
    # Open's Zoom Application from the specified location
    os.startfile("C:/Users/roy/AppData/Roaming/Zoom/bin/Zoom.exe")
    time.sleep(3)

    # Click's join button
    go_to_element_by_text("joinameeting")
    click_on_element()

    # Type the meeting id
    go_to_element_by_text("meetingid")
    write_to_element(meeting_id)

    # To turn of video and audio
    try:
        mediaBtn = pyautogui.locateAllOnScreen("zoom/media.png")
        for btn in mediaBtn:
            pyautogui.moveTo(btn)
            click_on_element()
    except OSError as ex:
        print(repr(ex))

    # To join
    go_to_element_by_text("join")
    click_on_element()

    # Enter's passcode to join meeting
    go_to_element_by_text("meetingPasscode")
    write_to_element(password)

    # Click's on join button
    go_to_element_by_text("joinmeeting")
    click_on_element()


def get_row_to_record(df):
    my_date = date.today()
    day_name = calendar.day_name[my_date.weekday()]
    now = datetime.now().strftime("%H:%M")
    row = df[(df["Timings"] == now) & (df["Day"] == day_name)]
    if not row.empty:
        return row.iloc[0]
    return None


def read_excel_file(file_name="zoom/timings.xlsx"):
    df = pd.read_excel(file_name, index=False)
    df["Timings"] = df["Timings"].apply(lambda x: x.strftime("%H:%M"))
    return df


def get_into_meeting(row):
    meeting_id = str(row["MeetingId"])
    if meeting_id.startswith("http"):
        meeting_id = get_meeting_id_from_url(meeting_id)
    password = str(row["Passcode"])
    time.sleep(5)
    signIn(meeting_id, password)
    time.sleep(2)
    print('signed in')
