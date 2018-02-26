# Alfred Chrome History Workflow

Access your Google Chrome history from Alfred with `ch {query}`.

![alfred chrome history workflow](screenshot.png)

## How to install

Clone this repo and symlink it to `<sync directory>/Alfred.alfredpreferences/workflows/alfred-chrome-history`. Your Alfred sync directory can be found going to Preferences → Advanced → Syncing.

Then run `make dev` to install requirements and set the repository up to be used as a workflow.

Or [download the workflow from the releases page][releases] and install by double-clicking it.

  [releases]: https://github.com/tupton/alfred-chrome-history/releases

## Configuration

The workflow should work out of the box with the `ch` prefix. If you'd like to change this, update the keyword in the Alfred workflow's script filter.

If simply typing `ch` does not yield any results, you might need to create the the following directory. Replace <YourFolder> with your username

    mkdir -p "/Users/<YourFolder>/Library/Caches/com.runningwithcrayons.Alfred-2/Workflow Data/"

The Alfred script filter is set up to use the default Chrome profile. If you need to use a different profile, update the `PROFILE` environment variable in the Alfred workflow's script filter.

By default, the script tries to grab favicons from a separate database. This can sometimes slow down the results, which is not desirable. To turn off favicon support, pass `--no-favicons` in the Alfred workflow's script filter. The last line of the script should look like the following:

    python chrome.py "${PROFILE}" "{query}" --no-favicons

## How to build

`make workflow` will put any dependencies in place and build `alfred-chrome-history.alfredworkflow` in the current directory.

Note that `sitepackages.py` attempts to find `alfred.py` and copy it into the workflow archive. Please let me know if this script fails to find `alfred.py`. It attempts to find it in both global installations and within a virtualenv, but I have only tested this on my local machine.

`make dev` also puts dependencies in place so that the workflow can work when symlinked to the correct workflows directory as mentioned above.

## Thanks

This workflow uses the wonderful [alfred-python][ap] library. It is provided in the generated workflow and does not need to be installed globally or otherwise before using this workflow.

  [ap]: https://github.com/nikipore/alfred-python
