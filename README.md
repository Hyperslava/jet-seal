# Jet Seal
Автор: Ермолинская Юлия Олеговна (№6)  
Разработчик: Сорокин Святослав Алексеевич (№20)  
Реализация реактивного тюленя по требованиям из `SPEC.md`.

## Запуск тестов

Требуется Python 3.10 или новее. Дополнительные зависимости не нужны.
Из корня репозитория выполните:

```bash
python -m unittest discover -s tests -t . -v
```

Запуск отдельного тестового модуля:

```bash
python -m unittest tests.test_scenarios -v
python -m unittest tests.test_jet_seal -v
```
