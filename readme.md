# Warzone Map Buddy

## Features
* Find skipped territory IDs
* Territory naming help
    * Updating territory names
    * Highlighting unnamed territories
* Cleanup SVG file (Warzone limits uploads to `2000000` bytes)
* Creating bonuses (and adding territories to that bonus)

Note: requires [Python](https://www.python.org/downloads/) to use

Feel free to create an [issue](https://github.com/dosaki/warzone-map-buddy/issues) if you find a bug, have a suggestion, or need clarification.

## Before using
### Download & setup
1. Download the [warzone-map-buddy zip](https://github.com/dosaki/warzone-map-buddy/archive/master.zip) or clone this repository
2. Open a terminal window
3. Navigate to the directory where you've downloaded warzone-map-buddy (`cd /path/to/directory`)
4. Install the dependencies with `pip install -r requirements.txt`

### Get your Warzone token
Get your token here: https://www.warzone.com/API/GetAPIToken (you need to be logged in to Warzone on your browser).

More info here: https://www.warzone.com/wiki/Get_API_Token_API

## Usage examples

### Check which territories you haven't named yet:
```shell
warzone-map-buddy.py --highlight-unnamed="your-file.highlighted.svg" "your-file.svg"
```

### Clean up the file for upload:
```shell
warzone-map-buddy.py --clean="your-file.cleaned.svg" "your-file.svg"
```

### Update Warzone map with territory names:
```shell
warzone-map-buddy.py --email="your@email.com" --api-token="your-Token" --mapid=123456 --update-territory-names "your-file.svg"
```

### Update Warzone map with **new** bonuses:
Warzone doesn't support updating bonuses via their API
```shell
warzone-map-buddy.py --email="your@email.com" --api-token="your-Token" --mapid=123456 --create-bonusess "your-file.svg"
```

## Full `--help`
```
Usage:
  warzone-map-buddy.py [options] <file>
  warzone-map-buddy.py (-h | --help)
  warzone-map-buddy.py --version

Options:
  -h --help                      Show this screen.
  --version                      Show version.
  --update-territory-names       Updates territory names by matching the id with the title (or label, if title is empty)
  --create-bonuses               Create bonuses (new ones will be added every time) based on groups' IDs with the label "bonus". Will take the fill colour of one of the territories inside the group.
  --create-penalties             Create penalties (new ones will be added every time) based on each territory in a layer called "Penalties"
  --clean=<out-file>             Clean up the SVG to make it lighter (for uploading)
  --find-skipped-ids             Find skipped territory IDs
  --highlight-unnamed=<out-file> Highlight territories (with white border) without a name in their label or title
  --api-token=<token>            API Access Token (find yours here: https://www.warzone.com/API/GetAPIToken)
  --email=<email>                Your account email address
  --mapid=<id>                   The Map ID (find it in "Link for Sharing")
  --size                         Prints the file size in bytes
  --debug                        Shows what arguments you ran
```