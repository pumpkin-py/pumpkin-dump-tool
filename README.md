# pumpkin-dump-grapher

CLI tool for creating graphs from pumpkin.py database dumps.


## Installation

```bash
git clone ...
cd pumpkin-dump-grapher
# optionally:
python3 -m venv .venv
source .venv/bin/activate
```

## Generate CSV from dump files

```bash
usage: grapher extract [-h] --user USER --guild GUILD --content CONTENT
                       [--allow-overwrite]
                       directory output

positional arguments:
  directory          path to dump directory
  output             path to output file

optional arguments:
  -h, --help         show this help message and exit
  --user USER        Discord user ID
  --guild GUILD      Discord guild ID
  --content CONTENT  type of content ('karma', 'karma-given', 'karma-
                     taken', 'points', 'hug', 'pet', 'hyperpet', 'lick',
                     'hyperlick', 'spank')
  --allow-overwrite  overwrite old files without asking

```

```bash
python3 -m grapher extract --user $USER_ID --guild $GUILD_ID --content points dumps/ ${GUILD_ID}_${USER_ID}_points.csv
```
