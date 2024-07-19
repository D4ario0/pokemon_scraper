from selectolax.parser import HTMLParser, Node
from itertools import batched
from dataclasses import asdict
from tinydb.table import Table
from tinydb import TinyDB
import re

from .models import Pokemon, Stats
from .constants import *

# REGEX PATTERNS
ABILITY = re.compile(r"[0-9]\.\s*([A-Za-z\s]+)")
H_ABILITY = re.compile(r"(?:[a-z])([A-Z][a-zA-Z\s]*\s*\(hidden ability\))")
INT = re.compile(r"^-?\d+$")
FLOAT = re.compile(r"^-?\d*\.\d+$")

# MAIN PARSING LOGIC


def parse_response(html: str, db_table: Table) -> None:
    """Parses the HTML response to extract information about Pokémon and appends the entry to the database."""
    tree = HTMLParser(html)

    # Information about a pokemon form is displayed in 4 tables with a class named "vitas-table"
    CHUNK_SIZE = 4

    pokemon_name = tree.css_first("h1").text()
    pokemon_forms = tree.css_first(".sv-tabs-tab-list").text().strip().split(sep="\n")
    tables = batched(tree.css(".vitals-table"), CHUNK_SIZE)

    EXTRACTORS = [extract_basics, extract_misc, extract_breeding, extract_stats]

    # Map every form detected to a set of 4 tables
    for form, table_set in zip(pokemon_forms, tables):

        pokemon = Pokemon(name=format_name(pokemon_name, form))

        # Map each extracting function to each table to perform the data extraction
        try:

            for func, table in zip(EXTRACTORS, table_set):
                func(pokemon, get_table_rows(table))

        except Exception as e:
            print(f"There is an issue with {pokemon.name}: {e}")

        pokemon.tags = add_tags(pokemon.name, pokemon.dex_number)

        print(pokemon.name)
        db_table.insert(asdict(pokemon))


def extract_basics(pokemon: Pokemon, table: list[str]) -> None:
    """Extracts basic information about a Pokémon from a table and updates the Pokemon dictionary."""
    pokemon.dex_number = format_number(table[0])

    types = table[1].split()
    pokemon.primary_type = types[0]
    pokemon.secondary_type = types[1] if len(types) > 1 else None

    pokemon.height = format_number(table[3])
    pokemon.weight = format_number(table[4])

    h_ability = "".join(H_ABILITY.findall(table[5]))
    pokemon.abilities = ABILITY.findall(table[5].removesuffix(h_ability)) or ["Undiscovered"]
    pokemon.hidden_ability = (h_ability.strip().removesuffix(" (hidden ability)") or "Undiscovered")


def extract_misc(pokemon: Pokemon, table: list[str]) -> None:
    """Extracts miscellaneous information about a Pokémon from a table and updates the Pokemon dictionary."""
    pokemon.EV_yield = table[0]
    pokemon.catch_rate = format_number(table[1])
    pokemon.base_friendship = format_number(table[2])
    pokemon.base_exp = format_number(table[3])
    pokemon.growth_rate = table[4]


def extract_breeding(pokemon: Pokemon, table: list[str]) -> None:
    """Extracts breeding information about a Pokémon from a table and updates the Pokemon dictionary."""
    egg_groups = table[0].strip().split()
    valid_groups = []

    for i, word in enumerate(egg_groups):
        if word == "Water":
            word = f"{word} {egg_groups[i + 1]}"

        if word in EGG_GROUPS:
            valid_groups.append(word)

    pokemon.primary_egg_group = (valid_groups[0] if len(valid_groups) > 0 else "Undiscovered")
    pokemon.secondary_egg_group = (valid_groups[1] if len(valid_groups) > 1 else None)

    pokemon.egg_cycles = format_number(table[2])


def extract_stats(pokemon: Pokemon, table: list[str]) -> None:
    """Extracts stats information about a Pokémon, parses to int the results and updates the Pokemon dictionary."""
    extracted_stats = map(int, table[::4])
    pokemon.stats = Stats(*extracted_stats)


# PARSING HELPERS


def get_table_rows(node: Node) -> list[str]:
    """Extracts text content from table data (td) elements within a given node."""
    td_elements = [td.text(deep=True).strip() for td in node.css("td")]
    return td_elements


def format_name(name: str, form: str) -> str:
    """Formats the name of a Pokémon with its form."""
    special_forms = (name, "X", "Y", "♀", "♂")
    return form if form.endswith(special_forms) else f"{name} {form}"


def format_number(text: str) -> int | float | None:
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

    # Preloads "is_category" with dexNumber and short-circuits appending if false
    rang_check = lambda ranges, tag: is_category(number, ranges) and tags.append(tag)
    rang_check(STARTER, "Starter")
    rang_check(LEGENDARY, "Legendary")
    rang_check(FOSSIL, "Fossil")
    rang_check(ULTRA_BEAST, "Ultra Beast")
    rang_check(PARADOX_FORMS, "Paradox Form")

    # Preloads "is_form" with form and short-circuits appending if false
    form_check = lambda gimmick, tag: is_form(form, gimmick) and tags.append(tag)
    form_check("Mega", "Mega-Evolution")
    form_check("Alolan", "Alolan Form")
    form_check("Galarian", "Galarian Form")
    form_check("Hisuian", "Hisuian Form")
    form_check("Paldean", "Paldean Form")

    form in VGC_CHAMPS and tags.append("World Champion")
    number in MYTHICAL and tags.append("Mythical")
    number in PSEUDO_LEGENDARY and tags.append("Pseudo-Legendary")

    tags.append(is_gen(number, form, GENERATION))

    return tags


# TAGGING HELPERS


def is_gen(dex_number: int, form: str, gen_ranges: list[tuple[int, int]]) -> str:
    """Check if Pokémon's dex number falls within any given range and returns the tag if true."""

    if form.startswith("Alolan"):
        return "Generation 7"
    if form.startswith("Galarian"):
        return "Generation 8"
    if form.startswith("Hisuian"):
        return "Generation 8"
    if form.startswith("Paldean") or form.endswith("Breed"):
        return "Generation 9"

    for i, (min_dex, max_dex) in enumerate(gen_ranges):
        if min_dex <= dex_number <= max_dex:
            return f"Generation {i + 1}"


def is_category(dex_number: int, category_ranges: list[tuple[int, int]]) -> bool:
    """Check if pokemon's dex number falls within any given range and returns the tag if true."""
    return any(min_dex <= dex_number <= max_dex for min_dex, max_dex in category_ranges)


def is_form(form: str, target: str) -> bool:
    """Check if pokemon's form starts with the target prefix and returns the tag if true."""
    return form.startswith(f"{target} ")
