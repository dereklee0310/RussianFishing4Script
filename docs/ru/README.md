**[[English version]][readme_en]** **[[中文版]][readme_zh-TW]**
<div align="center">

![RF4S][rf4s_logo]
<h1 align="center">RF4S: Скрипт для Russian Fishing 4</h1>

**Автоматический бот для Russian Fishing 4 с поддержкой спиннинга, донной, морской и поплавочной ловли.**

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://opensource.org/license/gpl-3-0)
[![Discord](https://img.shields.io/badge/discord-join-rf44.svg?labelColor=191937&color=6F6FF7&logo=discord)](https://discord.gg/BZQWQnAMbY)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat)](http://makeapullrequest.com)
[![Python: 3.10 | 3.11 | 3.12](https://img.shields.io/badge/python-3.10_%7C_3.11_%7C_3.12-blue)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

</div>

> [!TIP]
> Присоединяйтесь к нашему [серверу Discord][discord], чтобы предлагать идеи, сообщать об ошибках или получить помощь.

---

## Установка

> [!WARNING]
> 1. Путь к папке проекта **не должен** содержать кириллицу и другие неанглийские символы.
> 2. Исполняемый файл (.exe) может вызывать ложные срабатывания антивируса. Рекомендуем запускать через Python. Подробнее: **[INSTALLATION][installation]**.

### Исполняемый файл (.exe)
Скачайте `rf4s.zip` из раздела [Releases][releases] и распакуйте.

### pip
```
git clone https://github.com/dereklee0310/RussianFishing4Script.git
cd RussianFishing4Script
pip install -r requirements.txt
```

### uv
```
git clone https://github.com/dereklee0310/RussianFishing4Script.git
cd RussianFishing4Script
uv sync
```

> [!IMPORTANT]
> Python 3.13+ не поддерживается. Используйте версии **3.10**, **3.11** или **3.12**.

---

## Язык интерфейса

RF4S поддерживает два языка интерфейса: **английский** (`en`) и **русский** (`ru`). Интерфейс скрипта (меню, логи, результаты, уведомления) отображается на выбранном языке.

### Первый запуск
При первом запуске скрипт спросит язык игры. Ваш выбор сохранится в `config.yaml`:
```
What's your game language? [(1) en (2) ru (3) q (quit)]
>>> 2
```

### Изменение языка
Откройте файл `config.yaml` в корне проекта и измените параметр `LANGUAGE`:
```yaml
# Английский интерфейс
LANGUAGE: "en"

# Русский интерфейс
LANGUAGE: "ru"
```
Сохраните файл и перезапустите скрипт — изменения вступят в силу.

### Переключение через командную строку (одноразово)
Если нужно запустить с другим языком без редактирования конфига:
```
python main.py LANGUAGE "ru"
```
```
.\main.exe LANGUAGE "en"
```

> [!IMPORTANT]
> Параметр `LANGUAGE` влияет одновременно на **язык интерфейса скрипта** и на **выбор изображений** для распознавания элементов игры. Убедитесь, что он совпадает с языком вашей игры.

---

## Предварительная настройка

### Обнаружение подмотки
По умолчанию бот отслеживает шпулю (красная рамка), чтобы определить прогресс подмотки.
Убедитесь, что катушка полностью заполнена леской, иначе бот не поднимет удочку вовремя.
Если используете радужную леску, добавьте параметр `-R` — бот будет отслеживать индикатор метража (зелёная рамка), что точнее.
Подробнее см. **[CONFIGURATION][configuration]**.

![status]

### Фиксация щелчка мыши (ClickLock)
Если в Windows включена функция «Фиксация щелчка» (ClickLock), установите длительное время удержания.

![click_lock]

### Отображение
- Масштаб интерфейса в системе и в игре: **1x**
- Режим окна игры: **оконный** или **безрамочный оконный**

---

## Использование

### Донная ловля
Добавьте удочки в слоты быстрого выбора, забросьте и разместите рядом — бот будет управлять ими клавишами `1`–`3`.

### Спиннинг, морская ловля, телескоп и др.
Возьмите в руки нужную удочку.

> [!NOTE]
> Несколько удочек одновременно поддерживает только режим **донной ловли**.

### Запуск

**Исполняемый файл** — двойной щелчок или:
```
.\main.exe
```

**Python:**
```
python main.py
```

**uv:**
```
uv run main.py
```

> [!TIP]
> Подробнее о параметрах запуска и настройке профилей: **[CONFIGURATION][configuration]**.

---

## Возможности

| Функция | Описание |
|---|---|
| Рыболовный бот | Автоматическая рыбалка |
| Крафт предметов | Создание наживок, прикормок, приманок и т.д. |
| Движение вперёд | Переключение `W` (или `Shift+W` для бега) |
| Сбор наживки | Автоматический сбор наживки в режиме ожидания |
| Авто фрикцион | Автоматическая регулировка фрикционного тормоза |
| Расчёт снасти | Расчёт характеристик снасти и рекомендуемого фрикциона |

---

## Решение проблем

<details>
<summary>Windows Defender определяет файл как вредоносное ПО</summary>

Это ложное срабатывание. Подробнее: [Nuitka FAQ][malware].
</details>

<details>
<summary>Не удаётся остановить скрипт</summary>

Некоторые клавиши могли «залипнуть» (`Ctrl`, `Shift`, кнопка мыши). Нажмите их ещё раз, затем используйте `Ctrl+C`.
</details>

<details>
<summary>Зависает на 12x% при забросе</summary>

- Убедитесь, что язык игры совпадает с параметром `LANGUAGE` в конфиге.
- Убедитесь, что катушка полностью намотана, или используйте радужную леску с флагом `-R`.
</details>

<details>
<summary>Не поднимает удочку, когда рыба рядом</summary>

- Убедитесь, что катушка полностью намотана, или используйте радужную леску с флагом `-R`.
- Измените размер окна игры.
- Уменьшите `BOT.SPOOL_CONFIDENCE` в `config.yaml`.
- Избегайте ярких источников света (прямые солнечные лучи), выключите свет на лодке.
</details>

<details>
<summary>Бот запущен, но ничего не происходит</summary>

Запустите от имени администратора.
</details>

---

## Журнал изменений
См. **[CHANGELOG][changelog]**.

## Лицензия
**[GNU General Public License v3][license]**

## Участие
Принимаются любые вклады: исправления ошибок, предложения функций, переводы.

## Контакты
dereklee0310@gmail.com

[readme_en]: /README.md
[readme_zh-TW]: /docs/zh-TW/README.md
[rf4s_logo]: /static/readme/RF4S.png
[click_lock]: /static/readme/clicklock.png
[malware]: https://nuitka.net/user-documentation/common-issue-solutions.html#windows-virus-scanners

[discord]: https://discord.gg/BZQWQnAMbY
[python]: https://www.python.org/downloads/
[releases]: https://github.com/dereklee0310/RussianFishing4Script/releases
[status]: /static/readme/status.png
[configuration]: /docs/ru/CONFIGURATION.md
[changelog]: /docs/ru/CHANGELOG.md
[license]: /LICENSE
[installation]: /docs/ru/INSTALLATION.md
