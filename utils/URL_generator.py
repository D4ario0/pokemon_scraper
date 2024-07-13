from typing import Generator
from csv import DictReader

class URLGenerator:
    def __init__(self, filepath):
        self.url = "https://pokemondb.net/pokedex/%s"
        self.filepath = filepath

    def generate(self) -> Generator:
        with open(self.filepath, "r") as pkmns:
            names = DictReader(pkmns)
            for row in names:
                yield self.url % row["Name"]
