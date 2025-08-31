ARCHETYPES = {
    'Warrior': {
        'str': (70, 100), 'sta': (60, 90), 'agi': (40, 70), 'dex': (40, 70), 'con': (60, 90),
        'int': (10, 40), 'wis': (30, 60), 'cha': (30, 60), 'hp': (80, 100), 'mana': (10, 30),
        'level': (5, 10), 'weapon_pwr': (10, 15), 'spell_pwr': (3, 7), 'block_pwr': (8, 12),
        'rem_hp': (0,0), 'rem_mana':(0,0), 'rem_sta':(0,0), 'Warrior':(0,0), 'Rogue':(0,0), 'Mage':(0,0), 'Cleric':(0,0),
        'is_blocking': (0,0), 'is_dodging': (0,0),
    },
    'Rogue': {
        'str': (40, 70), 'sta': (30, 50), 'agi': (70, 100), 'dex': (70, 100), 'con': (30, 50),
        'int': (20, 50), 'wis': (30, 60), 'cha': (40, 70), 'hp': (60, 80), 'mana': (10, 30),
        'level': (4, 9), 'weapon_pwr': (8, 13), 'spell_pwr': (2, 6), 'block_pwr': (6, 10),
        'rem_hp': (0,0), 'rem_mana':(0,0), 'rem_sta':(0,0), 'Warrior':(0,0), 'Rogue':(0,0), 'Mage':(0,0), 'Cleric':(0,0),
        'is_blocking': (0,0), 'is_dodging': (0,0),
    },
    'Mage': {
        'str': (10, 30), 'sta': (10, 40), 'agi': (20, 50), 'dex': (40, 70), 'con': (10, 40),
        'int': (80, 100), 'wis': (50, 80), 'cha': (30, 60), 'hp': (30, 60), 'mana': (80, 100),
        'level': (5, 10), 'weapon_pwr': (2, 6), 'spell_pwr': (10, 15), 'block_pwr': (3, 7),
        'rem_hp': (0,0), 'rem_mana':(0,0), 'rem_sta':(0,0), 'Warrior':(0,0), 'Rogue':(0,0), 'Mage':(0,0), 'Cleric':(0,0),
        'is_blocking': (0,0), 'is_dodging': (0,0),
    },
    'Cleric': {
        'str': (40, 70), 'sta': (40, 80), 'agi': (30, 60), 'dex': (40, 70), 'con': (40, 80),
        'int': (40, 70), 'wis': (70, 100), 'cha': (40, 70), 'hp': (60, 90), 'mana': (50, 80),
        'level': (5, 10), 'weapon_pwr': (5, 10), 'spell_pwr': (8, 14), 'block_pwr': (5, 10),
        'rem_hp': (0,0), 'rem_mana':(0,0), 'rem_sta':(0,0), 'Warrior':(0,0), 'Rogue':(0,0), 'Mage':(0,0), 'Cleric':(0,0),
        'is_blocking': (0,0), 'is_dodging': (0,0),
    }
}


def get_hero_class_name(hero: dict)->str:
    # Returns the hero class name based on one-hot encoded features
    for class_name in ARCHETYPES.keys():
        if hero.get(class_name, 0) == 1:
            return class_name