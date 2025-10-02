import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional

import numpy as np
import soundfile as sf
import librosa

from transformers import pipeline


@dataclass
class EmotionResult:
    emotion: str
    confidence: float
    intensity: str
    secondary_emotions: List[str]
    scores: Dict[str, float]


class VoiceToEmotion:
    """
    superb/hubert-large-superb-er
    返回与 FaceToEmotion 相同风格的 JSON 字段。
    """

    def __init__(
        self,
        model_name: str = "superb/hubert-large-superb-er",
        device: Optional[int] = 0,         # CUDA: device=0；CPU: device=None 或 -1
        target_sr: int = 16000
    ):
        self.target_sr = target_sr
        # transformers 的 audio-classification 管线可以直接吃 numpy/int16 或文件路径
        self.pipe = pipeline(
            task="audio-classification",
            model=model_name,
            device=device if device is not None else -1,
            top_k=None  # 返回全标签分数，便于组装 scores/secondary
        )

    # --- 工具函数们 ---
    @staticmethod
    def _intensity(score: float) -> str:
        if score >= 0.8:
            return "high"
        elif score >= 0.5:
            return "medium"
        else:
            return "low"

    def _load_audio(self, path: str) -> np.ndarray:
        """读取音频，转单声道 & 16k 采样率（或指定的 target_sr）。"""
        # 优先用 soundfile 读（支持多数格式）
        wav, sr = sf.read(path, always_2d=False)
        # 转为 float32
        if wav.dtype != np.float32:
            wav = wav.astype(np.float32, copy=False)

        # 多通道 -> 单通道
        if wav.ndim == 2:
            wav = np.mean(wav, axis=1)

        # 重采样到 target_sr
        if sr != self.target_sr:
            wav = librosa.resample(y=wav, orig_sr=sr, target_sr=self.target_sr)

        return wav

    # --- 对外主函数 ---
    def analyze_file(self, path: str) -> List[Dict[str, Any]]:

        audio = self._load_audio(path)
        # 传 numpy 给 pipeline
        outputs = self.pipe(audio, sampling_rate=self.target_sr)
        print(outputs)##上线删掉

        # 排序
        outputs = sorted(outputs, key=lambda x: x["score"], reverse=True)

        primary = outputs[0]["label"]
        pscore = float(outputs[0]["score"])

        secondary = [o["label"] for o in outputs[1:4] if o["score"] > 0.0]
        scores = {o["label"]: float(o["score"]) for o in outputs}

        result = EmotionResult(
            emotion=primary,
            confidence=round(pscore, 4),
            intensity=self._intensity(pscore),
            secondary_emotions=secondary,
            scores={k: round(v, 4) for k, v in scores.items()}
        )

        # 与 FaceToEmotion 对齐：返回列表，每条为 dict
        return [result.__dict__]

    def analyze_and_save_json(self, path: str, out_json: str, pretty: bool = True) -> None:
        res = self.analyze_file(path)
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=2 if pretty else None)


