# Publish Checklist

## Source Of Truth
- Title and bilingual description come from `video-descriptions.md`.
- Video file comes from `videos/lessonN.mp4`.
- If `videos/lessonN.mp4` is broken, regenerate from `lessonN/audio-manifest.json` and `lessonN/dialogues.md` using `scripts/generate_lesson_video.py`.

## Metadata Pattern
- Title: `儿童日常对话英语 - 第N课`
- Tags:
  - `#亲子英语`
  - `#小学英语`
  - `#少儿英语`
- Collection: `儿童日常对话英语`
- Save permission: `不允许`

## Description Pattern
Description body should contain:

1. The three tags.
2. The eight bilingual lines for the lesson.

Example structure:

```text
#亲子英语 #小学英语 #少儿英语
Sentence 1.中文。
Sentence 2.中文。
Sentence 3.中文。
Sentence 4.中文。
Sentence 5.中文。
Sentence 6.中文。
Sentence 7.中文。
Sentence 8.中文。
```

## Publish Gate
Do not click publish until all of these are true:
- video preview is visible
- title is non-empty
- description is filled
- collection shows `第N集`
- save permission shows `不允许`

## Post-Publish Check
Search for `第N课` in content management.

- If state is `已发布`, the task is done.
- If state is `审核中`, the submission succeeded and is waiting for Douyin review.
- If the lesson is absent, retry the publish flow.