import os


def get_disks():
    drives = []
    for drive_letter in range(65, 91):
        drive = chr(drive_letter) + ":"
        if os.path.exists(drive):
            drives.append(drive)
    return drives
