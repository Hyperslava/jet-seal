"""Сценарные тесты JetSeal: TC-33 … TC-36 (TEST_CASES.md, SPEC 4.2).

Шаблон каждого теста: Given / When / Then. Тюленем управляет Pilot.
"""

import unittest

from jet_seal import (
    JetSeal,
    JetSealCannotDive,
    JetSealCannotFly,
    JetSealNoFins,
    JetSealNoStrength,
    JetSealTooDeep,
)
from tests.pilot import Pilot


class TestStormAtReef(unittest.TestCase):

    def test_TC_33_storm_at_three_brothers_reef(self):
        """TC-33: сценарий «Шторм у Рифа Трёх Братьев»."""
        # Given
        seal = JetSeal("Плюх", 300, 1.2, 40, energy=90)
        pilot = Pilot(seal)

        # When: ползёт к воде на 5 км
        hours = pilot.ползти(5)
        # Then
        self.assertAlmostEqual(hours, 1.25)
        self.assertAlmostEqual(seal.energy, 75)
        self.assertFalse(seal.is_swimming)

        # When: плывёт 20 км
        pilot.плыть(20)
        # Then
        self.assertAlmostEqual(seal.energy, 55)
        self.assertAlmostEqual(seal.position_km, 25)
        self.assertTrue(seal.is_swimming)

        # When: водоворот
        # Then
        self.assertTrue(pilot.преодолеть("whirlpool"))
        self.assertAlmostEqual(seal.energy, 55)

        # When: ныряет на 10 м
        pilot.нырнуть(10)
        # Then
        self.assertAlmostEqual(seal.energy, 50)
        self.assertAlmostEqual(seal.depth_m, 10)

        # When: проходит под рифом
        # Then
        self.assertTrue(pilot.преодолеть("reef"))

        # When: ныряет ещё раз, не всплывая
        # Then
        with self.assertRaises(JetSealCannotDive):
            pilot.нырнуть(5)
        self.assertAlmostEqual(seal.energy, 50)

        # When: всплывает и плывёт 10 км
        pilot.всплыть()
        pilot.плыть(10)
        # Then
        self.assertAlmostEqual(seal.depth_m, 0)
        self.assertAlmostEqual(seal.energy, 40)
        self.assertAlmostEqual(seal.position_km, 35)

        # When: пытается взлететь
        # Then
        with self.assertRaises(JetSealCannotFly):
            pilot.взлететь()
        self.assertAlmostEqual(seal.position_km, 35)

        # When: пытается проплыть 50 км
        # Then
        with self.assertRaises(JetSealNoStrength):
            pilot.плыть(50)
        self.assertAlmostEqual(seal.energy, 40)

        # When: заправляется на 70
        pilot.заправиться(70)
        # Then
        self.assertAlmostEqual(seal.energy, 100)

        # When: плывёт ещё 10 км
        pilot.плыть(10)
        # Then: итоговое состояние
        self.assertAlmostEqual(seal.position_km, 45)
        self.assertAlmostEqual(seal.energy, 90)
        self.assertTrue(seal.is_swimming)
        self.assertAlmostEqual(seal.depth_m, 0)


class TestLagoonEscape(unittest.TestCase):

    def test_TC_34_escape_from_dried_lagoon(self):
        """TC-34: сценарий «Побег из пересохшей лагуны»."""
        # Given
        seal = JetSeal("Бульк", 120, 0.6, 20, energy=30)
        pilot = Pilot(seal)

        # When: плывёт 4 км
        hours = pilot.плыть(4)
        # Then
        self.assertAlmostEqual(hours, 0.2)
        self.assertAlmostEqual(seal.energy, 26)

        # When: пытается пройти водоворот
        # Then: ласты короче 1.0 м
        self.assertFalse(pilot.преодолеть("whirlpool"))

        # When: ныряет на 8 м
        pilot.нырнуть(8)
        # Then
        self.assertAlmostEqual(seal.energy, 22)

        # When: всплывает и пытается нырнуть на 15 м (максимум 12 м)
        pilot.всплыть()
        # Then
        with self.assertRaises(JetSealTooDeep):
            pilot.нырнуть(15)
        self.assertAlmostEqual(seal.energy, 22)

        # When: ласты повреждаются, капитан пытается плыть и ползти
        pilot.повредить_ласты()
        # Then
        with self.assertRaises(JetSealNoFins):
            pilot.плыть(1)
        with self.assertRaises(JetSealNoFins):
            pilot.ползти(1)
        self.assertAlmostEqual(seal.position_km, 4)

        # When: ласты чинят и капитан плывёт 1 км
        pilot.починить_ласты()
        pilot.плыть(1)
        # Then
        self.assertAlmostEqual(seal.energy, 21)
        self.assertAlmostEqual(seal.position_km, 5)

        # When: ползёт по суше 3 км
        hours = pilot.ползти(3)
        # Then
        self.assertAlmostEqual(hours, 1.5)
        self.assertAlmostEqual(seal.energy, 12)
        self.assertFalse(seal.is_swimming)

        # When: проходит дамбу
        # Then
        self.assertTrue(pilot.преодолеть("dam"))

        # When: ползёт ещё 4 км (энергии хватает ровно)
        pilot.ползти(4)
        # Then
        self.assertAlmostEqual(seal.energy, 0)
        self.assertAlmostEqual(seal.position_km, 12)

        # When: пытается плыть 1 км
        # Then
        with self.assertRaises(JetSealNoStrength):
            pilot.плыть(1)

        # When: заправляется на 15
        pilot.заправиться(15)
        # Then: итоговое состояние
        self.assertAlmostEqual(seal.position_km, 12)
        self.assertAlmostEqual(seal.energy, 15)
        self.assertFalse(seal.is_swimming)
        self.assertAlmostEqual(seal.depth_m, 0)
        self.assertTrue(seal.fins_intact)


class TestSmugglingThroughDam(unittest.TestCase):

    def test_TC_35_smuggling_through_dam(self):
        """TC-35: сценарий «Контрабанда через дамбу»."""
        # Given
        seal = JetSeal("Шлёп", 200, 1.5, 30, energy=50)
        pilot = Pilot(seal)

        # When: плывёт 10 км
        hours = pilot.плыть(10)
        # Then
        self.assertAlmostEqual(hours, 10 / 30)
        self.assertAlmostEqual(seal.energy, 40)
        self.assertAlmostEqual(seal.position_km, 10)
        self.assertTrue(seal.is_swimming)

        # When: водоворот
        # Then: энергию не тратит
        self.assertTrue(pilot.преодолеть("whirlpool"))
        self.assertAlmostEqual(seal.energy, 40)

        # When: ныряет ровно на максимальную глубину (1.5 * 20 = 30 м)
        pilot.нырнуть(30)
        # Then
        self.assertAlmostEqual(seal.energy, 25)
        self.assertAlmostEqual(seal.depth_m, 30)
        self.assertTrue(pilot.преодолеть("reef"))

        # When: всплывает и пытается нырнуть на 31 м
        pilot.всплыть()
        # Then
        with self.assertRaises(JetSealTooDeep):
            pilot.нырнуть(31)
        self.assertAlmostEqual(seal.depth_m, 0)
        self.assertAlmostEqual(seal.energy, 25)

        # When: ползёт по суше 2 км
        hours = pilot.ползти(2)
        # Then
        self.assertAlmostEqual(hours, 2 / 3)
        self.assertAlmostEqual(seal.energy, 19)
        self.assertAlmostEqual(seal.position_km, 12)
        self.assertFalse(seal.is_swimming)
        self.assertTrue(pilot.преодолеть("dam"))

        # When: плывёт на всю оставшуюся энергию (19 км)
        pilot.плыть(19)
        # Then
        self.assertAlmostEqual(seal.energy, 0)
        self.assertAlmostEqual(seal.position_km, 31)
        self.assertTrue(seal.is_swimming)
        self.assertFalse(pilot.преодолеть("dam"))

        # When: энергии нет, пытается плыть и ползти
        # Then: состояние не меняется
        with self.assertRaises(JetSealNoStrength):
            pilot.плыть(1)
        with self.assertRaises(JetSealNoStrength):
            pilot.ползти(1)
        self.assertAlmostEqual(seal.position_km, 31)
        self.assertTrue(seal.is_swimming)

        # When: заправляется на 100 и плывёт 10 км
        pilot.заправиться(100)
        self.assertAlmostEqual(seal.energy, 100)
        pilot.плыть(10)
        # Then: итоговое состояние
        self.assertAlmostEqual(seal.position_km, 41)
        self.assertAlmostEqual(seal.energy, 90)
        self.assertTrue(seal.is_swimming)
        self.assertAlmostEqual(seal.depth_m, 0)
        self.assertTrue(pilot.состояние["fins_intact"])


class TestShoreFromDepth(unittest.TestCase):

    def test_TC_36_leaving_water_from_depth(self):
        """TC-36: сценарий «Выход на берег с глубины»."""
        # Given
        seal = JetSeal("Хрюндель", 250, 1.1, 20, energy=70)
        pilot = Pilot(seal)

        # When: плывёт 5 км и ныряет на 20 м
        pilot.плыть(5)
        pilot.нырнуть(20)
        # Then
        self.assertAlmostEqual(seal.energy, 55)
        self.assertAlmostEqual(seal.depth_m, 20)
        self.assertAlmostEqual(seal.position_km, 5)

        # When: пытается пройти дамбу
        # Then: тюлень в воде
        self.assertFalse(pilot.преодолеть("dam"))

        # When: выходит на берег, проползая 4 км
        hours = pilot.ползти(4)
        # Then
        self.assertAlmostEqual(hours, 2.0)
        self.assertAlmostEqual(seal.energy, 43)
        self.assertAlmostEqual(seal.depth_m, 0)
        self.assertFalse(seal.is_swimming)
        self.assertAlmostEqual(seal.position_km, 9)

        # When: пытается пройти дамбу
        # Then
        self.assertTrue(pilot.преодолеть("dam"))

        # When: возвращается в воду, проплывая 3 км
        pilot.плыть(3)
        # Then
        self.assertAlmostEqual(seal.energy, 40)
        self.assertTrue(seal.is_swimming)
        self.assertAlmostEqual(seal.position_km, 12)

        # When: ныряет на 10 м
        pilot.нырнуть(10)
        # Then
        self.assertAlmostEqual(seal.energy, 35)
        self.assertAlmostEqual(seal.depth_m, 10)

        # When: пытается пройти дамбу
        # Then
        self.assertFalse(pilot.преодолеть("dam"))

        # When: проползает 1 км
        hours = pilot.ползти(1)
        # Then: итоговое состояние
        self.assertAlmostEqual(hours, 0.5)
        self.assertAlmostEqual(seal.energy, 32)
        self.assertAlmostEqual(seal.depth_m, 0)
        self.assertAlmostEqual(seal.position_km, 13)
        self.assertFalse(seal.is_swimming)


if __name__ == "__main__":
    unittest.main()
