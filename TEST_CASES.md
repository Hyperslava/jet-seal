# Test Case Specification

ТЗ: `SPEC.md` v0.2. 
Тип: 
`module` — модульный тест (AAA), 
`scenario` — сценарный тест (GWT, через Pilot).
Если во входе или предусловии указано «(subTest)», в тесте несколько входов, каждый проверяется отдельным `subTest`.
NaN и ±inf обозначают `float("nan")`, `float("inf")`, `float("-inf")`.

| ID | Тип | Источник | Предусловие | Вход | Ожидание | Приоритет |
|---|---|---|---|---|---|---|
| TC-01 | module | SPEC 3.2, 6.2 | — | name="" | ValueError "name must not be empty" | high |
| TC-02 | module | SPEC 3.2, 3.5, 6.2 | — | mass_kg, fin_length_m, max_speed_kmh по очереди = 0 и -1; затем = NaN, +inf, -inf (subTest) | ValueError "<параметр> must be positive" для 0 и -1; ValueError "<параметр> must be finite" для NaN и ±inf | high |
| TC-03 | module | SPEC 3.2, 3.5, 6.2 | — | energy=-1; energy=101; energy=NaN, +inf, -inf | ValueError "energy must be between 0 and 100"; ValueError "energy must be finite" | high |
| TC-04 | module | SPEC 3.2, 3.5, 6.2 | — | name=123; mass_kg, fin_length_m, max_speed_kmh, energy по очереди = "x", True, None (subTest) | TypeError "invalid argument type" | medium |
| TC-05 | module | SPEC 3.2, 3.3 | fin=1.2 | JetSeal("a",1,1.2,1) | energy=100, position=0, is_swimming=False, depth=0, fins_intact=True, max_depth_m=24 | high |
| TC-06 | module | SPEC 3.4.1, 4.1 | energy=100, speed=40 | move(20,"water") | 0.5; position=20; energy=80; is_swimming=True | high |
| TC-07 | module | SPEC 3.4.1, 4.1 | energy=100, speed=40 | move(2,"ground") | 0.5; energy=94; is_swimming=False | high |
| TC-08 | module | SPEC 3.4.1, 3.5, 6.2 | ласты целы; damage_fins() (subTest) | move(1,"air") | JetSealCannotFly "jet seal cannot fly" в обоих случаях (воздух проверяется раньше ласт) | high |
| TC-09 | module | SPEC 3.4.1, 3.5, 5, 6.2 | — | move(0,"water"); move(-1,"air"); move(1,"lava"); move("abc","water"); move(True,"water"); move("abc","lava"); move(1,5); move(NaN,"water"); move(+inf,"water") | ValueError "distance_km must be positive"; ValueError (не CannotFly); ValueError "unknown terrain"; TypeError ×4 "invalid argument type" (тип проверяется раньше значения); ValueError "distance_km must be finite" ×2; состояние не меняется | high |
| TC-10 | module | SPEC 3.4.1, 4.1, 6.2 | energy=10 | move(20,"water") | JetSealNoStrength "not enough energy: required 20, have 10" (целые допускаются с .0 и без); energy=10; position=0 | high |
| TC-11 | module | SPEC 3.4.1, 3.5, 6.2 | damage_fins(); energy=100 и energy=0 (subTest) | move(1,"water"); move(1,"ground") | JetSealNoFins "fins are damaged" во всех случаях (ласты проверяются раньше энергии); состояние не меняется | high |
| TC-12 | module | SPEC 3.4.1, 5 | energy=100, speed=40 | move(100,"water") | energy=0; position=100 | high |
| TC-13 | module | SPEC 3.4.1 | depth=10 | move(1,"water"); move(1,"ground") | после воды depth=10; после суши depth=0 | medium |
| TC-14 | module | SPEC 3.4.2 | is_swimming, fin=1.2, energy=100 | dive(10) | depth=10; energy=95 | high |
| TC-15 | module | SPEC 3.4.2, 3.5, 6.2 | в воде; на берегу (subTest) | dive(0); dive(-5); в воде также dive("5"); dive(True); dive(None); dive(NaN); dive(+inf); dive(-inf) | ValueError "depth_m must be positive" (в воде и на берегу); TypeError "invalid argument type"; ValueError "depth_m must be finite"; состояние не меняется | medium |
| TC-16 | module | SPEC 3.4.2, 3.5, 6.2 | в воде; на берегу; damage_fins() (subTest) | dive(5) | JetSealNoFins "fins are damaged" (ласты проверяются раньше поверхности); состояние не меняется | medium |
| TC-17 | module | SPEC 3.4.2, 3.5, 6.2 | на берегу; в воде на глубине 10 (subTest) | dive(5) | JetSealCannotDive "can dive only from water surface"; состояние не меняется | high |
| TC-18 | module | SPEC 3.4.2, 5, 6.2 | is_swimming, fin=0.5 (max 10), energy=100; is_swimming, fin=0.5, energy=2 (subTest) | dive(15); затем dive(10) при energy=100 | JetSealTooDeep "depth exceeds maximum for fin length" (состояние не меняется); затем успешно, depth=10; при energy=2 тоже TooDeep, а не NoStrength | high |
| TC-19 | module | SPEC 3.4.2, 5, 6.2 | is_swimming, energy=2; is_swimming, energy=5 (subTest) | dive(10) (нужно 5) | при energy=2: JetSealNoStrength "not enough energy: required 5, have 2" (целые допускаются с .0 и без), depth=0, energy=2; при energy=5: успешно, depth=10, energy=0 | high |
| TC-20 | module | SPEC 3.4.3 | в воде на глубине 10, energy=50; то же с damage_fins(); на берегу (subTest) | surface() (в первом случае дважды) | depth=0, energy не меняется, исключений нет; на берегу состояние не меняется | medium |
| TC-21 | module | SPEC 3.4.4, 5 | fin=1.2, is_swimming; fin=0.6; на берегу; damage_fins(); fin=1.0, is_swimming; fin=1.001, is_swimming (subTest) | can_overcome("whirlpool") | True; False; False; False; False (граница строгая: > 1.0); True; состояние не меняется | high |
| TC-22 | module | SPEC 3.4.4 | depth=10; depth=0; depth=10 и damage_fins() (subTest) | can_overcome("reef") | True; False; False | medium |
| TC-23 | module | SPEC 3.4.4 | на берегу; в воде; на берегу и damage_fins() (subTest) | can_overcome("dam") | True; False; False | medium |
| TC-24 | module | SPEC 3.4.4, 3.5, 6.2 | — | can_overcome("tree"); can_overcome(42) | ValueError "unknown obstacle"; TypeError "invalid argument type" | medium |
| TC-25 | module | SPEC 3.4.5 | energy=100 | calculate_energy(10,"water"); calculate_energy(10,"ground") | 10; 30; energy=100 | high |
| TC-26 | module | SPEC 3.4.5, 3.5 | energy=1, damage_fins() | calculate_energy(1,"air"); (0,"water"); (1,"lava"); ("a","water"); (NaN,"water"); (100,"water") | CannotFly; ValueError; ValueError; TypeError; ValueError; 100 (без NoFins и NoStrength) | medium |
| TC-27 | module | SPEC 3.4.6, 4.1 | energy=20 | refuel(50) | energy=70 | high |
| TC-28 | module | SPEC 3.4.6, 5 | energy=50 | refuel(1000) | energy=100 | high |
| TC-29 | module | SPEC 3.4.6, 3.5, 6.2 | energy=50 | refuel(0); refuel(-5); refuel(None); refuel("5"); refuel(True); refuel(NaN); refuel(+inf); refuel(-inf) | ValueError "amount must be positive" ×2; TypeError "invalid argument type" ×3; ValueError "amount must be finite" ×3; energy=50 | high |
| TC-30 | module | SPEC 3.4.7 | energy=50 | damage_fins(); repair_fins() | fins_intact False, затем True; energy=50 | medium |
| TC-31 | module | SPEC 3.4.8 | energy=90 | get_status(); затем move(10,"water") и снова get_status(); status["energy"]=-1; снимок до move(5,"water") и после | 7 ключей: name, energy, position_km, is_swimming, depth_m, fin_length_m, fins_intact; значения верны; словарь — независимый снимок: изменение словаря не меняет тюленя, а последующие действия не меняют ранее полученный словарь; каждый вызов возвращает новый словарь | medium |
| TC-32 | module | SPEC 6.1 | — | issubclass(...) | CannotFly, NoStrength, NoFins, TooDeep, CannotDive ⊂ JetSealError ⊂ CrazyVehicleError | high |
| TC-33 | scenario | SPEC 4.2 | — | Сценарий «Шторм у Рифа Трёх Братьев», все шаги | position=45, energy=90, is_swimming=True, depth=0 | high |
| TC-34 | scenario | SPEC 4.2 | — | Сценарий «Побег из пересохшей лагуны», все шаги | position=12, energy=15, is_swimming=False, depth=0, fins_intact=True | high |
| TC-35 | scenario | SPEC 4.2 | — | Сценарий «Контрабанда через дамбу», все шаги | position=41, energy=90, is_swimming=True, depth=0, fins_intact=True | high |
| TC-36 | scenario | SPEC 4.2 | — | Сценарий «Выход на берег с глубины», все шаги | position=13, energy=32, is_swimming=False, depth=0 | medium |
| TC-37 | module | SPEC 3.3 | energy=50, damage_fins(); (subTest по каждому из 10 атрибутов) | присваивание атрибуту: name, mass_kg, fin_length_m, max_speed_kmh, max_depth_m, energy, position_km, is_swimming, depth_m, fins_intact | AttributeError; значение атрибута не меняется | high |

Итого: 33 модульных и 4 сценарных тест-кейса (ID TC-37 добавлен после ревью; сценарные TC-33…TC-36 сохранили номера).