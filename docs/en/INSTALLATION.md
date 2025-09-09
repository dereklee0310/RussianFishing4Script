## Install Python
### Step 1: [Download][download] Python 3.12.10 installer

### Step 2: Install Python 3.12.10
Select "Use admin privileges when installing py.exe" and "Add python.exe to PATH", then click "Install Now".

![setup][setup]

### Step 3: [Download][github] Source code 

### Step 4: Unzip `RussianFishing4Script-main.zip`

![unzip][unzip]

### Step 5: Copy the full path to the extracted folder

![path][path]

### Step 6: Open Command Prompt
Type `Win + R` and enter cmd to open it.

![cmd][cmd]

### Step 7: Navigate to the project folder
Type `cd <the path from step 5>` in cmd. For example:
```
cd C:\Users\derek\tmp\RussianFishing4Script-main
```

![cd][cd]

### Step 8: Install dependencies
Type the following command — you only need to do this once: 
```
pip install -r requirements.txt
```

![pip][pip]

> [!TIP]
> We strongly recommend creating a virtual environment before installing dependencies. We skip that part because it's a tutorial for dummies. (ha!)

### Step 9: Launch the bot!
Run the bot with this command:
```
python main.py
```

![run][run]

> [!IMPORTANT]
> Every time you reopen Command Prompt, remember to navigate to the project folder first! For example: 
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