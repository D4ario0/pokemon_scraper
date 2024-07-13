# Pokemon Scraper

This is a small scraper script to fetch data from over ~1000 urls for every pokemon (including alternative forms) up until Generation 9's _The Hidden Treasure of Area Zero_. 
This project was powered by `aiohttp` for asynchronous http requests and `selectolax` for lightning-fast html parsing.

Despite existing resources like PokeAPI my goal was to generate a file in `.json` format for providing a speedy solution for tiny/small/medium size apps requiring information of every pokemon specie.

# Data
The data is optimized to be quickly diggested by any json api like `JavaScript`'s `JSON.parse` or quickly setup a `TinyDB` database in `Python`.
The output will contain a list of pyhton "dictionaries" (json-like objects) with the following `keys`:

  | key | datatype |
  | --- | --- |
  | "id" | str
  | "dexNumber | int 
  | "name" | str
  | "types" | arr[str]
  | "height" | float
  | "weight | float 
  | "abilities" | arr[str]
  | "hidden_ability" | str
  | "EV_yield" | str
  | "catch_rate" | int 
  | "base_friendship" | int
  | "base_exp" | int
  | "egg_groups" | arr[str]
  | "egg_cycles" | int 
  | "HP" | int 
  | "ATA" | int 
  | "DEF" | int 
  | "SPA" | int 
  | "SPD" | int 
  | "SPE" | int 
  | "BST" | int
  | "tags" | arr[str] 

# Usage
1. Clone the repo.
2. Execute `pip install -r requirements.txt --no-index` in your terminal
3. Run scraper.py
4. Verify `pokemonDB.json` is created (~932 KB)

# Credit
Special thanks to the team/admin behind [pokemondb.net](https://pokemondb.net/) where most of the information is taken from

> [!CAUTION]
> I strongly suggest to read https://pokemondb.net/robots.txt before attempting to scrape the website
