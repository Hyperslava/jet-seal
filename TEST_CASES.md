# Test Case Specification

## Модульные тесты

| ID | Источник | Предусловие | Вход | Ожидание | Приоритет |
|---|---|---|---|---|---|
| TC-01 | SPEC 3.2 | — | name="" | ValueError | high |
| TC-02 | SPEC 3.2 | — | mass_kg, fin_length_m, max_speed_kmh по очереди = 0 и -1 (subTest) | ValueError | high |
| TC-03 | SPEC 3.2 | — | energy=-1; energy=101 | ValueError | high |
| TC-04 | SPEC 3.2 | — | name=123; mass_kg="x" | TypeError | medium |
| TC-05 | SPEC 3.2, 3.3 | fin=1.2 | JetSeal("a",1,1.2,1) | energy=100, position=0, is_swimming=False, depth=0, fins_intact=True, max_depth_m=24 | high |
| TC-06 | SPEC 3.4.1, 4.1 | energy=100, speed=40 | move(20,"water") | 0.5; position=20; energy=80; is_swimming=True | high |
| TC-07 | SPEC 3.4.1, 4.1 | energy=100, speed=40 | move(2,"ground") | 0.5; energy=94; is_swimming=False | high |
| TC-08 | SPEC 3.4.1 | — | move(1,"air") | JetSealCannotFly | high |
| TC-09 | SPEC 3.4.1, 5 | — | move(0,"water"); move(-1,"air"); move(1,"lava"); move("abc","water") | ValueError; ValueError; ValueError; TypeError; состояние не меняется | high |
| TC-10 | SPEC 3.4.1, 4.1 | energy=10 | move(20,"water") | JetSealNoStrength; energy=10; position=0 | high |
| TC-11 | SPEC 3.4.1 | damage_fins() | move(1,"water"); move(1,"ground") | JetSealNoFins в обоих случаях | high |
| TC-12 | SPEC 3.4.1, 5 | energy=100, speed=40 | move(100,"water") | energy=0; position=100 | high |
| TC-13 | SPEC 3.4.1 | depth=10 | move(1,"water"); move(1,"ground") | после воды depth=10; после суши depth=0 | medium |
| TC-14 | SPEC 3.4.2 | is_swimming, fin=1.2, energy=100 | dive(10) | depth=10; energy=95 | high |
| TC-15 | SPEC 3.4.2 | is_swimming | dive(0); dive(-5) | ValueError | medium |
| TC-16 | SPEC 3.4.2 | is_swimming, damage_fins() | dive(5) | JetSealNoFins | medium |
| TC-17 | SPEC 3.4.2 | на берегу; в воде на глубине 10 (subTest) | dive(5) | JetSealCannotDive | high |
| TC-18 | SPEC 3.4.2, 5 | is_swimming, fin=0.5 (max 10) | dive(15); dive(10) | JetSealTooDeep (состояние не меняется); затем успешно, depth=10 | high |
| TC-19 | SPEC 3.4.2 | is_swimming, energy=2 | dive(10) (нужно 5) | JetSealNoStrength; depth=0; energy=2 | medium |
| TC-20 | SPEC 3.4.3 | depth=10, energy=50 | surface() дважды | depth=0; energy=50 | medium |
| TC-21 | SPEC 3.4.4 | fin=1.2, is_swimming; fin=0.6; на берегу; damage_fins() (subTest) | can_overcome("whirlpool") | True; False; False; False | high |
| TC-22 | SPEC 3.4.4 | depth=10; depth=0 (subTest) | can_overcome("reef") | True; False | medium |
| TC-23 | SPEC 3.4.4 | на берегу; в воде (subTest) | can_overcome("dam") | True; False | medium |
| TC-24 | SPEC 3.4.4 | — | can_overcome("tree") | ValueError | medium |
| TC-25 | SPEC 3.4.5 | energy=100 | calculate_energy(10,"water"); calculate_energy(10,"ground") | 10; 30; energy=100 | high |
| TC-26 | SPEC 3.4.5 | energy=1, damage_fins() | calculate_energy(1,"air"); (0,"water"); (1,"lava"); ("a","water"); (100,"water") | CannotFly; ValueError; ValueError; TypeError; 100 (без NoFins и NoStrength) | medium |
| TC-27 | SPEC 3.4.6, 4.1 | energy=20 | refuel(50) | energy=70 | high |
| TC-28 | SPEC 3.4.6, 5 | energy=50 | refuel(1000) | energy=100 | high |
| TC-29 | SPEC 3.4.6 | — | refuel(0); refuel(-5) | ValueError | high |
| TC-30 | SPEC 3.4.7 | energy=50 | damage_fins(); repair_fins() | fins_intact False, затем True; energy=50 | medium |
| TC-31 | SPEC 3.4.8 | — | get_status() | 7 ключей: name, energy, position_km, is_swimming, depth_m, fin_length_m, fins_intact; значения верны | medium |
| TC-32 | SPEC 6.1 | — | issubclass(...) | CannotFly, NoStrength, NoFins, TooDeep, CannotDive ⊂ JetSealError ⊂ CrazyVehicleError | high |

## Сценарные тесты

| ID | Источник | Вход | Ожидание | Приоритет |
|---|---|---|---|---|
| TC-33 | SPEC 4.2 | Сценарий «Шторм у Рифа Трёх Братьев», все шаги | position=45, energy=90, is_swimming=True, depth=0 | high |
| TC-34 | SPEC 4.2 | Сценарий «Побег из пересохшей лагуны», все шаги | position=12, energy=15, is_swimming=False, depth=0, fins_intact=True | high |
| TC-35 | SPEC 4.2 | Сценарий «Контрабанда через дамбу», все шаги | position=41, energy=90, is_swimming=True, depth=0, fins_intact=True | high |
| TC-36 | SPEC 4.2 | Сценарий «Выход на берег с глубины», все шаги | position=13, energy=32, is_swimming=False, depth=0 | medium |