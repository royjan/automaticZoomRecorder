from video import capture_screen
from zoom.zoom import *

if __name__ == '__main__':
    df = read_excel_file()
    while True:
        row = get_row_to_record(df)
        if row is not None:
            get_into_meeting(row)
            during = int(row['During'])
            capture_screen(during)
            break
