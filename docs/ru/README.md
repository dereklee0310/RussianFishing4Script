**[[English version]][readme_en]** **[[中文版]][readme_zh-TW]**
<div align="center">

![RF4S][rf4s_logo]
<h1 align="center">RF4S: Скрипт для игры Russian Fishing 4</h1>

**Простой бот для игры Russian Fishing 4, поддерживающий спиннинговую, донную, морскую и поплавочную ловлю.**

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://opensource.org/license/gpl-3-0)
[![Discord](https://img.shields.io/badge/discord-join-rf44.svg?labelColor=191937&color=6F6FF7&logo=discord)](https://discord.gg/BZQWQnAMbY)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat)](http://makeapullrequest.com)
[![Python: 3.10 | 3.11 | 3.12](https://img.shields.io/badge/python-3.10_%7C_3.11_%7C_3.12-blue)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

<!-- <a target="_blank" href="https://github.com/pylint-dev/pylint" style="background:none">
    <img src="https://img.shields.io/badge/linting-pylint-yellowgreen" style="height: 22px;" />
</a> -->
<!-- <a target="_blank" href="https://github.com/psf/black" style="background:none">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" style="height: 22px;" />
</a> -->
<!-- <a target="_blank" href="link_to_docs, tbd" style="background:none">
    <img src="https://img.shields.io/badge/docs-%23BE1B55" style="height: 22px;" />
</a> -->  

</div>

> [!TIP]
> Присоединяйтесь к нашему [серверу Discord][discord], если хотите предложить новые функции, сообщить об ошибках или получить помощь по использованию скрипта.

## Установка
> [!WARNING] 
> Путь к загрузке не должен содержать неанглийские символы.
### Исполняемый файл (.exe)
Скачайте `rf4s.zip` из раздела [Releases][releases].
> [!WARNING] 
> Исполняемый файл с большей вероятностью будет обнаружен. Рекомендуем запускать скрипт через Python.
> Если вы не знаете, как запустить его через Python, см. раздел **[УСТАНОВКА][installation]**.
### pip
```
git clone https://github.com/dereklee0310/RussianFishing4Script.git
cd RussianFishing4Script
pip install -r requirements.txt
```
> [!IMPORTANT] 
> Python версии 3.13 и выше не поддерживаются. Требуемые версии: >=3.10, <=3.12.

### uv
```
git clone https://github.com/dereklee0310/RussianFishing4Script.git
cd RussianFishing4Script
uv sync
```

## Настройки
### Фиксация щелчка мыши в Windows
Если включена функция «Фиксация щелчка мыши» в Windows, установите длительное время удержания.

![click_lock]
### Отображение
Установите масштаб интерфейса системы и игры в «1x» и используйте «оконный режим» или «безрамочный оконный режим» для окна игры.
### Обнаружение катушки
По умолчанию бот отслеживает катушку (красная рамка), чтобы определить прогресс подмотки.  
Убедитесь, что катушка полностью намотана леской, чтобы точно определить завершение подмотки.  
Если используется радужная леска, включите флаг `-R`, чтобы переключить обнаружение на шкалу (зелёная рамка) для лучшей точности.  
Подробности см. в разделе **[CONFIGURATION][configuration]**.

![status]

## Использование
### Донная ловля
Добавьте свои удочки в слоты быстрого выбора, забросьте их и разместите поблизости, чтобы бот мог управлять ими с помощью клавиш (1 ~ 3).
### Спиннинг, морская ловля, телескопическая удочка и др.
Возьмите в руки удочку, которую хотите использовать.
> [!NOTE]
> В настоящее время только режим донной ловли поддерживает несколько удочек.
### Исполняемый файл (.exe)
Запустите двойным щелчком или командой:
```
.\main.exe
```
### Python
```
python main.py
```
### uv
```
uv run main.py
```

> [!TIP]
> См. **[CONFIGURATION][configuration]** для расширенного использования и настройки.

## Возможности
| Возможность                  | Описание                                              |
| ------------------------ | -------------------------------------------------------- |
| Бот для рыбалки              | Автоматический бот для рыбалки                                         |
| Создание предметов              | Создание наживок, прикормок, приманок и т.д.                     |
| Движение вперёд           | Переключение `W` (или `Shift + W` для бега)                |
| Сбор наживок            | Автоматический сбор наживок в режиме ожидания                |
| Автоматический тормоз сцепления  | Автоматическая регулировка тормоза сцепления                  |
| Расчёт характеристик снасти | Расчёт характеристик снасти и рекомендованного тормоза сцепления   |

## Устранение неполадок
<details>
<summary>Windows Defender определяет как вредоносное ПО?</summary>

- Это ложное срабатывание, см. [эту страницу][malware]. 
</details>
<!-- ------------------------------- divide -------------------------------- -->
<details>
<summary>Не могу остановить скрипт?</summary>

- Некоторые клавиши могли залипнуть (например, `Ctrl`, `Shift`, кнопка мыши и т.д.).  
  Нажмите их ещё раз, чтобы отпустить, затем введите `Ctrl-C` как обычно.
</details>
<!-- ------------------------------- divide -------------------------------- -->
<details>
<summary>Залипает на 12x% при забросе?</summary>

- Убедитесь, что язык игры и язык скрипта совпадают.
- Убедитесь, что катушка полностью намотана, или используйте радужную леску и флаг `-R`. 
</details>
<!-- ------------------------------- divide -------------------------------- -->
<details>
<summary>После окончания подмотки не поднимает удочку?</summary>

- Убедитесь, что катушка полностью намотана, или используйте радужную леску и флаг `-R`. 
- Измените размер окна игры.
- Уменьшите значение `BOT.SPOOL_CONFIDENCE` в файле `config.yaml`.
- Избегайте ярких источников света (например, прямых солнечных лучей) или выключите освещение на лодке.
</details>
<!-- ------------------------------- divide -------------------------------- -->
<details>
<summary>Бот работает, но ничего не происходит?</summary>

- Запустите от имени администратора.
</details>
<!-- ------------------------------- divide -------------------------------- -->

## Журнал изменений
См. **[CHANGELOG][changelog].**

## Лицензия
**[GNU General Public License версия 3][license]**

## Участие
Приветствуются любые вклады, отчёты об ошибках и идеи по новым функциям.

## Связь
dereklee0310@gmail.com 

[readme_en]: /README.md
[readme_zh-TW]: /docs/zh-TW/README.md
[rf4s_logo]: /static/readme/RF4S.png
[python_badge]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[windows_badge]: https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white
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