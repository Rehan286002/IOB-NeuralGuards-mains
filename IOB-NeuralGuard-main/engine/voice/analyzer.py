import numpy as np
import librosa
from pathlib import Path
from core.logger import get_logger

logger = get_logger(__name__)

AUDIO_DIR = Path("engine/voice/sample_audio").resolve()

def analyze_voice(audio_ref: str) -> dict:
    try:
        safe_path = (AUDIO_DIR / Path(audio_ref).name).resolve()
        if not safe_path.is_relative_to(AUDIO_DIR):
            logger.error(f"Path traversal attempt: {audio_ref}")
            raise ValueError("Invalid audio reference path.")

        if not safe_path.exists():
            logger.warning(f"Audio file not found: {safe_path}")
            return {"decision": "ALLOW", "reason": "file_not_found"}

        y, sr = librosa.load(str(safe_path), sr=None)

        flatness = librosa.feature.spectral_flatness(y=y)
        zcr = librosa.feature.zero_crossing_rate(y=y)

        mean_flatness = float(np.mean(flatness))
        mean_zcr = float(np.mean(zcr))

        fraud_score = 0.0
        if mean_flatness > 0.3:
            fraud_score += 0.5
        if mean_zcr > 0.1:
            fraud_score += 0.3
        fraud_score = min(fraud_score, 1.0)

        logger.info(f"Voice analysis: {audio_ref} | score={fraud_score} | flatness={mean_flatness:.4f} | zcr={mean_zcr:.4f}")

        if fraud_score >= 0.5:
            return {"decision": "BLOCK", "reason": "deepfake_detected", "score": fraud_score}

        return {"decision": "ALLOW", "score": fraud_score}

    except Exception as e:
        logger.error(f"Voice analysis failed for {audio_ref}: {str(e)}")
        return {"decision": "ALLOW", "error": "voice_analysis_unavailable", "detail": str(e)}
