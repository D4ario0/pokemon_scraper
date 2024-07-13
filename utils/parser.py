from selectolax.parser import HTMLParser, Node
from collections import OrderedDict
from itertools import batched
from tinydb.table import Table
from tinydb import TinyDB
from .constants import *
import re

# REGEX PATTERNS
ABILITY = re.compile(r"[0-9]\.\s*([A-Za-z\s]+)")
H_ABILITY = re.compile(r"(?:[a-z])([A-Z][a-zA-Z\s]*\s*\(hidden ability\))")
INT = re.compile(r"^-?\d+$")
FLOAT = re.compile(r"^-?\d*\.\d+$")


# CONSTANTS INDEX
INDEXED_TYPES = OrderedDict((type_key, idx) for idx, type_key in enumerate(TYPES))
INDEXED_EG = OrderedDict((eg_key, idx) for idx, eg_key in enumerate(EGG_GROUPS))

def start_db(db: TinyDB) -> Table:
    type_table = db.table("types")
    eg_table = db.table("egg_group")
    pokemon_table = db.table("pokemon")

    for type_key, idx in INDEXED_TYPES.items():
        type_table.insert({'type': type_key, 'index': idx})


    for eg_key, idx in INDEXED_EG.items():
        eg_table.insert({'egg_group': eg_key, 'index': idx})
    
    return pokemon_table
    

# MAIN PARSING LOGIC
def parse_response(html: str, db_table: Table) -> None:
    """Parses the HTML response to extract information about Pokémon and appends the entry to the database."""
    tree = HTMLParser(html)

    name = tree.css_first("h1").text()
    forms = tree.css_first(".sv-tabs-tab-list").text().strip().split(sep="\n")
    
    #Information about pokemon forms come packed every 4 HTML tables
    CHUNK_SIZE = 4
    tables = batched(tree.css(".vitals-table"), CHUNK_SIZE)

    for form, info in zip(forms,tables):

        pokemon = {"name":format_name(name, form)}

        try:
            table = get_table_rows(info[0])
            extract_basics(pokemon, table)
        except Exception as e:
            print(f"There is an issue with {pokemon["name"]}: {e}")

        try:
            table = get_table_rows(info[1])
            extract_misc(pokemon, table)
        except Exception as e:
            print(f"There is an issue with {pokemon["name"]}: {e}")

        try:
            table = get_table_rows(info[2])
            extract_breeding(pokemon, table)
        except Exception as e:
            print(f"There is an issue with {pokemon["name"]}: {e}")
        
        try:
            table = get_table_rows(info[3])[::4]
            extract_stats(pokemon, table)
        except Exception as e:
            print(f"There is an issue with {pokemon["name"]}: {e}")

        pokemon["tags"] = add_tags(pokemon["name"], pokemon["dexNumber"])

        print(pokemon["name"])
        db_table.insert(pokemon)


def extract_basics(pokemon: dict, table: list[str]) -> None:
    """Extracts basic information about a Pokémon from a table and updates the Pokémon dictionary."""
    pokemon["dexNumber"] = format_number(table[0])
    pokemon["types"] = [INDEXED_TYPES[key] for key in table[1].split()]
    pokemon["height"] = format_number(table[3])
    pokemon["weight"] = format_number(table[4])
    h_ability = "".join(H_ABILITY.findall(table[5]))
    pokemon["abilities"] = ABILITY.findall(table[5].removesuffix(h_ability)) or ["Undiscovered"]
    pokemon["hidden_ability"] = h_ability.strip().removesuffix(" (hidden ability)") or "Undiscovered"


def extract_misc(pokemon: dict, table: list[str]) -> None:
    """Extracts miscellaneous information about a Pokémon from a table and updates the Pokémon dictionary."""
    pokemon["EV_yield"] = table[0]
    pokemon["catch_rate"] = format_number(table[1])
    pokemon["base_friendship"] = format_number(table[2])
    pokemon["base_exp"] = format_number(table[3])
    pokemon["growth_rate"] = table[4]


def extract_breeding(pokemon: dict, table: list[str]) -> None:
    """Extracts breeding information about a Pokémon from a table and updates the Pokémon dictionary."""
    pokemon["egg_groups"] = []

    egg_groups = table[0].strip().split()

    for i, word in enumerate(egg_groups):
        if word == "Water":
            word = f"{word} {egg_groups[i+1]}"
        
        word in INDEXED_EG and pokemon["egg_groups"].append(INDEXED_EG[word])
        
    pokemon["egg_cycles"] = format_number(table[2])


def extract_stats(pokemon: dict, table: list[str]) -> None:
    """Extracts statistical information about a Pokémon from a table and updates the Pokémon dictionary."""
    keys = ["HP", "ATA", "DEF", "SPA", "SPD", "SPE", "BST"]
    stats = map(int, table)

    pokemon.update(zip(keys, stats))


# PARSING HELPERS
def get_table_rows(node: Node) -> list[str]:
    """Extracts text content from table data (td) elements within a given node."""
    td_elements = [td.text(deep=True).strip() for td in node.css("td")]
    return td_elements


def format_name(name:str, form:str) -> str:
    """Formats the name of a Pokémon with its form."""
    special_forms = (name, "X", "Y", "(female)", "(male)")
    return form if form.endswith(special_forms) else f"{name} {form}"


def format_number(text:str) -> int | float | None:
    """Formats a text string into an integer or float if applicable."""
    number = text.split(maxsplit=1)[0]
    if INT.match(number):
        return int(number)
    if FLOAT.match(number):
        return float(number)
    return None


# TAGGING LOGIC - SEE constants.py for reference
def add_tags(form: str, number: int) -> list[str]:
    """Define relevant tags to the pokemon based on various criteria."""
    tags = []

    #Preloads "is_category" with dexNumber and short-circuits appending if false
    rang_check = lambda ranges, tag: is_category(number, ranges) and tags.append(tag)
    rang_check(STARTER, "Starter")
    rang_check(LEGENDARY, "Legendary")
    rang_check(FOSSIL, "Fossil")
    rang_check(ULTRA_BEAST, "Ultra Beast")
    rang_check(PARADOX_FORMS, "Paradox Form")

    #Preloads "is_form" with form and short-circuits appending if false
    form_check = lambda gimmick, tag: is_form(form, gimmick) and tags.append(tag)
    form_check("Mega", "Mega-Evolution")
    form_check("Alolan", "Alolan Form") 
    form_check("Galarian", "Galarian Form")
    form_check("Hisuian", "Hisuian Form")
    form_check("Paldean", "Paldean Form")

    form in VGC_CHAMPS and tags.append("World Champion")
    number in MYTHICAL and tags.append("Mythical")
    number in PSEUDO_LEGENDARIES and tags.append("Pseudo-Legendaries")

    tags.append(is_gen(number, form, GENERATION))

    return tags

# TAGGING HELPERS
def is_gen(dexNumber: int, form: str, gen_ranges: list[tuple[int, int]]) -> str:
    """Check if Pokémon's dex number falls within any given range and return the tag if true."""

    if form.startswith("Alolan"): return "Generation 7"
    if form.startswith("Galarian"): return "Generation 8"
    if form.startswith("Hisuian"): return "Generation 8"
    if form.startswith("Paldean") or form.endswith("Breed"): return "Generation 9"
    
    for i, (min_dex, max_dex) in enumerate(gen_ranges):
        if min_dex <= dexNumber <= max_dex:
            return f"Generation {i+1}"


def is_category(dexNumber:int, category_ranges: list[tuple[int, int]]) -> str|None:
    """Check if pokemon's dex number falls within any given range and return the tag if true."""
    return any(min_dex <= dexNumber <= max_dex for min_dex, max_dex in category_ranges)


def is_form(form: str, target: str) -> str|None:
    """Check if pokemon's form starts with the target prefix and return the tag if true."""
    return form.startswith(f"{target} ")
