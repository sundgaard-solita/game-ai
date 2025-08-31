from hero import Hero


class HeroState:
    def __init__(self, stats, rem_hp, rem_mana, cur_sta=None):
        self.str_ = stats.get('str', 0)
        self.sta = stats.get('sta', 1)
        self.agi = stats.get('agi', 0)
        self.dex = stats.get('dex', 0)
        self.int_ = stats.get('int', 0)
        self.wis = stats.get('wis', 0)
        self.cha = stats.get('cha', 0)
        self.max_hp = stats.get('hp', 1)
        self.max_mana = stats.get('mana', 1)
        self.max_sta = self.sta
        self.rem_hp = rem_hp
        self.rem_mana = rem_mana
        self.rem_sta = cur_sta if cur_sta is not None else self.sta

    @property
    def hp_ratio(self):
        return self.rem_hp / self.max_hp

    @property
    def mana_ratio(self):
        return self.rem_mana / self.max_mana

    @property
    def sta_ratio(self):
        return self.rem_sta / self.max_sta

    def spend_sta(self, amount):
        self.rem_sta = max(0, self.rem_sta - amount)

    def regen_sta(self, amount=5):
        self.rem_sta = min(self.max_sta, self.rem_sta + amount)


def clamp_resources(hero:Hero):
    hero.features['rem_hp'] = max(0, hero.features['rem_hp'])
    hero.features['rem_mana'] = max(0, hero.features['rem_mana'])
    hero.features['rem_sta'] = max(0, hero.features['rem_sta'])

def init_flags(hero):
    #hero.setdefault('is_blocking', False)
    #hero.setdefault('is_dodging', False)
    #hero.setdefault('is_casting ', False)
    #hero.setdefault('is_using_wand', False)
    #hero.setdefault('is_using_bow', False)
    #hero.setdefault('is_resting', False)
    #hero.setdefault('is_protected', False)
    #hero.setdefault('is_healing', False)
    #hero.setdefault('is_attacking', False)
    # Set default class based on one hot ecoded class
    #hero.setdefault('class', next((k for k, v in hero.items() if v == 1), 'Unknown'))
    a = 1