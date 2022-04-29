# TermCast
A terminal-based podcast player from RSS feeds

## Installation
This requires VLC Media Player to be installed

On linux

`sudo snap install vlc`

or

`sudo apt install vlc`

On Mac

`brew install vlc`

Or download from [here](https://www.videolan.org/vlc/)

Dependencies are mangaged with poetry. Installation instructions are [here](https://python-poetry.org/docs/)

Dependencies can be installed by running

`poetry install`

## Usage
RSS feed links must be added to a `sources.txt` file in the root directory. An example is available in `example_sources.txt`

The player can be run with

`poetry run python main.py`

The player can be navigated by either keyboard or mouse.
On keyboard, the arrow keys can be used to navigate within a widget and tab will switch between widgets.
