# Установка RF4S

Пошаговая инструкция по установке и первому запуску.

---

## Шаг 1. Установите Python 3.12

Скачайте установщик: **[Python 3.12.10 (64-bit)][download]**

При установке обязательно отметьте:
- **Use admin privileges when installing py.exe**
- **Add python.exe to PATH**

Затем нажмите **Install Now**.

![setup][setup]

> [!IMPORTANT]
> Python 3.13+ не поддерживается. Используйте версии **3.10**, **3.11** или **3.12**.

---

## Шаг 2. Скачайте исходный код

Скачайте архив: **[RussianFishing4Script-main.zip][github]**

---

## Шаг 3. Распакуйте архив

Распакуйте `RussianFishing4Script-main.zip` в удобную папку.

> [!WARNING]
> Путь к папке **не должен** содержать кириллицу и другие неанглийские символы.

![unzip][unzip]

---

## Шаг 4. Скопируйте путь к папке

Откройте распакованную папку и скопируйте полный путь из адресной строки проводника.

![path][path]

---

## Шаг 5. Откройте командную строку

Нажмите `Win + R`, введите `cmd` и нажмите Enter.

![cmd][cmd]

---

## Шаг 6. Перейдите в папку проекта

Введите `cd` и вставьте скопированный путь:
```
cd C:\Users\derek\tmp\RussianFishing4Script-main
```

![cd][cd]

---

## Шаг 7. Установите зависимости

Выполните эту команду один раз:
```
pip install -r requirements.txt
```

![pip][pip]

> [!TIP]
> Рекомендуется использовать виртуальное окружение (`venv`), но этот шаг пропущен для простоты.

---

## Шаг 8. Запустите бота

```
python main.py
```

При первом запуске скрипт задаст два вопроса:
1. **Язык игры** — выберите `1` (English) или `2` (Русский)
2. **ClickLock** — включена ли фиксация щелчка мыши в Windows

Ваши ответы сохранятся в файле `config.yaml`. Позже можно изменить язык, отредактировав параметр `LANGUAGE` в этом файле:
```yaml
LANGUAGE: "ru"   # Русский интерфейс
LANGUAGE: "en"   # Английский интерфейс
```

![run][run]

> [!IMPORTANT]
> При каждом новом открытии командной строки не забывайте сначала перейти в папку проекта:
> ```
> cd C:\Users\derek\tmp\RussianFishing4Script-main
> python main.py
> ```

---

## Альтернатива: установка через uv

[uv](https://docs.astral.sh/uv/) — более быстрая альтернатива pip.

```
git clone https://github.com/dereklee0310/RussianFishing4Script.git
cd RussianFishing4Script
uv sync
uv run main.py
```

[download]: https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe
[setup]: /static/readme/setup.png
[unzip]: /static/readme/unzip.png
[path]: /static/readme/path.png
[cmd]: /static/readme/cmd.png
[cd]: /static/readme/cd.png
[pip]: /static/readme/pip.png
[run]: /static/readme/run.png
[github]: https://github.com/dereklee0310/RussianFishing4Script/archive/refs/heads/main.zip
