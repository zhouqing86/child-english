---
name: douyin-video-publish
description: 'Publish child-english lesson videos to Douyin. Use for lesson video upload, metadata filling, collection selection, publish verification, and diagnosing broken lesson mp4 files before publishing.'
argument-hint: 'Provide the lesson name, for example: lesson22'
user-invocable: true
---

# Douyin Video Publish

Use this skill when publishing a lesson video from this repository to Douyin creator center.

This skill captures the validated workflow used in this project for lessons 2 and 6 through 24, including the file-repair path that was needed for lesson22.

## When To Use
- Publish `lessonN` video content to Douyin.
- Republish a lesson that failed to upload or failed to appear in content management.
- Verify title, bilingual description, tags, collection episode, and save permission before clicking publish.
- Diagnose a lesson mp4 that does not enter the Douyin uploaded preview state.

## Project Defaults
- Collection: `儿童日常对话英语`
- Tags: `#亲子英语 #小学英语 #少儿英语`
- Description source: [publish checklist](./references/publish-checklist.md)
- Canonical videos: workspace `videos/lessonN.mp4`
- Browser upload staging: `D:\Program Files\Microsoft VS Code\.playwright-mcp\uploads\lessonN.mp4`
- Required save setting: `不允许`

## Standard Procedure
1. Identify the lesson number and read the matching section from `video-descriptions.md`.
2. Verify the source video exists at `videos/lessonN.mp4`.
3. Validate the video before upload.
   - Prefer loading it with `moviepy` or `ffmpeg`.
   - If the file cannot be read or Douyin never leaves the empty upload state, regenerate the lesson video.
4. Copy the lesson mp4 into the Playwright upload staging folder.
5. Open Douyin creator center publish page:
   - `https://creator.douyin.com/creator-micro/content/post/video?enter_from=publish_page`
6. Upload the lesson mp4 and wait until the page enters the normal preview state.
   - Do not continue while the page still shows only the large `点击上传` area.
7. Fill title as `儿童日常对话英语 - 第N课`.
8. Fill description with the three tags followed by the bilingual lesson lines from `video-descriptions.md`.
9. Prefer adding tags conservatively:
   - Type one hashtag at a time.
   - Select the matching dropdown suggestion for each of `#亲子英语`, `#小学英语`, `#少儿英语`.
10. Select the collection `儿童日常对话英语` and verify the page shows `第N集`.
11. Change save permission from `允许` to `不允许`.
12. Recheck these fields before publish:
   - title is present
   - description is bilingual and complete
   - collection shows `第N集`
   - save permission is `不允许`
   - upload preview is visible
13. Click `发布`.
14. Confirm navigation to content management and verify the lesson appears there.

## Regeneration Procedure
Use this when the mp4 is corrupt or Douyin upload does not transition into preview mode.

1. Run the repository video generator:
   - `d:/dev/workspace/child-english/.venv/Scripts/python.exe scripts/generate_lesson_video.py --lesson lessonN`
2. Validate the regenerated file with `moviepy` by opening `lessonN/video/lessonN.mp4`.
3. Replace `videos/lessonN.mp4` with the regenerated file.
4. Copy the regenerated file into the Playwright upload staging directory.
5. Retry the publish flow from a fresh Douyin publish page.

## Verified Troubleshooting Rules
- If Douyin accepts the file chooser but never shows preview, suspect a broken mp4 first.
- `moov atom not found` means the mp4 container is corrupt and must be regenerated or replaced.
- If title input is unstable, use DOM-based value assignment and dispatch input/change events.
- If the page state is obviously stale, open a fresh publish page before retrying.
- Do not trust a draft-looking page that still shows the empty upload block.

## Final Verification
After publish, open content management and confirm the lesson state.

- `已发布`: publish completed successfully.
- `审核中`: submit succeeded, but final publication is still pending review.
- missing from results: treat as failed and retry from the publish page.

## References
- [publish checklist](./references/publish-checklist.md)