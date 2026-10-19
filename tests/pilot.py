"""Капитан тюленя: обёртка, которая управляет JetSeal на доменном языке."""


class Pilot:
    """Эмулятор капитана.
    Скрывает вызовы методов JetSeal за доменными действиями."""

    def __init__(self, seal):
        self._seal = seal

    def ползти(self, distance_km):
        return self._seal.move(distance_km, "ground")

    def плыть(self, distance_km):
        return self._seal.move(distance_km, "water")

    def взлететь(self, distance_km=1):
        return self._seal.move(distance_km, "air")

    def нырнуть(self, depth_m):
        self._seal.dive(depth_m)

    def всплыть(self):
        self._seal.surface()

    def преодолеть(self, obstacle):
        return self._seal.can_overcome(obstacle)

    def заправиться(self, amount):
        self._seal.refuel(amount)

    def повредить_ласты(self):
        self._seal.damage_fins()

    def починить_ласты(self):
        self._seal.repair_fins()

    @property
    def состояние(self):
        return self._seal.get_status()
