import os
import sys
import shutil
import argparse
import exifread
from datetime import datetime
from argparse import RawTextHelpFormatter

def error(string, error_type=1):
    sys.stderr.write(f'ERROR: {string}\n')
    exit(error_type)

def log(string):
    sys.stderr.write(f'LOG: {string}\n')

jpg_file_extensions = ['jpg', 'jpeg', 'jpe', 'jfif']

parser = argparse.ArgumentParser(description=f"Reorganize jpg files in a directory, so that:\ntarget\n|___year\n|   |___month-day\n\nRecognizable file extensions: {', '.join(jpg_file_extensions)} (not case sensitive).", formatter_class=RawTextHelpFormatter)
parser.add_argument('mode', choices=['cp', 'mv'], help='copy (cp) or move (mv) files')
parser.add_argument('source', help='source directory')
parser.add_argument('target', help='parent directory for the reorganized files')

args = parser.parse_args()

if not os.path.isdir(args.source):
	error(f"{args.source} does not exist.")

for dirpath,_,filenames in os.walk(args.source):
	for f in filenames:

		pic = os.path.abspath(os.path.join(args.source, f))
		file_extension = pic.rsplit('.', 1)[-1]

		if file_extension.lower() in jpg_file_extensions:

			# Open image file for reading (binary mode)
			with open(pic, 'rb') as pic_binary:

				# Return Exif tags
				tags = exifread.process_file(pic_binary, details=False)
				date = tags.get('EXIF DateTimeOriginal')
				timeStamp = None

				if (date):
					timeStamp = datetime.strptime(date.__str__(), '%Y:%m:%d %H:%M:%S')
					full_Date = timeStamp.strftime('%m-%d')
					year = str(timeStamp.year)

					target_dir_with_date = f"{args.target}/{year}/{full_Date}"
					os.makedirs(target_dir_with_date, exist_ok=True)
					if args.mode == 'cp':
						shutil.copy(pic, target_dir_with_date)
					elif args.mode == 'mv':
						shutil.move(pic, target_dir_with_date)
				else:
					log(f"Skipping {pic}: cannot extract EXIF tags.")
		else:
			log(f"Skipping {pic}: unknown file extension.")
