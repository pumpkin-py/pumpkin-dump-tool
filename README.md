# pumpkin-dump-grapher

CLI tool for creating graphs from pumpkin.py database dumps.

The `cairosvg` requires system library `libcairo2`.


## Installation

```bash
# get the code
git clone git@github.com:pumpkin-py/pumpkin-dump-tool.git
cd pumpkin-dump-tool
# create virtual environment
python3 -m venv .venv
source .venv/bin/activate
# install the package
python3 -m pip install -e .
```

You can verify that the package installed by running

```
$ pumpkin-grapher
usage: grapher [-h] [-v] {extract,graph} ...

positional arguments:
  {extract,graph}

optional arguments:
  -h, --help       show this help message and exit
  -v, --version    show program's version number and exit
```

## Generate CSV from dump files

```
pumpkin-grapher extract
usage: pumpkin-grapher extract [-h] --guild GUILD --user USER --content CONTENT
                       [-d DIRECTORY] [-o OUTPUT] [--allow-overwrite]

optional arguments:
  -h, --help            show this help message and exit
  --guild GUILD         Discord guild ID
  --user USER           Discord user ID
  --content CONTENT     type of content ('karma', 'karma-given', 'karma-taken',
                        'points', 'hug', 'pet', 'hyperpet', 'lick', 'hyperlick',
                        'spank')
  -d DIRECTORY, --directory DIRECTORY
                        path to dump directory
  -o OUTPUT, --output OUTPUT
                        path to output file
  --allow-overwrite     overwrite old files without asking
```

```bash
python3 -m grapher extract --guild $GUILD_ID --user $USER_ID --content points -d dumps/
```

## Convert the CSV to table

```
pumpkin-grapher graph -h
usage: pumpkin-grapher graph [-h] [--allow-overwrite] source output

positional arguments:
  source             path to source CSV
  output             path to output file

optional arguments:
  -h, --help         show this help message and exit
  --allow-overwrite  overwrite old files without asking
```

```bash
pumpkin-grapher graph ${GUILD}_${USER}_${CONTENT}.csv ${GUILD}_${USER}_${CONTENT}.png
```
