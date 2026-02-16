# Installing RF4S

Step-by-step guide for installation and first launch.

---

## Step 1. Install Python 3.12

Download the installer: **[Python 3.12.10 (64-bit)][download]**

During installation, make sure to check:
- **Use admin privileges when installing py.exe**
- **Add python.exe to PATH**

Then click **Install Now**.

![setup][setup]

> [!IMPORTANT]
> Python 3.13+ is not supported. Use versions **3.10**, **3.11**, or **3.12**.

---

## Step 2. Download the source code

Download the archive: **[RussianFishing4Script-main.zip][github]**

---

## Step 3. Extract the archive

Extract `RussianFishing4Script-main.zip` to a convenient folder.

> [!WARNING]
> The folder path **must not** contain Cyrillic or other non-English characters.

![unzip][unzip]

---

## Step 4. Copy the folder path

Open the extracted folder and copy the full path from the Explorer address bar.

![path][path]

---

## Step 5. Open Command Prompt

Press `Win + R`, type `cmd`, and press Enter.

![cmd][cmd]

---

## Step 6. Navigate to the project folder

Type `cd` followed by the copied path:
```
cd C:\Users\derek\tmp\RussianFishing4Script-main
```

![cd][cd]

---

## Step 7. Install dependencies

Run this command once:
```
pip install -r requirements.txt
```

![pip][pip]

> [!TIP]
> Using a virtual environment (`venv`) is recommended, but this step is skipped for simplicity.

---

## Step 8. Launch the bot

```
python main.py
```

On first launch, the script will ask two questions:
1. **Game language** — choose `1` (English) or `2` (Russian)
2. **ClickLock** — whether Windows mouse ClickLock is enabled

Your answers will be saved to `config.yaml`. You can later change the language by editing the `LANGUAGE` parameter in this file:
```yaml
LANGUAGE: "ru"   # Russian interface
LANGUAGE: "en"   # English interface
```

![run][run]

> [!IMPORTANT]
> Every time you reopen Command Prompt, remember to navigate to the project folder first:
> ```
> cd C:\Users\derek\tmp\RussianFishing4Script-main
> python main.py
> ```

---

## Alternative: Installation via uv

[uv](https://docs.astral.sh/uv/) — a faster alternative to pip.

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
