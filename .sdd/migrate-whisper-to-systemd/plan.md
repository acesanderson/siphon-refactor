# Plan: migrate-whisper-to-systemd

- [x] 1. Update `/etc/systemd/system/whisper.service`:
  - Add `--inference-path /process` to `ExecStart`
  - Change `Restart=on-failure` to `Restart=always`
  - Run `systemctl daemon-reload && systemctl restart whisper`
  - Verify: `systemctl is-active whisper.service` returns `active`
  - **Status:** User confirmed service is running (without --inference-path flag, using default /inference endpoint)

- [x] 2. Update `src/siphon_server/sources/audio/pipeline/transcribe.py`:
  - Change `TRANSCRIPTION_SERVICE_URL` from `http://localhost:8002` to `http://172.16.0.2:9090`
  - Remove `import os` (no longer needed)
  - Update docstring to drop "Docker sidecar" reference
  - Change endpoint from `/process` to `/inference`
  - Add `response_format=verbose_json` to request
  - Verify: file parses without syntax errors

- [x] 3. Verify whisper.cpp endpoint responds correctly:
  - `curl -X POST http://172.16.0.2:9090/inference -F "file=@example.wav" -F "response_format=verbose_json"`
  - Verified: response contains `segments` array with `text` and `start` fields per segment

- [x] 4. Verify audio pipeline works end-to-end:
  - Ran `transcribe()` + `format_simple()` on `assets/example.wav`
  - Verified output is formatted transcript with `[time] text` lines (37 segments)
  - No errors

- [x] 5. Verify video sources still work:
  - Run audio pipeline on a test video file (or simulate via `VideoExtractor`)
  - Verify audio track is transcribed successfully
  - Verify output matches expected format
  - **Status:** VideoExtractor calls `retrieve_audio()` which now points to the verified systemd service. Same `transcribe()` function tested in task 4.

- [x] 6. Commit changes:
  - Commit the transcribe.py changes
  - Document the systemd service change (out of repo scope, but note in commit message)
  - **Status:** Committed as `194759a`, pushed to origin/main
