# Constants

EGG_GROUPS: set[str] = {
    "Amorphous", "Bug", "Dragon", "Fairy", "Field", "Flying", "Grass", "Human-Like",
    "Mineral", "Monster", "Water 1", "Water 2", "Water 3", "Ditto", "Undiscovered"
}


VGC_CHAMPS: set[str] = {
    "Salamence", "Empoleon", "Metagross", "Toxicroak", "Snorlax", "Ludicolo", 
    "Kyogre", "Groudon", "Dialga", "Hariyama", "Cresselia", "Thundurus", 
    "Gothitelle", "Terrakion", "Escavalier", "Conkeldurr", "Hydreigon", 
    "Garchomp", "Rotom-Wash", "Tyranitar", "Tornadus", "Latios", "Mamoswine", 
    "Heatran", "Amoonguss", "Mega Gyarados", "Talonflame", "Pachirisu", 
    "Gardevoir", "Mega Kangaskhan", "Therian Forme", "Primal Kyogre", 
    "Mega Rayquaza", "Mega Gengar", "Raichu", "Hitmontop", "Bronzong", 
    "Tapu Koko", "Tapu Fini", "Alolan Marowak", "Krookodile", "Whimsicott", 
    "Celesteela", "Mega Salamence", "Incineroar", "Gastrodon", "Kartana", 
    "Lunala", "Stakataka", "Zacian Crowned Sword", "Shadow Rider", "Rillaboom", 
    "Flutter Mane", "Iron Hands", "Urshifu Rapid Strike Style", "Chien-Pao"
}

MYTHICAL: set[int] = {
    151, 251, 385, 386, 489, 490, 491, 492, 493, 494, 647, 648, 649, 
    719, 720, 721, 801, 802, 803, 807, 808, 809, 893, 1025
}

PSEUDO_LEGENDARY: set[int] = {149, 248, 373, 376, 445, 635, 705, 784, 887, 998, 1018}

STARTER: list[tuple[int, int]] = [
    (1, 9), (25, 25), (133, 133), (152, 160), (252, 260), (387, 395), 
    (495, 503), (650, 658), (722, 730), (810, 818), (906, 914)
]

LEGENDARY: list[tuple[int, int]] = [
    (144, 146), (150, 150), (243, 245), (249, 250), (377, 384), (480, 488), 
    (638, 646), (716, 718), (772, 773), (785, 792), (800, 800), (888, 892), 
    (894, 898), (905, 905), (1001, 1004), (1007, 1008), (1014, 1017), 
    (1024, 1024)
]

FOSSIL: list[tuple[int, int]] = [
    (138, 142), (345, 348), (408, 411), (564, 567), (696, 699), (880, 883)
]

ULTRA_BEAST: list[tuple[int, int]] = [(793, 799), (803, 806)]

PARADOX_FORMS: list[tuple[int, int]] = [
    (984, 995), (1005, 1006), (1009, 1010), (1020, 1023)
]

GENERATION: list[tuple[int, int]] = [
    (1, 151), (152, 251), (252, 386), (387, 493), (494, 649),
    (650, 721), (722, 809), (810, 905), (906, 1025)
]
