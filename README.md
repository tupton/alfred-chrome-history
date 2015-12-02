# Alfred Chrome History Workflow

Access your Google Chrome history from Alfred with `ch {query}`.

![alfred chrome history workflow](screenshot.png)

## How to install

Clone this repo and symlink it to `<sync directory>/Alfred.alfredpreferences/workflows/alfred-chrome-history`. Your Alfred sync directory can be found going to Preferences → Advanced → Syncing.

Or [download the workflow from the releases page][releases].

  [releases]: https://github.com/tupton/alfred-chrome-history/releases

## How to build

`make workflow` will put any dependencies in place and build `alfred-chrome-history.alfredworkflow` in the current directory.

Note that `sitepackages.py` attempts to find `alfred.py` and copy it into the workflow archive. Please let me know if this script fails to find `alfred.py`. It attempts to find it in both global installations and within a virtualenv, but I have only tested this on my local machine.

## Thanks

This workflow uses the wonderful [alfred-python][ap] library. It is provided in the generated workflow and does not need to be installed globally or otherwise before using this workflow.

  [ap]: https://github.com/nikipore/alfred-python
