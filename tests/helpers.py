"""Вспомогательные функции для тестов JetSeal."""

from jet_seal import JetSeal


def make_swimming_seal(energy=100.0, fin_length_m=1.2, max_speed_kmh=40.0):
    """Возвращает тюленя, который уже в воде, на поверхности,
    с заданной энергией.

    По SPEC 3.2 новый тюлень стоит на берегу, а в воду он попадает только через
    move(..., "water"). Поэтому тюлень один раз проплывает 1 км
    (-1 ед. энергии),
    а недостающая энергия добавляется через refuel().
    Итог:
    energy == energy, depth_m == 0, is_swimming == True, position_km == 1.
    """
    start = min(100.0, energy + 1)
    seal = JetSeal("Тест", 100, fin_length_m, max_speed_kmh, energy=start)
    seal.move(1, "water")
    if seal.energy < energy:
        seal.refuel(energy - seal.energy)
    return seal


def snapshot(seal):
    """Снимок изменяемого состояния тюленя
    (для проверок «состояние не меняется»).
    """
    return (
        seal.energy,
        seal.position_km,
        seal.is_swimming,
        seal.depth_m,
        seal.fins_intact,
    )
