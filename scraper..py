from selectolax.parser import HTMLParser, Node
from URL_generator import URLGenerator
from typing import List, Dict
import requests
import json
import re


# urls = URLGenerator()
url = "https://pokemondb.net/pokedex/gyarados"
response = requests.get(url).text
current_number = 1

ability_re = re.compile(r"[0-9]\.\s*([A-Za-z\s]+)")
h_ability_re = re.compile(r"(?:[a-z])([A-Z][a-zA-Z\s]*\s*\(hidden ability\))")


def generate_id() -> None:
    global current_number
    id = f"p{current_number:03d}"
    current_number += 1
    return id


def get_rows(node: Node) -> List[str]:
    td_elements = [td.text(deep=True).strip() for td in node.css("td")]
    return td_elements


def extract_basics(pokemon: Dict, table: List[str], form: str) -> None:
    pokemon["id"] = generate_id()
    pokemon["dexNumber"] = int(table[0])
    pokemon["name"] = form
    pokemon["types"] = table[1].split()
    pokemon["height"] = float(table[3].split(maxsplit=1)[0])
    pokemon["weight"] = float(table[4].split(maxsplit=1)[0])
    h_ability = "".join(h_ability_re.findall(table[5]))
    pokemon["abilities"] = ability_re.findall(table[5].removesuffix(h_ability))
    pokemon["hidden_ability"] = h_ability.strip().removesuffix(" (hidden ability)")
    return


def extract_misc(pokemon: Dict, table: List[str]) -> None:
    pokemon["EV_yield"] = table[0]
    pokemon["catch_rate"] = int(table[1].split(maxsplit=1)[0])
    pokemon["base_friendship"] = int(table[2].split(maxsplit=1)[0])
    pokemon["base_exp"] = int(table[3])
    pokemon["growth_rate"] = table[4]
    return


def extract_breeding(pokemon: Dict, table: List[str]) -> None:
    pokemon["egg_groups"] = table[0].strip().split()
    pokemon["egg_cycles"] = int(table[2].split(maxsplit=1)[0])
    return


def extract_stats(pokemon: Dict, table: List[str]) -> None:
    pokemon["HP"] = table[0]
    pokemon["ATA"] = table[1]
    pokemon["DEF"] = table[2]
    pokemon["SPA"] = table[3]
    pokemon["SPD"] = table[4]
    pokemon["SPE"] = table[5]
    pokemon["BST"] = table[6]
    return


def parse_response(html: str) -> List[Dict]:
    tree = HTMLParser(html)
    forms = tree.css_first(".sv-tabs-tab-list").text().strip().split(sep="\n")
    tables = tree.css(".vitals-table")
    evo_info = tree.css(".infocard-list-evo")
    CHUNK_SIZE = 4
    pokemon_forms = []

    for idx, form in enumerate(forms):
        start = idx * CHUNK_SIZE
        end = start + CHUNK_SIZE
        info = tables[start:end]

        pokemon = {}

        table = get_rows(info.pop(0))
        extract_basics(pokemon, table, form)

        table = get_rows(info.pop(0))
        extract_misc(pokemon, table)

        table = get_rows(info.pop(0))
        extract_breeding(pokemon, table)

        table = get_rows(info.pop(0))[::4]
        extract_stats(pokemon, table)

        pokemon_forms.append(pokemon)


parse_response(response)
