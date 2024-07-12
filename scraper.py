from selectolax.parser import HTMLParser, Node
from utils import add_tags, URLGenerator
from aiohttp import ClientSession
import asyncio
import json
import re

ability_re = re.compile(r"[0-9]\.\s*([A-Za-z\s]+)")
h_ability_re = re.compile(r"(?:[a-z])([A-Z][a-zA-Z\s]*\s*\(hidden ability\))")
integers = re.compile(r"^-?\d+$")
floats = re.compile(r"^-?\d*\.\d+$")

current_number = 1

def generate_id() -> None:
    """Generates a unique identifier for a Pokémon entry."""
    global current_number
    id = f"p{current_number:03d}"
    current_number += 1
    return id


def get_rows(node: Node) -> list[str]:
    """Extracts text content from table data (td) elements within a given node."""
    td_elements = [td.text(deep=True).strip() for td in node.css("td")]
    return td_elements


def format_name(name:str, form:str) -> str:
    """Formats the name of a Pokémon with its form."""
    return form if form.endswith(name) else f"{name} {form}"


def format_numbers(text:str) -> int | float | None:
    """Formats a text string into an integer or float if applicable."""
    number = text.split(maxsplit=1)[0]
    if integers.match(number):
        return int(number)
    if floats.match(number):
        return float(number)
    return None


def extract_basics(pokemon: dict, table: list[str], name: str) -> None:
    """Extracts basic information about a Pokémon from a table and updates the Pokémon dictionary."""
    pokemon["id"] = generate_id()
    pokemon["dexNumber"] = int(table[0])
    pokemon["name"] = name
    pokemon["types"] = table[1].split()
    pokemon["height"] = format_numbers(table[3])
    pokemon["weight"] = format_numbers(table[4])
    h_ability = "".join(h_ability_re.findall(table[5]))
    pokemon["abilities"] = ability_re.findall(table[5].removesuffix(h_ability)) or ["Undiscovered"]
    pokemon["hidden_ability"] = h_ability.strip().removesuffix(" (hidden ability)") or "Undiscovered"
    return


def extract_misc(pokemon: dict, table: list[str]) -> None:
    """Extracts miscellaneous information about a Pokémon from a table and updates the Pokémon dictionary."""
    pokemon["EV_yield"] = table[0]
    pokemon["catch_rate"] = format_numbers(table[1])
    pokemon["base_friendship"] = format_numbers(table[2])
    pokemon["base_exp"] = int(table[3])
    pokemon["growth_rate"] = table[4]
    return


def extract_breeding(pokemon: dict, table: list[str]) -> None:
    """Extracts breeding information about a Pokémon from a table and updates the Pokémon dictionary."""
    pokemon["egg_groups"] = table[0].strip().split()
    pokemon["egg_cycles"] = format_numbers(table[2])
    return


def extract_stats(pokemon: dict, table: list[str]) -> None:
    """Extracts statistical information about a Pokémon from a table and updates the Pokémon dictionary."""
    pokemon["HP"] = int(table[0])
    pokemon["ATA"] = int(table[1])
    pokemon["DEF"] = int(table[2])
    pokemon["SPA"] = int(table[3])
    pokemon["SPD"] = int(table[4])
    pokemon["SPE"] = int(table[5])
    pokemon["BST"] = int(table[6])
    return


def parse_response(html: str) -> list[dict]:
    """Parses the HTML response to extract information about Pokémon and returns a list of Pokémon dictionaries."""
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
        try:
            table = get_rows(info.pop(0))
            extract_basics(pokemon, table, format_name(name, form))
        except Exception as e:
            print(f"There is an issue with {pokemon["name"]}: {e}")

        try:
            table = get_rows(info.pop(0))
            extract_misc(pokemon, table)
        except Exception as e:
            print(f"There is an issue with {pokemon["name"]}: {e}")

        try:
            table = get_rows(info.pop(0))
            extract_breeding(pokemon, table)
        except Exception as e:
            print(f"There is an issue with {pokemon["name"]}: {e}")
        
        try:
            table = get_rows(info.pop(0))[::4]
            extract_stats(pokemon, table)
        except Exception as e:
            print(f"There is an issue with {pokemon["name"]}: {e}")

        pokemon["tags"] = add_tags(pokemon["name"], pokemon["dexNumber"])

        print(pokemon["name"])
        pokemon_forms.append(pokemon)
    
    return pokemon_forms


def save_to_json(data:list[dict], filename:str):
    """Saves a list of Pokémon dictionaries to a JSON file."""
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)


async def fetch(session: ClientSession, url:str, results:list[dict]) -> None:
    """Fetches data from a URL and parses the response to update the results list."""
    async with session.get(url) as response:
        results.extend(parse_response(await response.text()))


# Given pokemondb.net robots.txt policy of 4 seconds per requests no asynchronous library was considered
async def main():
    """Main function to generate URLs, fetch Pokémon data, and save it to a JSON file."""
    urls = URLGenerator("poke_list.csv").generate()
    pokemons = []

    async with ClientSession() as session:
        for url in urls:
            await fetch(session, url, pokemons)
            await asyncio.sleep(4)

    save_to_json(pokemons,"pokemonDB.json")

asyncio.run(main())