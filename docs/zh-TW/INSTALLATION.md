# 安裝 RF4S

逐步安裝與首次啟動指南。

---

## 步驟 1. 安裝 Python 3.12

下載安裝程式：**[Python 3.12.10 (64-bit)][download]**

安裝時請務必勾選：
- **Use admin privileges when installing py.exe**
- **Add python.exe to PATH**

然後點擊 **Install Now**。

![setup][setup]

> [!IMPORTANT]
> 不支援 Python 3.13+。請使用 **3.10**、**3.11** 或 **3.12** 版本。

---

## 步驟 2. 下載原始碼

下載壓縮檔：**[RussianFishing4Script-main.zip][github]**

---

## 步驟 3. 解壓縮

將 `RussianFishing4Script-main.zip` 解壓縮到方便的資料夾。

> [!WARNING]
> 資料夾路徑**不能**包含西里爾字母或其他非英文字元。

![unzip][unzip]

---

## 步驟 4. 複製資料夾路徑

開啟解壓縮後的資料夾，從檔案總管的網址列複製完整路徑。

![path][path]

---

## 步驟 5. 開啟命令提示字元

按下 `Win + R`，輸入 `cmd`，然後按 Enter。

![cmd][cmd]

---

## 步驟 6. 切換到專案資料夾

輸入 `cd` 加上複製的路徑：
```
cd C:\Users\derek\tmp\RussianFishing4Script-main
```

![cd][cd]

---

## 步驟 7. 安裝相依套件

執行以下指令（只需執行一次）：
```
pip install -r requirements.txt
```

![pip][pip]

> [!TIP]
> 建議使用虛擬環境（`venv`），但為了簡單起見，此步驟已略過。

---

## 步驟 8. 啟動機器人

```
python main.py
```

首次啟動時，腳本會詢問兩個問題：
1. **遊戲語言** — 選擇 `1`（English）或 `2`（Русский）
2. **ClickLock** — Windows 滑鼠鎖定點擊是否已啟用

您的回答將儲存到 `config.yaml`。之後可以透過編輯此檔案中的 `LANGUAGE` 參數來更改語言：
```yaml
LANGUAGE: "ru"   # 俄文介面
LANGUAGE: "en"   # 英文介面
```

![run][run]

> [!IMPORTANT]
> 每次重新開啟命令提示字元時，請記得先切換到專案資料夾：
> ```
> cd C:\Users\derek\tmp\RussianFishing4Script-main
> python main.py
> ```

---

## 替代方案：透過 uv 安裝

[uv](https://docs.astral.sh/uv/) — 比 pip 更快的替代工具。

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
