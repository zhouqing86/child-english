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

## 批量生成 dialogues 音频

```powershell
.\.venv\Scripts\python.exe .\scripts\generate_dialogue_audio.py --all
```

生成结果会保存到各 lesson 的 `audio/dialogues` 目录，并按“每段对话一个 mp3”输出。
默认 `Parent` 使用 `en-US-GuyNeural`，`Child` 使用更接近童声的 `en-US-AnaNeural`。

## 生成每个 lesson 的 MP4 视频

```powershell
.\.venv\Scripts\python.exe .\scripts\generate_lesson_video.py --all
```

脚本会把 `audio-manifest.json` 中的句子和 `dialogues.md` 中的对话合并成一个课时视频，输出到各 lesson 的 `video` 目录。

## 下载合法授权视频素材

```powershell
$env:PEXELS_API_KEY="你的_api_key"
.\.venv\Scripts\python.exe .\scripts\download_pexels_video.py --query "child brushing teeth" --output .\lesson1\video\brush_teeth_stock.mp4
```

如果你已经执行过 `.\.venv\Scripts\Activate.ps1`，上面的命令也可以简写为 `python ...`。
