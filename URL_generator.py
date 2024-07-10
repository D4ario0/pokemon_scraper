from pathlib import Path
from csv import DictReader


class URLGenerator:
    def __init__(self, filepath="./scraper/static/poke_list.csv"):
        self.url = "https://pokemondb.net/pokedex/%s"
        self.filepath = Path(filepath)

    def generate(self):
        with open(self.filepath, "r") as pkmns:
            names = DictReader(pkmns)
            for row in names:
                yield self.url % row["Name"]
