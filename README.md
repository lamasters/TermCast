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

### Local sources
Create a local folder in the TermCast root called `termcast_sources`. This folder should contain the files `sources.json` and `listen_time.json`. An example file for each of these is included. `example_listen_time.json` can be copied directly into the folder as is. `example_sources.json` can be edited with your list of RSS feeds and then copied into the folder. Make sure to rename these to `sources.json` and `listen_time.json`. In the file `config.json` change `source_type` to `"local"` instead of `"git"`.

### Synced sources
Create a personal git repository called `termcast_sources`. Clone this repository into the TermCast root. Follow the instructions above and commit the files to your repository. Leave the `source_type` as `"git"` in `config.json`. If you change your sources, push the changes to the repository. At launch, TermCast will download the latest source list and listen times. When finished listening, changes to listen times will be pushed to the repository.

The player can be run with
`poetry run python main.py`

The player can be navigated by either keyboard or mouse.
On keyboard, the arrow keys can be used to navigate within a widget and tab will switch between widgets.
