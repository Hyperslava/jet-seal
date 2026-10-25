"""Модель водного транспортного средства, описанного в ``SPEC.md``."""

from __future__ import annotations

import math
from typing import TypeAlias


Number: TypeAlias = int | float


class CrazyVehicleError(Exception):
    """Базовое исключение для ошибок необычных транспортных средств."""


class JetSealError(CrazyVehicleError):
    """Базовое исключение для предметных ошибок реактивного тюленя."""


class JetSealCannotFly(JetSealError):
    """Ошибка попытки реактивного тюленя переместиться по воздуху."""


class JetSealNoStrength(JetSealError):
    """Ошибка нехватки энергии у реактивного тюленя."""


class JetSealNoFins(JetSealError):
    """Ошибка попытки движения с повреждёнными ластами."""


class JetSealTooDeep(JetSealError):
    """Ошибка превышения максимальной глубины погружения."""


class JetSealCannotDive(JetSealError):
    """Ошибка попытки погружения не с поверхности воды."""


def _validate_number_type(value: object) -> None:
    """Отклонить значения, не являющиеся ``int`` или ``float``, включая bool."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("invalid argument type")


def _validate_finite(value: Number, parameter: str) -> None:
    """Проверить конечность числа после проверки его типа."""
    # Все целые числа конечны. Отдельная проверка float также предотвращает
    # OverflowError при передаче сколь угодно большого допустимого целого числа.
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"{parameter} must be finite")


def _validate_move_arguments(distance_km: object, terrain: object) -> None:
    """Проверить аргументы движения в установленном спецификацией порядке."""
    _validate_number_type(distance_km)
    if not isinstance(terrain, str):
        raise TypeError("invalid argument type")

    _validate_finite(distance_km, "distance_km")
    if distance_km <= 0:
        raise ValueError("distance_km must be positive")
    if terrain not in {"water", "ground", "air"}:
        raise ValueError("unknown terrain")


class JetSeal:
    """Одноместный тюлень, способный перемещаться по воде и суше."""

    def __init__(
        self,
        name: str,
        mass_kg: float,
        fin_length_m: float,
        max_speed_kmh: float,
        energy: float = 100.0,
    ) -> None:
        """Создать реактивного тюленя и проверить параметры конструктора."""
        if not isinstance(name, str):
            raise TypeError("invalid argument type")

        numeric_arguments = (
            (mass_kg, "mass_kg"),
            (fin_length_m, "fin_length_m"),
            (max_speed_kmh, "max_speed_kmh"),
            (energy, "energy"),
        )
        for value, _ in numeric_arguments:
            _validate_number_type(value)
        for value, parameter in numeric_arguments:
            _validate_finite(value, parameter)

        if not name:
            raise ValueError("name must not be empty")
        for value, parameter in numeric_arguments[:3]:
            if value <= 0:
                raise ValueError(f"{parameter} must be positive")
        if not 0 <= energy <= 100:
            raise ValueError("energy must be between 0 and 100")

        self._name = name
        self._mass_kg = float(mass_kg)
        self._fin_length_m = float(fin_length_m)
        self._max_speed_kmh = float(max_speed_kmh)
        self._max_depth_m = self._fin_length_m * 20
        self._energy = float(energy)
        self._position_km = 0.0
        self._is_swimming = False
        self._depth_m = 0.0
        self._fins_intact = True

    @property
    def name(self) -> str:
        """Вернуть имя тюленя."""
        return self._name

    @property
    def mass_kg(self) -> float:
        """Вернуть массу тюленя в килограммах."""
        return self._mass_kg

    @property
    def fin_length_m(self) -> float:
        """Вернуть длину ласт в метрах."""
        return self._fin_length_m

    @property
    def max_speed_kmh(self) -> float:
        """Вернуть максимальную скорость в воде в километрах в час."""
        return self._max_speed_kmh

    @property
    def max_depth_m(self) -> float:
        """Вернуть максимальную глубину погружения в метрах."""
        return self._max_depth_m

    @property
    def energy(self) -> float:
        """Вернуть текущий запас энергии."""
        return self._energy

    @property
    def position_km(self) -> float:
        """Вернуть общее пройденное расстояние в километрах."""
        return self._position_km

    @property
    def is_swimming(self) -> bool:
        """Вернуть признак нахождения тюленя в воде."""
        return self._is_swimming

    @property
    def depth_m(self) -> float:
        """Вернуть текущую глубину в метрах."""
        return self._depth_m

    @property
    def fins_intact(self) -> bool:
        """Вернуть признак целостности ласт."""
        return self._fins_intact

    def move(self, distance_km: float, terrain: str) -> float:
        """Переместиться по воде или суше и вернуть время пути в часах."""
        _validate_move_arguments(distance_km, terrain)
        if terrain == "air":
            raise JetSealCannotFly("jet seal cannot fly")
        if not self._fins_intact:
            raise JetSealNoFins("fins are damaged")

        required_energy = self.calculate_energy(distance_km, terrain)
        if required_energy > self._energy:
            raise JetSealNoStrength(
                "not enough energy: "
                f"required {required_energy}, have {self._energy}"
            )

        speed_kmh = self._max_speed_kmh
        if terrain == "ground":
            speed_kmh *= 0.1

        self._position_km += distance_km
        self._energy -= required_energy
        self._is_swimming = terrain == "water"
        if terrain == "ground":
            self._depth_m = 0.0
        return distance_km / speed_kmh

    def dive(self, depth_m: float) -> None:
        """Погрузиться с поверхности воды на заданную абсолютную глубину."""
        _validate_number_type(depth_m)
        _validate_finite(depth_m, "depth_m")
        if depth_m <= 0:
            raise ValueError("depth_m must be positive")
        if not self._fins_intact:
            raise JetSealNoFins("fins are damaged")
        if not self._is_swimming or self._depth_m != 0:
            raise JetSealCannotDive("can dive only from water surface")
        if depth_m > self._max_depth_m:
            raise JetSealTooDeep("depth exceeds maximum for fin length")

        required_energy = depth_m * 0.5
        if required_energy > self._energy:
            raise JetSealNoStrength(
                "not enough energy: "
                f"required {required_energy}, have {self._energy}"
            )

        self._depth_m = float(depth_m)
        self._energy -= required_energy

    def surface(self) -> None:
        """Вернуться на поверхность без затрат энергии."""
        self._depth_m = 0.0

    def can_overcome(self, obstacle: str) -> bool:
        """Вернуть возможность преодолеть препятствие в текущем состоянии."""
        if not isinstance(obstacle, str):
            raise TypeError("invalid argument type")
        if obstacle not in {"whirlpool", "reef", "dam"}:
            raise ValueError("unknown obstacle")
        if not self._fins_intact:
            return False
        if obstacle == "whirlpool":
            return self._is_swimming and self._fin_length_m > 1.0
        if obstacle == "reef":
            return self._depth_m > 0
        return not self._is_swimming

    def calculate_energy(self, distance_km: float, terrain: str) -> float:
        """Рассчитать расход энергии на движение без изменения состояния."""
        _validate_move_arguments(distance_km, terrain)
        if terrain == "air":
            raise JetSealCannotFly("jet seal cannot fly")
        multiplier = 1 if terrain == "water" else 3
        return float(distance_km * multiplier)

    def refuel(self, amount: float) -> None:
        """Пополнить запас энергии положительным значением, но не выше 100."""
        _validate_number_type(amount)
        _validate_finite(amount, "amount")
        if amount <= 0:
            raise ValueError("amount must be positive")
        self._energy = min(100.0, self._energy + amount)

    def damage_fins(self) -> None:
        """Отметить ласты как повреждённые."""
        self._fins_intact = False

    def repair_fins(self) -> None:
        """Отметить ласты как целые."""
        self._fins_intact = True

    def get_status(self) -> dict[str, str | float | bool]:
        """Вернуть новый словарь со снимком публичного изменяемого состояния."""
        return {
            "name": self._name,
            "energy": self._energy,
            "position_km": self._position_km,
            "is_swimming": self._is_swimming,
            "depth_m": self._depth_m,
            "fin_length_m": self._fin_length_m,
            "fins_intact": self._fins_intact,
        }


__all__ = [
    "CrazyVehicleError",
    "JetSeal",
    "JetSealCannotDive",
    "JetSealCannotFly",
    "JetSealError",
    "JetSealNoFins",
    "JetSealNoStrength",
    "JetSealTooDeep",
]
