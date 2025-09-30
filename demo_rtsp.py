#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RTSP工具检测演示
"""

import cv2
import time
import threading

def demo_rtsp_detection():
    """演示RTSP工具检测功能"""
    rtsp_url = "rtsp://192.168.3.213:8080/h264.sdp"
    
    print("🎬 RTSP工具检测演示")
    print(f"📡 RTSP地址: {rtsp_url}")
    print("⏱️ 演示时长: 15秒")
    print("🔍 每10秒进行一次检测")
    print("=" * 50)
    
    # 连接RTSP流
    cap = cv2.VideoCapture(rtsp_url)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    cap.set(cv2.CAP_PROP_FPS, 25)
    
    if not cap.isOpened():
        print("❌ 无法连接RTSP流")
        return
    
    print("✅ RTSP流连接成功!")
    
    start_time = time.time()
    frame_count = 0
    detection_count = 0
    last_detection = 0
    
    try:
        while True:
            current_time = time.time()
            elapsed = current_time - start_time
            
            # 15秒后停止
            if elapsed > 15:
                break
                
            ret, frame = cap.read()
            if not ret:
                print("⚠️ 读取帧失败")
                break
                
            frame_count += 1
            
            # 每10秒进行一次"检测"（演示）
            if current_time - last_detection >= 10:
                detection_count += 1
                last_detection = current_time
                
                print(f"\n🔍 模拟检测 #{detection_count}")
                print(f"📊 帧数: {frame_count}")
                print(f"⏰ 运行时间: {elapsed:.1f}秒")
                print(f"📐 分辨率: {frame.shape[1]}x{frame.shape[0]}")
                
                # 模拟检测结果
                print("🛠️ 模拟检测结果:")
                print("   ✅ 工具1: 在位")
                print("   ✅ 工具2: 在位") 
                print("   ❌ 工具3: 缺失")
                print("   📊 完整性: 66.7%")
            
            # 短暂延迟避免过高CPU使用
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n👋 用户中断")
    finally:
        cap.release()
        print(f"\n🎉 演示结束!")
        print(f"📊 总帧数: {frame_count}")
        print(f"⏱️ 总时长: {elapsed:.1f}秒")
        print(f"🔍 检测次数: {detection_count}")

if __name__ == "__main__":
    demo_rtsp_detection()