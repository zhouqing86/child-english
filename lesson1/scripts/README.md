# Lesson 1 Scripts

## 1. 安装依赖

在项目根目录执行：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 2. 生成 lesson1 音频

在项目根目录执行：

```powershell
.\.venv\Scripts\python.exe .\lesson1\scripts\generate_audio.py
```

也可以使用项目级脚本：

```powershell
.\.venv\Scripts\python.exe .\scripts\generate_audio.py --lesson lesson1
```

如果想换语音，可以执行：

```powershell
.\.venv\Scripts\python.exe .\lesson1\scripts\generate_audio.py --voice en-US-JennyNeural
```

生成结果会保存到 lesson1/audio 目录。

## 3. 下载合法授权视频素材

先申请 Pexels API Key，然后执行：

```powershell
$env:PEXELS_API_KEY="你的_api_key"
.\.venv\Scripts\python.exe .\lesson1\scripts\download_pexels_video.py --query "child brushing teeth" --output .\lesson1\video\01_brush_your_teeth.mp4
```

## 4. 说明

不建议下载版权来源不清晰的视频。优先使用自制视频或明确授权的库存素材。