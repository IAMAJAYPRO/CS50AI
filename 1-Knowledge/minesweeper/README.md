Here's how you can format the command-line usage information for your `README.md`:


## Usage

Run the following command to see the available options:

```bash
py runner.py -h
```

You should see the following output:

```
pygame 2.5.2 (SDL 2.28.3, Python 3.12.0)
Hello from the pygame community. https://www.pygame.org/contribute.html
usage: runner.py [-h] [-d] [--dim HEIGHT WIDTH | --square SIZE] [--mines N_mines] [--expand | -E]

options:
  -h, --help            show this help message and exit
  -d, --debug           shows color for what ai thinks is safe/mine. RED=Mine, Green=Safe.
  --dim HEIGHT WIDTH, --dimensions HEIGHT WIDTH
                        Specify height and width.
  --square SIZE, --size SIZE
                        Specify the size for both height and width.
  --mines N_mines       number of mines, default 8
  --expand              Expand the 0 neighbours chain (default)
  -E                    Do not expand the 0 neighbours chain

Debugger by @IAMAJAYPRO. Also added color differences (the game looks better) (UI)
```
