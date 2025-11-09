import logging

logger = logging.getLogger(__name__)


def format(annotated_transcript, group_by_speaker=True):
    """
    Format the annotated transcript into readable text.

    Args:
        annotated_transcript: Output from combine()
        group_by_speaker: Whether to group consecutive words by same speaker

    Returns:
        str: Formatted transcript
    """
    if not annotated_transcript:
        return ""

    if not group_by_speaker:
        logger.warning(
            "[FORMAT] Formatting without grouping by speaker may produce less readable output."
        )
        # Simple word-by-word format
        lines = []
        for item in annotated_transcript:
            timestamp = f"[{item['start_time']:.1f}s]"
            lines.append(f"{timestamp} {item['speaker']}: {item['word']}")
        return "\n".join(lines)

    # Group by speaker for more readable output
    logger.debug("[FORMAT] Formatting transcript by grouping words by speaker.")
    lines = []
    current_speaker = None
    current_words = []
    current_start_time = None

    for item in annotated_transcript:
        speaker = item["speaker"]

        if speaker != current_speaker:
            # Speaker changed, output previous speaker's text
            if current_speaker is not None and current_words:
                timestamp = f"[{current_start_time:.1f}s]"
                text = " ".join(current_words)
                lines.append(f"{timestamp} {current_speaker}: {text}")

            # Start new speaker
            current_speaker = speaker
            current_words = [item["word"]]
            current_start_time = item["start_time"]
        else:
            # Same speaker, add word
            current_words.append(item["word"])

    # Don't forget the last speaker
    logger.debug("[FORMAT] Finalizing transcript for last speaker.")
    if current_speaker is not None and current_words:
        timestamp = f"[{current_start_time:.1f}s]"
        text = " ".join(current_words)
        lines.append(f"{timestamp} {current_speaker}: {text}")

    return "\n".join(lines)
