"""Warzone Map Buddy - Helps you build your Warzone Maps

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
"""

from docopt import docopt
from xml.dom import minidom
import requests
import json
import os

def get_territories_without_names(doc):
    territories = []
    paths = filter(lambda x: 'Territory_' in x.getAttribute('id'), doc.getElementsByTagName('*'))
    for path in paths:
        territory_id=path.getAttribute('id')
        territory_name=""
        if len(path.getElementsByTagName('title')) != 0:
            territory_name=path.getElementsByTagName('title')[0].firstChild.data
        if territory_name == "":
            territory_name=path.getAttribute('inkscape:label')
        if territory_name == "" or "#" in territory_name:
            territories.append(path)
    return territories

def get_territory_ids(doc):
    paths = filter(lambda x: 'Territory_' in x.getAttribute('id'), doc.getElementsByTagName('*'))
    territory_ids = list(map(lambda x: int(x.getAttribute('id').replace('Territory_', '')), paths))
    territory_ids.sort()
    return territory_ids

def missing_elements(lst):
    return [x for x in range(lst[0], lst[-1]+1) if x not in lst] 

def get_territory_name(path):
    territory_name=""
    if len(path.getElementsByTagName('title')) != 0:
        territory_name=path.getElementsByTagName('title')[0].firstChild.data
    if territory_name == "":
        territory_name=path.getAttribute('inkscape:label')
    return territory_name

def get_name_commands(doc):
    has_errors = False
    territory_commands = []
    paths = filter(lambda x: 'Territory_' in x.getAttribute('id'), doc.getElementsByTagName('*'))
    for path in paths:
        territory_id = path.getAttribute('id')
        territory_name = get_territory_name(path)
        
        if territory_name != "" and "#" not in territory_name:
            if territory_name in map(lambda x: x['name'],territory_commands):
                has_errors = True
                print("Duplicate: ", territory_name)
            territory_commands.append({
                'command': 'setTerritoryName',
                'id': int(territory_id.replace('Territory_', '')),
                'name': territory_name,
            })

    return (territory_commands, has_errors)

def get_bonus_value(territories_number, is_capital):
    if is_capital:
        return int(3.5 + max(territories_number*0.8, 1)*2)
    if territories_number == 1:
        return 2
    return int(territories_number*0.55)

def get_penalty_commands(doc):
    penalty_commands = []
    penalty_layer = list(filter(lambda x: 'penalty' in x.getAttribute('inkscape:label').lower(), doc.getElementsByTagName('g')))[0]
    penalties = list(filter(lambda x: 'Territory_' in x.getAttribute('id'), penalty_layer.getElementsByTagName('*')))
    for penalty in penalties:
        penalty_name = "- " + get_territory_name(penalty)
        penalty_commands.append({
            "command": 'addBonus',
            "name": penalty_name,
            "armies": -1,
            "color": "#000000"
        })
        penalty_commands.append({
            "command": 'addTerritoryToBonus',
            "id": int(penalty.getAttribute('id').replace("Territory_", "")),
            "bonusName": penalty_name
        })
    return penalty_commands, False

def get_bonus_commands(doc):
    bonus_commands = []
    groups = filter(lambda x: 'bonus' in x.getAttribute('inkscape:label').lower(), doc.getElementsByTagName('g'))
    for g in groups:
        territories = list(filter(lambda x: 'Territory_' in x.getAttribute('id'), g.getElementsByTagName('*')))
        style = territories[0].getAttribute('style')
        stroke = list(filter(lambda x: 'fill:' in x, style.split(";")))[0]
        print(g.getAttribute('id'))
        is_capital = "Capital:" in  g.getAttribute('id')
        bonus_name = g.getAttribute('id').replace("_", " ")
        bonus_commands.append({
            "command": 'addBonus',
            "name": bonus_name,
            "armies": get_bonus_value(len(territories), is_capital),
            "color": stroke.split(":")[1].strip()
        })
        for territory in territories:
            bonus_commands.append({
                "command": 'addTerritoryToBonus',
                "id": int(territory.getAttribute('id').replace("Territory_", "")),
                "bonusName": bonus_name
            })
    return bonus_commands, False

def send_to_warzone(email, token, mapid, commands):
    warzone_endpoint = "https://www.warzone.com/API/SetMapDetails"
    payload = {
        "email": email,
        "APIToken": token,
        "mapID": mapid,
        "commands": commands
    }
    req = requests.post(warzone_endpoint, data=json.dumps(payload))
    print(req.json())

def show_territory_gaps(doc):
    territory_ids = get_territory_ids(doc)
    print("Last ID: ", territory_ids[len(territory_ids)-1])
    print("Skipped IDs: ", missing_elements(territory_ids))

def save(doc, out_file):
    with open(out_file, "w") as xml_file:
        doc.writexml(xml_file)

def removeAllTags(doc, tag):
    tags = doc.getElementsByTagName(tag)
    for t in tags:
        t.parentNode.removeChild(t)

def clean_style(style):
    styles = filter(lambda x: "fill" in x or "stroke" in x, style.split(","))
    return ";".join(styles)

def lighten(file_path):
    territories = []
    doc = minidom.parse(file_path)
    paths = filter(lambda x: 'BonusLink_' in x.getAttribute('id'), doc.getElementsByTagName('*'))
    for path in paths:
        attrkeys = [*path.attributes._attrs.keys()]
        for attr in attrkeys:
            if attr not in ['d', 'id', 'transform', 'width', 'height', 'x', 'y', 'ry', 'rx']:
                path.removeAttribute(attr)

    paths = filter(lambda x: 'Territory_' in x.getAttribute('id'), doc.getElementsByTagName('*'))
    for path in paths:
        children = path.getElementsByTagName('*')
        for child in children:
            path.removeChild(child)
        attrkeys = [*path.attributes._attrs.keys()]
        for attr in attrkeys:
            if attr not in ['d', 'id', 'transform']:
                path.removeAttribute(attr)
                
    paths = doc.getElementsByTagName('g')
    for path in paths:
        attrkeys = [*path.attributes._attrs.keys()]
        for attr in attrkeys:
            if attr not in ['transform']:
                path.removeAttribute(attr)

    paths = filter(lambda x: not ('Information' in x.getAttribute('id') or 'BonusLink_' in x.getAttribute('id') or 'portal' in x.getAttribute('inkscape:label')), doc.getElementsByTagName('*'))
    for path in paths:
        if "style" in path.attributes._attrs.keys():
            path.setAttribute('style', clean_style(path.getAttribute('style')))

        attrkeys = [*path.attributes._attrs.keys()]
        for attr in attrkeys:
            if attr not in ['d', 'id', 'transform', 'style'] and path.nodeName != "svg":
                path.removeAttribute(attr)

        if 'Territory_' in path.getAttribute('id'):
            for child in path.getElementsByTagName('*'):
                child.parentNode.removeChild(child)
        if 'Territory_' not in path.getAttribute('id'):
            for child in path.getElementsByTagName('title'):
                child.parentNode.removeChild(child)

    removeAllTags(doc, 'defs')
    removeAllTags(doc, 'sodipodi:namedview')

    return doc

def clean(file_name, out_file_name):
    out_file = file_name.split(".svg")[0] + ".light.svg"
    if out_file_name is not None:
        out_file = out_file_name
    doc = lighten(file_name)
    save(doc, out_file_name)

def highlight(file_name, out_file_name):
    out_file = file_name.split(".svg")[0] + ".highlighted.svg"
    if out_file_name is not None:
        out_file = out_file_name

    doc = minidom.parse(file_name)
    territories = get_territories_without_names(doc)
    for t in territories:
        style = t.getAttribute("style")
        stroke = list(filter(lambda x: 'stroke:' in x, style.split(";")))[0]
        t.setAttribute("style", style.replace(stroke, "stroke:#ffffff"))
    save(doc, out_file_name)

def get_dict(dictionary, name):
    try:
        return dictionary[name]
    except:
        return None

def file_size(path):
    return os.stat(path).st_size

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Warzone Map Buddy 1.0.0')
    doc = minidom.parse(arguments["<file>"])
    commands = []
    commands_have_errors = False
    if arguments["--debug"]:
        print(arguments)

    if arguments["--find-skipped-ids"]:
        show_territory_gaps(doc)

    if arguments["--clean"] is not None:
        clean(arguments["<file>"], arguments["--clean"])
        print(file_size(arguments["--clean"]))

    if arguments["--highlight-unnamed"]:
        highlight(arguments["<file>"], arguments["--highlight-unnamed"])

    if arguments["--update-territory-names"]:
        name_commands, err = get_name_commands(doc)
        commands_have_errors = commands_have_errors or err
        commands = commands + name_commands

    if arguments["--create-bonuses"]:
        bonus_commands, err = get_bonus_commands(doc)
        commands_have_errors = commands_have_errors or err
        commands = commands + bonus_commands

    if arguments["--create-penalties"]:
        penalty_commands, err = get_penalty_commands(doc)
        commands_have_errors = commands_have_errors or err
        commands = commands + penalty_commands

    if arguments["--size"]:
        print(file_size(arguments["<file>"]))

    if arguments["--debug"]:
        print("commands: ", commands)
        
    if not commands_have_errors:
        if len(commands) > 0:
            if arguments["--email"] is None:
                print("Missing required parameter --email")
            if arguments["--api-token"] is None:
                print("Missing required parameter --api-token")
            if arguments["--mapid"] is None:
                print("Missing required parameter --mapid")
            send_to_warzone(arguments["--email"], arguments["--api-token"], arguments["--mapid"], commands)
    else:
        print("Found issues while validating the commands to send. See above.")
