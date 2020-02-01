```
usage: reorganize.py [-h] [-f] {cp,mv} source target

Reorganize jpg files in a directory, so that:
target
|___year
|   |___month-day

Recognizable file extensions: jpg, jpeg, jpe, jfif (not case sensitive).

positional arguments:
  {cp,mv}      copy (cp) or move (mv) files
  source       source directory
  target       parent directory for the reorganized files

optional arguments:
  -h, --help   show this help message and exit
  -f, --force  overwrite file if exist
```