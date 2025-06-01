class HeroState:
    def __init__(self, stats, cur_hp, cur_mana, cur_sta=None):
        self.str_ = stats.get('str', 0)
        self.sta = stats.get('sta', 1)
        self.agi = stats.get('agi', 0)
        self.dex = stats.get('dex', 0)
        self.int_ = stats.get('int', 0)
        self.wis = stats.get('wis', 0)
        self.cha = stats.get('cha', 0)
        self.max_hp = stats.get('HP', 1)
        self.max_mana = stats.get('Mana', 1)
        self.max_sta = self.sta
        self.cur_hp = cur_hp
        self.cur_mana = cur_mana
        self.cur_sta = cur_sta if cur_sta is not None else self.sta

    @property
    def hp_ratio(self):
        return self.cur_hp / self.max_hp

    @property
    def mana_ratio(self):
        return self.cur_mana / self.max_mana

    @property
    def sta_ratio(self):
        return self.cur_sta / self.max_sta

    def spend_sta(self, amount):
        self.cur_sta = max(0, self.cur_sta - amount)

    def regen_sta(self, amount=5):
        self.cur_sta = min(self.max_sta, self.cur_sta + amount)


def clamp_resources(hero):
    hero['cur_hp'] = max(0, hero['cur_hp'])
    hero['cur_mana'] = max(0, hero['cur_mana'])
    hero['cur_sta'] = min(hero['features'].get('sta', 1), max(0, hero.get('cur_sta', 0)))

def init_flags(hero):
    hero.setdefault('is_blocking', False)
    hero.setdefault('is_dodging', False)
    hero.setdefault('cur_sta', hero['features'].get('sta', 1))
