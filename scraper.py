from aiohttp import ClientSession
from tinydb.table import Table
from tinydb import TinyDB
import asyncio

from utils import parse_response, start_db, URLGenerator


# Given pokemondb.net robots.txt policy of 4 seconds delay, requests will be delayed. Accidentally the scraper was
# tested against a no time restriction and the ~1_000 request were completed in roughly 2 seconds The scrape time for
# 1025 pokemon entries with a 4-second delay per request is ~1h10m, leave the script running in the background
async def main():
    """Main function to generate URLs, fetch Pokémon data, and save it to a JSON file."""
    urls = URLGenerator("poke_list.csv").generate()
    pokemon_table = start_db(TinyDB("pokemonDB.json"))

    async with ClientSession() as session:
        for url in urls:
            await fetch(session, url, pokemon_table)
            await asyncio.sleep(4)


async def fetch(session: ClientSession, url: str, table: Table) -> None:
    """Fetches data from a URL and parses the response to update the results list."""
    async with session.get(url) as response:
        parse_response(await response.text(), table)


asyncio.run(main())
