from func import *

with open("student_number.txt", "r") as file:
    for line in file.readlines():
        number = line.replace("\n", "")

        weeks = detect_weeks(number)

        clean(number)
        connect_and_download(number, weeks)
        assemble(number, weeks)
        clean2(number, weeks)
        normalize_ics_to_utf8(f"ics_files/{number}.ics")
        #reformat(number)
        #fix_wrong_dst(number)

