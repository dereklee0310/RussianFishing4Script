## Установка Python
### Шаг 1: [Скачайте][download] установщик Python 3.12.10

### Шаг 2: Установите Python 3.12.10
При установке отметьте галочками **«Использовать права администратора при установке py.exe»** и **«Добавить python.exe в PATH»**, затем нажмите **«Установить сейчас»**.

![setup][setup]

### Шаг 3: [Скачайте][github] исходный код

### Шаг 4: Распакуйте архив `RussianFishing4Script-main.zip`

![unzip][unzip]

### Шаг 5: Скопируйте полный путь к распакованной папке

![path][path]

### Шаг 6: Откройте командную строку
Нажмите `Win + R`, введите `cmd` и нажмите Enter.

![cmd][cmd]

### Шаг 7: Перейдите в папку проекта
В командной строке введите `cd <путь, скопированный на шаге 5>`. Например:

```
cd C:\Users\derek\tmp\RussianFishing4Script-main
```

![cd][cd]

### Шаг 8: Установите зависимости
Выполните следующую команду — достаточно сделать это один раз:
```
pip install -r requirements.txt
```

![pip][pip]

> [!TIP]
> Мы *настоятельно* рекомендуем создать виртуальное окружение перед установкой зависимостей — но мы пропустили этот шаг, чтобы упростить инструкцию для новичков. (Вы справитесь!)

### Шаг 9: Запустите бота!
Запустите бота с помощью этой команды:
```
python main.py
```

![run][run]

> [!IMPORTANT]
> Каждый раз, когда вы снова открываете командную строку, не забывайте сначала перейти в папку проекта! Например:
> ```
> cd C:\Users\derek\tmp\RussianFishing4Script-main
> python main.py
> ```

[download]: https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe  
[installer]: /static/readme/installer.png
[setup]: /static/readme/setup.png
[unzip]: /static/readme/unzip.png
[path]: /static/readme/path.png
[cmd]: /static/readme/cmd.png
[cd]: /static/readme/cd.png
[pip]: /static/readme/pip.png
[run]: /static/readme/run.png
[github]: https://github.com/dereklee0310/RussianFishing4Script/archive/refs/heads/main.zip