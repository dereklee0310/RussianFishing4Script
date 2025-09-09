## 安裝 Python
### 步驟 1：[下載][download] Python 3.12.10 安裝程式

### 步驟 2：安裝 Python 3.12.10
安裝時請勾選「安裝 py.exe 時使用管理員權限」與「將 python.exe 加入 PATH」，然後點擊「立即安裝」。

![setup][setup]

### 步驟 3：[下載][github] 原始碼

### 步驟 4：解壓縮 `RussianFishing4Script-main.zip`

![unzip][unzip]

### 步驟 5：複製解壓縮後資料夾的完整路徑

![path][path]

### 步驟 6：開啟命令提示字元
按下 `Win + R`，輸入 `cmd` 後按 Enter 開啟。

![cmd][cmd]

### 步驟 7：切換至專案資料夾
在命令提示字元中輸入 `cd <步驟 5 複製的路徑>`。例如：
```
cd C:\Users\derek\tmp\RussianFishing4Script-main
```

![cd][cd]

### 步驟 8：安裝相依套件
執行以下指令 — 只需執行一次：

```
pip install -r requirements.txt
```

![pip][pip]

> [!TIP]
> 我們強烈建議在安裝相依套件前先建立虛擬環境。但本教學為初學者設計，因此省略此步驟。（哈哈！）

### 步驟 9：啟動機器人！
執行以下指令啟動機器人：

```
python main.py
```

![run][run]

> [!IMPORTANT]
> 每次重新開啟命令提示字元時，請務必先切換至專案資料夾！例如：
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