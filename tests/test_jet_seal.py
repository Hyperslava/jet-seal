"""Модульные тесты JetSeal: TC-01 … TC-32 и TC-37 (TEST_CASES.md).

Шаблон каждого теста: AAA (Arrange / Act / Assert).
ID тест-кейса указан в имени метода и в докстринге.
"""

import unittest

from jet_seal import (
    CrazyVehicleError,
    JetSeal,
    JetSealCannotDive,
    JetSealCannotFly,
    JetSealError,
    JetSealNoFins,
    JetSealNoStrength,
    JetSealTooDeep,
)
from tests.helpers import make_swimming_seal, snapshot

# Специальные значения float: NaN, +inf, -inf (SPEC 3.5)
NON_FINITE = (float("nan"), float("inf"), float("-inf"))


def new_seal(energy=100.0, fin_length_m=1.2, max_speed_kmh=40.0):
    """Тюлень на берегу со стандартными параметрами."""
    return JetSeal("Плюх", 300, fin_length_m, max_speed_kmh, energy=energy)


# Конструктор (SPEC 3.2, 3.3)
class TestConstructor(unittest.TestCase):

    def test_TC_01_empty_name_raises_value_error(self):
        """TC-01: пустое имя -> ValueError."""
        # Act / Assert
        with self.assertRaisesRegex(ValueError, "name must not be empty"):
            JetSeal("", 300, 1.2, 40)

    def test_TC_02_non_positive_numeric_params_raise_value_error(self):
        """TC-02: mass_kg, fin_length_m, max_speed_kmh = 0 и -1 -> ValueError."""
        # Arrange
        base = {"mass_kg": 300, "fin_length_m": 1.2, "max_speed_kmh": 40}
        for param in base:
            for bad_value in (0, -1):
                with self.subTest(param=param, value=bad_value):
                    kwargs = dict(base, **{param: bad_value})
                    # Act / Assert
                    with self.assertRaisesRegex(
                        ValueError, f"{param} must be positive"
                    ):
                        JetSeal("Плюх", **kwargs)
        # NaN и бесконечности не допускаются (SPEC 3.5)
        for param in base:
            for bad_value in NON_FINITE:
                with self.subTest(param=param, value=bad_value):
                    kwargs = dict(base, **{param: bad_value})
                    # Act / Assert
                    with self.assertRaisesRegex(ValueError, f"{param} must be finite"):
                        JetSeal("Плюх", **kwargs)

    def test_TC_03_energy_out_of_range_raises_value_error(self):
        """TC-03: energy = -1 и 101 -> ValueError; NaN и ±inf -> ValueError."""
        for bad_energy in (-1, 101):
            with self.subTest(energy=bad_energy):
                # Act / Assert
                with self.assertRaisesRegex(
                    ValueError, "energy must be between 0 and 100"
                ):
                    JetSeal("Плюх", 300, 1.2, 40, energy=bad_energy)
        for bad_energy in NON_FINITE:
            with self.subTest(energy=bad_energy):
                # Act / Assert
                with self.assertRaisesRegex(ValueError, "energy must be finite"):
                    JetSeal("Плюх", 300, 1.2, 40, energy=bad_energy)

    def test_TC_04_invalid_types_raise_type_error(self):
        """TC-04: name=123; числовые параметры = "x", True, None -> TypeError."""
        # Arrange
        base = {"mass_kg": 300, "fin_length_m": 1.2, "max_speed_kmh": 40, "energy": 100}
        with self.subTest(param="name", value=123):
            # Act / Assert
            with self.assertRaisesRegex(TypeError, "invalid argument type"):
                JetSeal(123, **base)
        for param in base:
            # bool формально подкласс int, но числом не считается (SPEC 3.5)
            for bad_value in ("x", True, None):
                with self.subTest(param=param, value=bad_value):
                    kwargs = dict(base, **{param: bad_value})
                    # Act / Assert
                    with self.assertRaisesRegex(TypeError, "invalid argument type"):
                        JetSeal("Плюх", **kwargs)

    def test_TC_05_initial_state_and_max_depth(self):
        """TC-05: начальное состояние, energy по умолчанию, max_depth_m = 24."""
        # Act
        seal = JetSeal("a", 1, 1.2, 1)
        # Assert
        self.assertEqual(seal.energy, 100)
        self.assertEqual(seal.position_km, 0)
        self.assertFalse(seal.is_swimming)
        self.assertEqual(seal.depth_m, 0)
        self.assertTrue(seal.fins_intact)
        self.assertAlmostEqual(seal.max_depth_m, 24.0)


# move (SPEC 3.4.1)
class TestMove(unittest.TestCase):

    def test_TC_06_move_water(self):
        """TC-06: плавание 20 км при скорости 40 км/ч."""
        # Arrange
        seal = new_seal(energy=100, max_speed_kmh=40)
        # Act
        hours = seal.move(20, "water")
        # Assert
        self.assertAlmostEqual(hours, 0.5)
        self.assertAlmostEqual(seal.position_km, 20)
        self.assertAlmostEqual(seal.energy, 80)
        self.assertTrue(seal.is_swimming)

    def test_TC_07_move_ground(self):
        """TC-07: ползание 2 км по суше (скорость x0.1, расход x3)."""
        # Arrange
        seal = new_seal(energy=100, max_speed_kmh=40)
        # Act
        hours = seal.move(2, "ground")
        # Assert
        self.assertAlmostEqual(hours, 0.5)
        self.assertAlmostEqual(seal.energy, 94)
        self.assertFalse(seal.is_swimming)

    def test_TC_08_move_air_raises_cannot_fly(self):
        """TC-08: полёт запрещён; воздух проверяется раньше ласт."""
        for fins_damaged in (False, True):
            with self.subTest(fins_damaged=fins_damaged):
                # Arrange
                seal = new_seal()
                if fins_damaged:
                    seal.damage_fins()
                # Act / Assert
                with self.assertRaisesRegex(JetSealCannotFly, "jet seal cannot fly"):
                    seal.move(1, "air")

    def test_TC_09_invalid_arguments_keep_state(self):
        """TC-09: неверные аргументы move; порядок: тип -> значение; состояние не меняется."""
        # Arrange
        seal = new_seal()
        before = snapshot(seal)
        cases = [
            # (distance, terrain, исключение, regex сообщения)
            (0, "water", ValueError, "distance_km must be positive"),
            (-1, "air", ValueError, "distance_km must be positive"),  # не CannotFly
            (1, "lava", ValueError, "unknown terrain"),
            ("abc", "water", TypeError, "invalid argument type"),
            (True, "water", TypeError, "invalid argument type"),  # bool не число
            ("abc", "lava", TypeError, "invalid argument type"),  # тип раньше значения
            (1, 5, TypeError, "invalid argument type"),  # terrain не строка
            (float("nan"), "water", ValueError, "distance_km must be finite"),
            (float("inf"), "water", ValueError, "distance_km must be finite"),
        ]
        for distance, terrain, exc, pattern in cases:
            with self.subTest(distance=distance, terrain=terrain):
                # Act / Assert
                with self.assertRaisesRegex(exc, pattern):
                    seal.move(distance, terrain)
                self.assertEqual(snapshot(seal), before)

    def test_TC_10_not_enough_energy_keeps_state(self):
        """TC-10: нехватка энергии -> JetSealNoStrength (в сообщении 20 и 10), состояние не меняется."""
        # Arrange
        seal = new_seal(energy=10)
        # Act / Assert: целое значение допускается с .0 и без (SPEC 6.2)
        with self.assertRaisesRegex(
            JetSealNoStrength,
            r"not enough energy: required 20(\.0+)?, have 10(\.0+)?",
        ):
            seal.move(20, "water")
        self.assertAlmostEqual(seal.energy, 10)
        self.assertAlmostEqual(seal.position_km, 0)

    def test_TC_11_damaged_fins_raise_no_fins(self):
        """TC-11: ласты повреждены -> JetSealNoFins (вода, суша); ласты раньше энергии."""
        for energy in (100, 0):
            for terrain in ("water", "ground"):
                with self.subTest(energy=energy, terrain=terrain):
                    # Arrange
                    seal = new_seal(energy=energy)
                    seal.damage_fins()
                    before = snapshot(seal)
                    # Act / Assert
                    with self.assertRaisesRegex(JetSealNoFins, "fins are damaged"):
                        seal.move(1, terrain)
                    self.assertEqual(snapshot(seal), before)

    def test_TC_12_exact_energy_is_enough(self):
        """TC-12: энергии хватает ровно -> движение разрешено, energy = 0."""
        # Arrange
        seal = new_seal(energy=100, max_speed_kmh=40)
        # Act
        seal.move(100, "water")
        # Assert
        self.assertAlmostEqual(seal.energy, 0)
        self.assertAlmostEqual(seal.position_km, 100)

    def test_TC_13_water_keeps_depth_ground_resets_it(self):
        """TC-13: по воде глубина сохраняется, по суше сбрасывается в 0."""
        # Arrange
        seal = make_swimming_seal(energy=100)
        seal.dive(10)
        # Act / Assert: вода
        seal.move(1, "water")
        self.assertAlmostEqual(seal.depth_m, 10)
        # Act / Assert: суша
        seal.move(1, "ground")
        self.assertAlmostEqual(seal.depth_m, 0)


# dive (SPEC 3.4.2)
class TestDive(unittest.TestCase):

    def test_TC_14_dive_success(self):
        """TC-14: dive(10) -> depth = 10, energy = 95."""
        # Arrange
        seal = make_swimming_seal(energy=100, fin_length_m=1.2)
        # Act
        seal.dive(10)
        # Assert
        self.assertAlmostEqual(seal.depth_m, 10)
        self.assertAlmostEqual(seal.energy, 95)

    def test_TC_15_invalid_depth_argument(self):
        """TC-15: dive(0), dive(-5) -> ValueError; dive("5"), True, None -> TypeError."""
        factories = {"в воде": make_swimming_seal, "на берегу": new_seal}
        for place, factory in factories.items():
            for bad_depth in (0, -5):
                with self.subTest(place=place, depth=bad_depth):
                    # Arrange
                    seal = factory()
                    before = snapshot(seal)
                    # Act / Assert
                    with self.assertRaisesRegex(ValueError, "depth_m must be positive"):
                        seal.dive(bad_depth)
                    self.assertEqual(snapshot(seal), before)
        for bad_type in ("5", True, None):
            with self.subTest(depth=bad_type):
                # Arrange
                seal = make_swimming_seal()
                # Act / Assert
                with self.assertRaisesRegex(TypeError, "invalid argument type"):
                    seal.dive(bad_type)
        for bad_value in NON_FINITE:
            with self.subTest(depth=bad_value):
                # Arrange
                seal = make_swimming_seal()
                before = snapshot(seal)
                # Act / Assert
                with self.assertRaisesRegex(ValueError, "depth_m must be finite"):
                    seal.dive(bad_value)
                self.assertEqual(snapshot(seal), before)

    def test_TC_16_damaged_fins_raise_no_fins(self):
        """TC-16: dive при повреждённых ластах -> JetSealNoFins (раньше проверки поверхности)."""
        factories = {"в воде": make_swimming_seal, "на берегу": new_seal}
        for place, factory in factories.items():
            with self.subTest(place=place):
                # Arrange
                seal = factory()
                seal.damage_fins()
                before = snapshot(seal)
                # Act / Assert
                with self.assertRaisesRegex(JetSealNoFins, "fins are damaged"):
                    seal.dive(5)
                self.assertEqual(snapshot(seal), before)

    def test_TC_17_dive_only_from_water_surface(self):
        """TC-17: на берегу и на глубине 10 dive(5) -> JetSealCannotDive."""
        with self.subTest(case="на берегу"):
            # Arrange
            seal = new_seal()
            before = snapshot(seal)
            # Act / Assert
            with self.assertRaisesRegex(
                JetSealCannotDive, "can dive only from water surface"
            ):
                seal.dive(5)
            self.assertEqual(snapshot(seal), before)
        with self.subTest(case="в воде на глубине 10"):
            # Arrange
            seal = make_swimming_seal()
            seal.dive(10)
            before = snapshot(seal)
            # Act / Assert
            with self.assertRaisesRegex(
                JetSealCannotDive, "can dive only from water surface"
            ):
                seal.dive(5)
            self.assertEqual(snapshot(seal), before)

    def test_TC_18_too_deep_and_max_depth_boundary(self):
        """TC-18: fin=0.5 (max 10): dive(15) -> TooDeep; dive(10) успешно; TooDeep раньше NoStrength."""
        with self.subTest(case="глубже максимума, затем ровно максимум"):
            # Arrange
            seal = make_swimming_seal(energy=100, fin_length_m=0.5)
            # Act / Assert: глубже максимума
            with self.assertRaisesRegex(
                JetSealTooDeep, "depth exceeds maximum for fin length"
            ):
                seal.dive(15)
            self.assertAlmostEqual(seal.depth_m, 0)
            self.assertAlmostEqual(seal.energy, 100)
            # Act / Assert: ровно максимальная глубина допустима
            seal.dive(10)
            self.assertAlmostEqual(seal.depth_m, 10)
        with self.subTest(case="энергии мало: TooDeep, а не NoStrength"):
            # Arrange
            seal = make_swimming_seal(energy=2, fin_length_m=0.5)
            before = snapshot(seal)
            # Act / Assert
            with self.assertRaises(JetSealTooDeep):
                seal.dive(15)
            self.assertEqual(snapshot(seal), before)

    def test_TC_19_dive_energy_shortage_and_exact_boundary(self):
        """TC-19: energy = 2, dive(10) -> NoStrength; energy = 5, dive(10) -> успешно, energy = 0."""
        with self.subTest(case="энергии не хватает"):
            # Arrange
            seal = make_swimming_seal(energy=2)
            # Act / Assert: в сообщении требуемая (5) и доступная (2) энергия
            with self.assertRaisesRegex(
                JetSealNoStrength,
                r"not enough energy: required 5(\.0+)?, have 2(\.0+)?",
            ):
                seal.dive(10)
            self.assertAlmostEqual(seal.depth_m, 0)
            self.assertAlmostEqual(seal.energy, 2)
        with self.subTest(case="энергии хватает ровно"):
            # Arrange
            seal = make_swimming_seal(energy=5)
            # Act
            seal.dive(10)
            # Assert
            self.assertAlmostEqual(seal.depth_m, 10)
            self.assertAlmostEqual(seal.energy, 0)


# surface (SPEC 3.4.3)
class TestSurface(unittest.TestCase):

    def test_TC_20_surface_resets_depth_for_free(self):
        """TC-20: surface() сбрасывает depth в 0 без затрат; работает при повреждённых ластах и на суше."""
        with self.subTest(case="на глубине 10, дважды"):
            # Arrange
            seal = make_swimming_seal(energy=55)
            seal.dive(10)  # energy: 55 -> 50
            self.assertAlmostEqual(seal.energy, 50)
            # Act
            seal.surface()
            seal.surface()
            # Assert
            self.assertAlmostEqual(seal.depth_m, 0)
            self.assertAlmostEqual(seal.energy, 50)
        with self.subTest(case="ласты повреждены"):
            # Arrange
            seal = make_swimming_seal(energy=55)
            seal.dive(10)
            seal.damage_fins()
            # Act
            seal.surface()
            # Assert
            self.assertAlmostEqual(seal.depth_m, 0)
            self.assertAlmostEqual(seal.energy, 50)
        with self.subTest(case="на берегу"):
            # Arrange
            seal = new_seal()
            before = snapshot(seal)
            # Act
            seal.surface()
            # Assert
            self.assertEqual(snapshot(seal), before)


# can_overcome (SPEC 3.4.4)
class TestCanOvercome(unittest.TestCase):

    def test_TC_21_whirlpool(self):
        """TC-21: водоворот: True только в воде, при целых ластах строго длиннее 1.0 м."""

        def short_fins():
            return make_swimming_seal(fin_length_m=0.6)

        def on_shore():
            return new_seal(fin_length_m=1.2)

        def damaged_fins():
            seal = make_swimming_seal(fin_length_m=1.2)
            seal.damage_fins()
            return seal

        cases = [
            ("fin=1.2, в воде", lambda: make_swimming_seal(fin_length_m=1.2), True),
            ("fin=0.6, в воде", short_fins, False),
            ("на берегу", on_shore, False),
            ("ласты повреждены", damaged_fins, False),
            # граница: правило fin_length_m > 1.0 строгое
            ("fin=1.0 (граница)", lambda: make_swimming_seal(fin_length_m=1.0), False),
            ("fin=1.001", lambda: make_swimming_seal(fin_length_m=1.001), True),
        ]
        for title, factory, expected in cases:
            with self.subTest(case=title):
                # Arrange
                seal = factory()
                before = snapshot(seal)
                # Act
                result = seal.can_overcome("whirlpool")
                # Assert
                self.assertIs(result, expected)
                self.assertEqual(snapshot(seal), before)

    def test_TC_22_reef(self):
        """TC-22: риф: True только на глубине (depth > 0) при целых ластах."""
        for depth, damaged, expected in (
            (10, False, True),
            (0, False, False),
            (10, True, False),
        ):
            with self.subTest(depth=depth, fins_damaged=damaged):
                # Arrange
                seal = make_swimming_seal()
                if depth:
                    seal.dive(depth)
                if damaged:
                    seal.damage_fins()
                # Act / Assert
                self.assertIs(seal.can_overcome("reef"), expected)

    def test_TC_23_dam(self):
        """TC-23: дамба: True только на суше при целых ластах."""
        with self.subTest(case="на берегу"):
            self.assertIs(new_seal().can_overcome("dam"), True)
        with self.subTest(case="в воде"):
            self.assertIs(make_swimming_seal().can_overcome("dam"), False)
        with self.subTest(case="на берегу, ласты повреждены"):
            seal = new_seal()
            seal.damage_fins()
            self.assertIs(seal.can_overcome("dam"), False)

    def test_TC_24_invalid_obstacle(self):
        """TC-24: неизвестное препятствие -> ValueError; не строка -> TypeError."""
        # Arrange
        seal = new_seal()
        with self.subTest(obstacle="tree"):
            # Act / Assert
            with self.assertRaisesRegex(ValueError, "unknown obstacle"):
                seal.can_overcome("tree")
        with self.subTest(obstacle=42):
            with self.assertRaisesRegex(TypeError, "invalid argument type"):
                seal.can_overcome(42)


# calculate_energy (SPEC 3.4.5)
class TestCalculateEnergy(unittest.TestCase):

    def test_TC_25_values_and_no_state_change(self):
        """TC-25: расход воды = 10, суши = 30; энергия не меняется."""
        # Arrange
        seal = new_seal(energy=100)
        before = snapshot(seal)
        # Act
        water = seal.calculate_energy(10, "water")
        ground = seal.calculate_energy(10, "ground")
        # Assert
        self.assertAlmostEqual(water, 10)
        self.assertAlmostEqual(ground, 30)
        self.assertAlmostEqual(seal.energy, 100)
        self.assertEqual(snapshot(seal), before)

    def test_TC_26_errors_without_nofins_and_nostrength(self):
        """TC-26: исключения расчёта; NoFins и NoStrength не поднимаются."""
        # Arrange
        seal = new_seal(energy=1)
        seal.damage_fins()
        # Act / Assert
        with self.subTest(case="воздух"):
            with self.assertRaises(JetSealCannotFly):
                seal.calculate_energy(1, "air")
        with self.subTest(case="distance = 0"):
            with self.assertRaises(ValueError):
                seal.calculate_energy(0, "water")
        with self.subTest(case="неизвестный terrain"):
            with self.assertRaises(ValueError):
                seal.calculate_energy(1, "lava")
        with self.subTest(case="distance не число"):
            with self.assertRaises(TypeError):
                seal.calculate_energy("a", "water")
        with self.subTest(case="distance = NaN"):
            with self.assertRaises(ValueError):
                seal.calculate_energy(float("nan"), "water")
        with self.subTest(case="энергии не хватает, ласты повреждены"):
            self.assertAlmostEqual(seal.calculate_energy(100, "water"), 100)


# refuel (SPEC 3.4.6)
class TestRefuel(unittest.TestCase):

    def test_TC_27_refuel_adds_energy(self):
        """TC-27: energy 20, refuel(50) -> 70."""
        # Arrange
        seal = new_seal(energy=20)
        # Act
        seal.refuel(50)
        # Assert
        self.assertAlmostEqual(seal.energy, 70)

    def test_TC_28_refuel_is_capped_at_100(self):
        """TC-28: energy 50, refuel(1000) -> 100."""
        # Arrange
        seal = new_seal(energy=50)
        # Act
        seal.refuel(1000)
        # Assert
        self.assertAlmostEqual(seal.energy, 100)

    def test_TC_29_invalid_amount(self):
        """TC-29: refuel(0), (-5), NaN, ±inf -> ValueError; refuel(None), "5", True -> TypeError."""
        # Arrange
        seal = new_seal(energy=50)
        for bad_amount in (0, -5):
            with self.subTest(amount=bad_amount):
                # Act / Assert
                with self.assertRaisesRegex(ValueError, "amount must be positive"):
                    seal.refuel(bad_amount)
                self.assertAlmostEqual(seal.energy, 50)
        for bad_type in (None, "5", True):
            with self.subTest(amount=bad_type):
                with self.assertRaisesRegex(TypeError, "invalid argument type"):
                    seal.refuel(bad_type)
                self.assertAlmostEqual(seal.energy, 50)
        for bad_value in NON_FINITE:
            with self.subTest(amount=bad_value):
                with self.assertRaisesRegex(ValueError, "amount must be finite"):
                    seal.refuel(bad_value)
                self.assertAlmostEqual(seal.energy, 50)


# damage_fins / repair_fins (SPEC 3.4.7)
class TestFins(unittest.TestCase):

    def test_TC_30_damage_and_repair_fins(self):
        """TC-30: damage_fins -> False, repair_fins -> True; energy не меняется."""
        # Arrange
        seal = new_seal(energy=50)
        # Act / Assert
        seal.damage_fins()
        self.assertFalse(seal.fins_intact)
        seal.repair_fins()
        self.assertTrue(seal.fins_intact)
        self.assertAlmostEqual(seal.energy, 50)


# get_status (SPEC 3.4.8)
class TestStatus(unittest.TestCase):

    EXPECTED_KEYS = {
        "name",
        "energy",
        "position_km",
        "is_swimming",
        "depth_m",
        "fin_length_m",
        "fins_intact",
    }

    def test_TC_31_get_status_keys_and_values(self):
        """TC-31: get_status() -> 7 ключей, значения верны, словарь — независимый снимок."""
        # Arrange
        seal = JetSeal("Плюх", 300, 1.2, 40, energy=90)
        # Act
        status = seal.get_status()
        # Assert
        self.assertEqual(set(status), self.EXPECTED_KEYS)
        self.assertEqual(status["name"], "Плюх")
        self.assertAlmostEqual(status["energy"], 90)
        self.assertAlmostEqual(status["position_km"], 0)
        self.assertIs(status["is_swimming"], False)
        self.assertAlmostEqual(status["depth_m"], 0)
        self.assertAlmostEqual(status["fin_length_m"], 1.2)
        self.assertIs(status["fins_intact"], True)

        # Act: после движения
        seal.move(10, "water")
        status = seal.get_status()
        # Assert
        self.assertAlmostEqual(status["energy"], 80)
        self.assertAlmostEqual(status["position_km"], 10)
        self.assertIs(status["is_swimming"], True)

        # Снимок независим: изменение словаря не меняет тюленя
        status["energy"] = -1
        self.assertAlmostEqual(seal.energy, 80)
        self.assertAlmostEqual(seal.get_status()["energy"], 80)

        # Снимок независим: действия тюленя не меняют ранее полученный словарь
        old_status = seal.get_status()
        seal.move(5, "water")
        new_status = seal.get_status()
        self.assertIsNot(new_status, old_status)  # каждый вызов — новый словарь
        self.assertAlmostEqual(old_status["energy"], 80)
        self.assertAlmostEqual(old_status["position_km"], 10)
        self.assertAlmostEqual(new_status["energy"], 75)
        self.assertAlmostEqual(new_status["position_km"], 15)


# Иерархия исключений (SPEC 6.1)
class TestExceptionHierarchy(unittest.TestCase):

    def test_TC_32_exception_hierarchy(self):
        """TC-32: доменные исключения наследуются от JetSealError -> CrazyVehicleError."""
        for exc in (
            JetSealCannotFly,
            JetSealNoStrength,
            JetSealNoFins,
            JetSealTooDeep,
            JetSealCannotDive,
        ):
            with self.subTest(exception=exc.__name__):
                self.assertTrue(issubclass(exc, JetSealError))
        self.assertTrue(issubclass(JetSealError, CrazyVehicleError))
        self.assertTrue(issubclass(CrazyVehicleError, Exception))


# Атрибуты только для чтения (SPEC 3.3)
class TestReadOnlyAttributes(unittest.TestCase):

    # атрибут -> значение, которое пытаемся присвоить
    ATTRIBUTES = {
        "name": "Другое",
        "mass_kg": 1,
        "fin_length_m": 9.9,
        "max_speed_kmh": 1,
        "max_depth_m": 1,
        "energy": -100,
        "position_km": 999,
        "is_swimming": True,
        "depth_m": 5,
        "fins_intact": True,
    }

    def test_TC_37_attributes_are_read_only(self):
        """TC-37: присваивание любому публичному атрибуту -> AttributeError, состояние не меняется."""
        # Arrange
        seal = new_seal(energy=50)
        seal.damage_fins()  # чтобы fins_intact = True было «ремонтом без ремонта»
        before = {name: getattr(seal, name) for name in self.ATTRIBUTES}
        for name, new_value in self.ATTRIBUTES.items():
            with self.subTest(attribute=name):
                # Act / Assert
                with self.assertRaises(AttributeError):
                    setattr(seal, name, new_value)
                self.assertEqual(getattr(seal, name), before[name])


if __name__ == "__main__":
    unittest.main()
