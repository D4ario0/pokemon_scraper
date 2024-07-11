from selectolax.parser import HTMLParser, Node
from URL_generator import URLGenerator
from tags import add_tags
import requests
import time
import json
import re

current_number = 1

ability_re = re.compile(r"[0-9]\.\s*([A-Za-z\s]+)")
h_ability_re = re.compile(r"(?:[a-z])([A-Z][a-zA-Z\s]*\s*\(hidden ability\))")


def generate_id() -> None:
    global current_number
    id = f"p{current_number:03d}"
    current_number += 1
    return id


def get_rows(node: Node) -> list[str]:
    td_elements = [td.text(deep=True).strip() for td in node.css("td")]
    return td_elements


def format_name(name:str, form:str) -> str:
    return form if form.endswith(name) else f"{name} {form}"


def extract_basics(pokemon: dict, table: list[str], name: str) -> None:
    pokemon["id"] = generate_id()
    pokemon["dexNumber"] = int(table[0])
    pokemon["name"] = name
    pokemon["types"] = table[1].split()
    pokemon["height"] = float(table[3].split(maxsplit=1)[0])
    pokemon["weight"] = float(table[4].split(maxsplit=1)[0])
    h_ability = "".join(h_ability_re.findall(table[5]))
    pokemon["abilities"] = ability_re.findall(table[5].removesuffix(h_ability)) or ["Undiscovered"]
    pokemon["hidden_ability"] = h_ability.strip().removesuffix(" (hidden ability)") or "Undiscovered"
    return


def extract_misc(pokemon: dict, table: list[str]) -> None:
    pokemon["EV_yield"] = table[0]
    pokemon["catch_rate"] = int(table[1].split(maxsplit=1)[0])
    pokemon["base_friendship"] = int(table[2].split(maxsplit=1)[0])
    pokemon["base_exp"] = int(table[3])
    pokemon["growth_rate"] = table[4]
    return


def extract_breeding(pokemon: dict, table: list[str]) -> None:
    pokemon["egg_groups"] = table[0].strip().split()
    pokemon["egg_cycles"] = int(table[2].split(maxsplit=1)[0])
    return


def extract_stats(pokemon: dict, table: list[str]) -> None:
    pokemon["HP"] = int(table[0])
    pokemon["ATA"] = int(table[1])
    pokemon["DEF"] = int(table[2])
    pokemon["SPA"] = int(table[3])
    pokemon["SPD"] = int(table[4])
    pokemon["SPE"] = int(table[5])
    pokemon["BST"] = int(table[6])
    return


def parse_response(html: str) -> list[dict]:
    tree = HTMLParser(html)
    name = tree.css_first("h1").text()
    forms = tree.css_first(".sv-tabs-tab-list").text().strip().split(sep="\n")
    tables = tree.css(".vitals-table")
    CHUNK_SIZE = 4
    pokemon_forms = []

    for idx, form in enumerate(forms):
        start = idx * CHUNK_SIZE
        end = start + CHUNK_SIZE
        info = tables[start:end]

        pokemon = {}

        table = get_rows(info.pop(0))
        extract_basics(pokemon, table, format_name(name, form))

        table = get_rows(info.pop(0))
        extract_misc(pokemon, table)

        table = get_rows(info.pop(0))
        extract_breeding(pokemon, table)

        table = get_rows(info.pop(0))[::4]
        extract_stats(pokemon, table)

        pokemon["tags"] = add_tags(pokemon["name"], pokemon["dexNumber"])

        print(pokemon)
        pokemon_forms.append(pokemon)
    
    return pokemon_forms

def save_to_json(data:list[dict], filename:str):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)


def main():
    urls = URLGenerator().generate()
    pokemons = []
    for url in urls:
        response = requests.get(url).text
        pokemons += parse_response(response)
        #
        time.sleep(4)

    save_to_json(pokemons,"pokemonDB.json")

if __name__ == "__main__":
    main()