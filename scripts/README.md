# Project Scripts

## 安装依赖

在项目根目录执行：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 生成单个 lesson 音频

```powershell
.\.venv\Scripts\python.exe .\scripts\generate_audio.py --lesson lesson1
```

如果要换语音：

```powershell
.\.venv\Scripts\python.exe .\scripts\generate_audio.py --lesson lesson1 --voice en-US-JennyNeural
```

## 批量生成所有已完成 lesson 音频

```powershell
.\.venv\Scripts\python.exe .\scripts\generate_audio.py --all
```

脚本会自动跳过没有 `audio-manifest.json` 的 lesson。

如果你已经执行过 `.\.venv\Scripts\Activate.ps1`，上面的命令也可以简写为 `python ...`。