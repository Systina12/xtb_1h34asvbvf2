# -*- coding: utf-8 -*-
import os
import io
import json
import time
import uuid
import tempfile
from dataclasses import asdict
from pathlib import Path
from typing import Dict, Any, List

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import cv2
from moviepy.editor import VideoFileClip

from models.FaceToEmotion import FaceToEmotion  # 见下方“模型文件命名”说明
from models.VoiceToEmotion import VoiceToEmotion

# =============== 工具函数 ===============

def _save_uploaded_file(tmpdir: Path, upfile) -> Path:
    """把 Streamlit UploadedFile 落盘，返回路径。"""
    suffix = Path(upfile.name).suffix or ".mp4"
    out = tmpdir / f"upload_{uuid.uuid4().hex}{suffix}"
    with open(out, "wb") as f:
        f.write(upfile.getbuffer())
    return out


def _iter_keyframes_opencv(video_path: Path, fps_pick: int = 1):
    """按每秒 1 帧抽帧，yield (sec, frame[BGR])."""
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    duration = int(max(1, round(total_frames / max(1.0, fps))))

    for sec in range(duration):
        cap.set(cv2.CAP_PROP_POS_MSEC, sec * 1000)
        ok, frame = cap.read()
        if not ok or frame is None:
            continue
        yield sec, frame
    cap.release()


def _draw_bbox_on_frame(frame_bgr: np.ndarray, results: List[Dict[str, Any]]):
    img = frame_bgr.copy()
    for r in results:
        x, y, w, h = r.get("bbox", [0, 0, 0, 0])
        emo = r.get("emotion", "?")
        conf = r.get("confidence", 0.0)
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        label = f"{emo} ({conf:.2f})"
        cv2.putText(img, label, (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    return img


def _write_wav(tmpdir: Path, sec_audio: np.ndarray, sr: int) -> Path:
    import soundfile as sf
    p = tmpdir / f"seg_{uuid.uuid4().hex}.wav"
    sf.write(p, sec_audio.astype(np.float32), sr)
    return p



def render_video_emotion_page():
    st.header("🎬 AI情绪识别")
    st.caption("上传 mp4/mov 等视频文件，系统将按秒抽帧与音频做人脸与语音情感识别。")

    up = st.file_uploader("上传视频文件", type=["mp4", "mov", "mkv", "avi"])
    col_a, col_b = st.columns(2)
    with col_a:
        do_draw = st.checkbox("在帧上绘制人脸框与情绪标签", value=True)
    with col_b:
        max_secs = st.number_input("最多处理秒数（0=全时长）", min_value=0, value=0, step=1)

    if not up:
        st.info("请先上传一个视频文件。")
        return

    with st.spinner("正在初始化模型（可能需要数十秒，首次加载较慢）..."):
        face_model = FaceToEmotion()
        voice_model = VoiceToEmotion()

    results_rows = []  # 用于 DataFrame 展示
    json_dump = {}     # {sec: {voice:..., face:[...]}}

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        video_path = _save_uploaded_file(td, up)

        # 读取音频（moviepy）
        clip = VideoFileClip(str(video_path))
        if clip.audio is None:
            st.error("该视频不包含音轨，无法进行语音情感识别。")
            return

        fps = clip.fps or 25.0
        duration = int(clip.duration or 0)
        if max_secs and max_secs > 0:
            duration = min(duration, int(max_secs))

        st.write(f"视频时长：{duration} 秒，帧率：{fps:.2f} FPS")
        prog = st.progress(0)

        # 逐秒：抽音频、抽帧、调用两种模型
        for sec, frame in _iter_keyframes_opencv(video_path):
            if sec >= duration:
                break

            # --- 1) 每秒音频切片 ---
            # moviepy 直接截取该秒音频并转 mono float32，16k 采样
            try:
                asec = clip.audio.subclip(sec, min(sec + 1, duration))
                # to_soundarray 默认 sr=44100，转 mono
                arr = asec.to_soundarray(fps=16000)  # shape [T,2] or [T]
                if arr.ndim == 2:
                    arr = arr.mean(axis=1)
                wav_path = _write_wav(td, arr, 16000)
                voice_json = voice_model.analyze_file(str(wav_path))  # list[dict]
            except Exception as e:
                voice_json = [{"error": str(e)}]

            # --- 2) 该秒关键帧做人脸情绪 ---
            # 写临时帧文件给 Face 模型（其接口接受路径）
            frame_path = td / f"frame_{sec:06d}.jpg"
            cv2.imwrite(str(frame_path), frame)
            try:
                face_json = face_model.analyze_file(str(frame_path))  # list[dict]
            except Exception as e:
                face_json = [{"error": str(e)}]

            # 可选：绘制框供预览
            preview_img = None
            if do_draw and isinstance(face_json, list) and face_json and "bbox" in face_json[0]:
                preview_img = _draw_bbox_on_frame(frame, face_json)

            # 组织行数据（便于 DataFrame 展示）
            top_voice = voice_json[0] if isinstance(voice_json, list) and voice_json else {}
            top_face = face_json[0] if isinstance(face_json, list) and face_json else {}

            row = {
                "second": sec,
                "voice_emotion": top_voice.get("emotion"),
                "voice_confidence": top_voice.get("confidence"),
                "face_emotion": top_face.get("emotion"),
                "face_confidence": top_face.get("confidence"),
            }
            results_rows.append(row)

            json_dump[sec] = {
                "voice": voice_json,  # 与示例一致：list[dict]
                "face": face_json
            }

            # 每 10 秒显示一个预览帧
            if do_draw and preview_img is not None and sec % 10 == 0:
                st.image(cv2.cvtColor(preview_img, cv2.COLOR_BGR2RGB), caption=f"第 {sec} 秒 预览")

            prog.progress(min(1.0, (sec + 1) / max(1, duration)))

        clip.close()

    # =============== 展示结果 ===============
    st.subheader("结果汇总（每秒 Top-1）")
    df = pd.DataFrame(results_rows)
    st.dataframe(df, use_container_width=True)

    # 简单可视化：时间序列置信度（语音/人脸）
    if not df.empty:
        c1, c2 = st.columns(2)
        with c1:
            fig1 = px.line(df, x="second", y="voice_confidence", title="语音情感 Top-1 置信度")
            st.plotly_chart(fig1, use_container_width=True)
        with c2:
            fig2 = px.line(df, x="second", y="face_confidence", title="人脸情感 Top-1 置信度")
            st.plotly_chart(fig2, use_container_width=True)

    # 导出 JSON（结构与示例对齐）
    st.subheader("导出 JSON")
    jbuf = io.StringIO()
    json.dump(json_dump, jbuf, ensure_ascii=False, indent=2)
    st.download_button(
        label="下载识别结果 (per-second.json)",
        data=jbuf.getvalue(),
        file_name="per-second.json",
        mime="application/json",
    )

    st.success("处理完成！")