# Spec: migrate-whisper-to-systemd

## Goal
Move the whisper audio transcription service from a Docker sidecar to a systemd unit, eliminating Docker dependency for this component while maintaining API compatibility with the siphon-server audio pipeline.

## Interface / Scope
- **In scope:**
  - Siphon-server audio pipeline (`transcribe.py`) calls the new systemd service instead of the Docker container
  - whisper.cpp binary runs as a persistent systemd service on alphablue
  - API contract: `POST /process` with multipart WAV upload, returns `{segments: [{text, start, end}]}`
- **Out of scope:**
  - Diarization service migration (separate concern, runs on port 8000)
  - Docker cleanup/removal (workers directory left as dead code)
  - Model changes (stays on `ggml-large-v3-turbo.bin`)
  - GPU acceleration (service runs CPU-only with `--no-gpu`)

## Non-goals
- **Diarization migration.** The diarization worker (port 8000) is a separate systemd migration. Don't touch it here.
- **Docker removal from the project.** Other workers (diarization_gpu, flux_imagegen) still use Docker. This spec only covers whisper.
- **Performance optimization.** The systemd service already runs with `--threads 16`. No tuning needed for this migration.
- **Multi-host deployment.** The systemd service runs only on alphablue. No load balancing or failover.

## Design decisions

1. **Keep the URL in code, not env.** The service is single-host (alphablue) and single-port (9090). Hardcode `http://172.16.0.2:9090` rather than adding an env var. The existing pattern in `diarize.py` uses a hardcoded URL. Consistency matters.

   *Rejected:* `os.getenv("WHISPER_SERVICE_URL", ...)` — adds config surface for a fixed deployment.

2. **Align whisper.cpp endpoint to match existing code.** whisper.cpp defaults to `/inference`. Change the service to use `/process` via `--inference-path /process` rather than updating the client code. The service is internal; changing one flag is simpler than changing one line of code plus a docstring.

   *Rejected:* Updating `transcribe.py` to call `/inference` — would require changing the URL construction and testing.

3. **Response shape is compatible as-is.** whisper.cpp returns `{text, segments: [{id, start, end, text, tokens}]}`. The `format_simple()` function only reads `chunk["start"]` and `chunk["text"]` from each segment. Extra fields are ignored. No adapter needed.

   *Rejected:* Writing a response adapter — unnecessary complexity.

4. **Service restart policy.** Change `Restart=on-failure` to `Restart=always` so the service recovers from clean exits (like the current `code=0/SUCCESS` state). The `Restart=on-failure` policy left the service down after the last exit.

   *Rejected:* Leaving `Restart=on-failure` — the service is currently dead and won't self-heal.

## Changes

### `/etc/systemd/system/whisper.service`
- Add `--inference-path /process` to `ExecStart` flags
- Change `Restart=on-failure` to `Restart=always`

```ini
[Service]
User=fishhouses
Group=fishhouses
ExecStart=/home/fishhouses/services/whisper/build/bin/whisper-server \
    -m /mnt/storage/models/whisper/ggml-large-v3-turbo.bin \
    --host 0.0.0.0 \
    --port 9090 \
    --no-gpu \
    --threads 16 \
    --inference-path /process
Restart=always
RestartSec=5
```

### `src/siphon_server/sources/audio/pipeline/transcribe.py`
- Change `TRANSCRIPTION_SERVICE_URL` from `http://localhost:8002` to `http://172.16.0.2:9090`
- Remove `import os` (no longer needed — no env var lookup)
- Update docstring to drop "Docker sidecar" reference

```python
TRANSCRIPTION_SERVICE_URL = "http://172.16.0.2:9090"
```

### `src/siphon_server/sources/audio/pipeline/diarize.py`
- No changes. Service still runs on `localhost:8000` (Docker sidecar, separate migration).

## Acceptance criteria

1. **Service is running.** `systemctl is-active whisper.service` returns `active` after `systemctl daemon-reload && systemctl restart whisper`.

2. **Endpoint responds.** `curl -X POST http://172.16.0.2:9090/process -F "file=@test.wav"` returns HTTP 200 with a JSON body containing a `segments` array.

3. **Response shape matches.** Each segment in the `segments` array contains `text` and `start` fields. The `format_simple()` function can process the response without modification.

4. **Audio pipeline works end-to-end.** Running `python -m siphon_server.sources.audio.pipeline.audio_pipeline` on a test WAV file produces formatted transcript output (timestamps + text).

5. **No Docker dependency.** The whisper Docker container (`whisper_gpu`) is no longer required for audio transcription. The Docker Compose service can be removed or left as dead code.

6. **Video sources still work.** Uploading a video file through the siphon pipeline transcribes the audio track successfully (video extractor calls the same `retrieve_audio()` function).
