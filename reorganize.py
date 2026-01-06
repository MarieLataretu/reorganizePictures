import os
import sys
import shutil
import argparse
import exifread
from datetime import datetime
from argparse import RawTextHelpFormatter
import subprocess
import json


def error(string, error_type=1):
    sys.stderr.write(f"ERROR: {string}\n")
    exit(error_type)


def log(string):
    sys.stderr.write(f"LOG: {string}\n")


def get_jpg_creation_time(file_path):
    # Open image file for reading (binary mode)
    with open(file_path, "rb") as pic_binary:
        tags = exifread.process_file(pic_binary, details=False)
        date = tags.get("EXIF DateTimeOriginal")
        if date:
            timeStamp = datetime.strptime(date.__str__(), "%Y:%m:%d %H:%M:%S")
            return timeStamp
        else:
            return None


def get_mp4_creation_time(file_path):
    cmd = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_entries",
        "format_tags=creation_time",
        file_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)

    creation_time = data["format"]["tags"].get("creation_time")
    if creation_time:
        # creation_time example: "2020-01-15T10:30:45.000000Z"
        timeStamp = datetime.strptime(creation_time.__str__(), "%Y-%m-%dT%H:%M:%S.%fZ")
        return timeStamp
    else:
        return None


def handle_file(source, timeStamp, pattern, target, force, mode):
    # timeStamp = datetime.strptime(date.__str__(), "%Y:%m:%d %H:%M:%S")
    full_Date = timeStamp.strftime(pattern)
    year = str(timeStamp.year)

    target_dir_with_date = f"{target}/{year}/{full_Date}"
    os.makedirs(target_dir_with_date, exist_ok=True)

    source_basename = os.path.basename(source)
    new_pic = os.path.join(target_dir_with_date, source_basename)

    if os.path.isfile(new_pic) and not force:
        log(f"Skipping {source_basename}: file already exists at {new_pic}.")
    else:
        if os.path.isfile(new_pic) and force:
            log(f"Overwriting {new_pic}")
        if mode == "cp":
            shutil.copy(source, target_dir_with_date)
        elif mode == "mv":
            shutil.move(source, target_dir_with_date)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=RawTextHelpFormatter,
    )
    parser.add_argument(
        "mode", choices=["cp", "mv"], help="copy (cp) or move (mv) files"
    )
    parser.add_argument("source", help="source directory")
    parser.add_argument("target", help="parent directory for the reorganized files")
    parser.add_argument(
        "-p",
        "--pattern",
        default="%m-%d",
        help="subdirectory naming pattern (strftime format code sting) [%%m-%%d]",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        default=False,
        help="overwrite file if exist [false]",
    )

    args = parser.parse_args()

    if not os.path.isdir(args.source):
        error(f"{args.source} does not exist.")

    for dirpath, _, filenames in os.walk(args.source):
        for f in filenames:

            pic = os.path.abspath(os.path.join(args.source, f))
            file_extension = pic.rsplit(".", 1)[-1]

            if file_extension.lower() in ("jpg", "jpeg", "jpe", "jfif"):
                creation_timestamp = get_jpg_creation_time(pic)
            elif file_extension.lower() == "mp4":
                creation_timestamp = get_mp4_creation_time(pic)
            else:
                log(f"Skipping {pic}: unknown file extension.")
                continue

            if creation_timestamp:
                handle_file(
                    pic,
                    creation_timestamp,
                    args.pattern,
                    args.target,
                    args.force,
                    args.mode,
                )
            else:
                log(f"Skipping {pic}: cannot read metadata.")
