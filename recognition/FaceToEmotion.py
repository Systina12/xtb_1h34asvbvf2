from pathlib import Path#测试代码

import cv2
import json
from fer import FER

class FaceToEmotion:
    def __init__(self):
        self.detector = FER(mtcnn=True)

    def _intensity(self, score: float) :
        if score >= 0.8:
            return "high"
        elif score >= 0.5:
            return "medium"
        else:
            return "low"


    def analyze_file(self, path: str):
        img = cv2.imread(path)
        if img is None:
            raise FileNotFoundError(f"Cannot read image: {path}")##提前抛出错误，不用浪费时间导入fer
        results = self.detector.detect_emotions(img)
        print(results)##调试用代码，上线删除

        outputs = []
        for r in results:
            emotions = r["emotions"]
            primary = max(emotions, key=emotions.get)
            score = float(emotions[primary])

            # 取前三个次级情绪
            secondary = sorted(
                [(k, float(v)) for k, v in emotions.items() if k != primary and v > 0],
                key=lambda x: x[1], reverse=True
            )[:3]

            outputs.append({
                "emotion": primary,
                "confidence": round(score, 4),
                "intensity": self._intensity(score),
                "secondary_emotions": [k for k, _ in secondary],
                "scores": {k: round(float(v), 4) for k, v in emotions.items()},
                "bbox": r["box"]  # [x, y, w, h]
            })
        return outputs

    def draw_bbox(self, image_path: str, results, save_path: str = None):
        img = cv2.imread(image_path)
        for r in results:
            x, y, w, h = r["bbox"]
            emo = r["emotion"]
            conf = r["confidence"]

            # 画矩形框
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # 在框上写文字
            label = f"{emo} ({conf:.2f})"
            cv2.putText(img, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 255, 0), 2)

        if save_path:
            cv2.imwrite(save_path, img)
        else:
            cv2.imshow("Emotion Detection", img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()



