#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RTSP功能测试脚本
"""

import cv2
import time

def test_rtsp_connection(rtsp_url):
    """测试RTSP连接"""
    print(f"🧪 测试RTSP连接: {rtsp_url}")
    
    # 测试OpenCV是否能创建VideoCapture对象
    try:
        cap = cv2.VideoCapture(rtsp_url)
        
        # 设置参数
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        cap.set(cv2.CAP_PROP_FPS, 25)
        
        print(f"📹 VideoCapture对象创建成功")
        
        # 测试是否能打开
        is_opened = cap.isOpened()
        print(f"📡 连接状态: {'✅ 已连接' if is_opened else '❌ 连接失败'}")
        
        if is_opened:
            # 尝试读取一帧
            print("🔍 尝试读取视频帧...")
            start_time = time.time()
            ret, frame = cap.read()
            end_time = time.time()
            
            if ret:
                height, width = frame.shape[:2]
                print(f"✅ 成功读取帧: {width}x{height}, 耗时: {end_time-start_time:.2f}秒")
                return True
            else:
                print("❌ 无法读取视频帧")
                return False
        else:
            print("💡 连接失败可能的原因:")
            print("   • 网络连接问题")
            print("   • RTSP URL错误")
            print("   • 摄像头离线")
            print("   • 认证失败")
            print("   • 防火墙阻止")
            return False
            
    except Exception as e:
        print(f"❌ 测试出错: {e}")
        return False
    finally:
        try:
            cap.release()
        except:
            pass

def test_rtsp_features():
    """测试RTSP功能特性"""
    print("🧪 RTSP功能测试开始\n")
    
    # 测试URL识别
    test_urls = [
        "rtsp://192.168.3.213:8080/h264.sdp",
        "rtsp://admin:password@192.168.1.100:554/stream",
        "rtsp://camera.local/live",
        "http://example.com/video.mp4",  # 非RTSP
        "0",  # 摄像头ID
    ]
    
    print("1️⃣ 测试URL识别:")
    for url in test_urls:
        is_rtsp = url.startswith('rtsp://')
        icon = "📡" if is_rtsp else "📷" if url.isdigit() else "🎬"
        result = "RTSP流" if is_rtsp else "摄像头" if url.isdigit() else "其他"
        print(f"  {icon} {url:<40} -> {result}")
    
    print("\n2️⃣ 测试您的RTSP地址:")
    your_rtsp = "rtsp://192.168.3.213:8080/h264.sdp"
    success = test_rtsp_connection(your_rtsp)
    
    print(f"\n{'='*50}")
    print(f"🎯 测试结果: {'✅ RTSP功能就绪' if success else '⚠️ 需要检查网络连接'}")
    
    if not success:
        print("\n🔧 调试建议:")
        print("1. 确认摄像头IP地址和端口")
        print("2. 检查网络连接")
        print("3. 尝试用VLC播放器测试RTSP流")
        print("4. 检查是否需要用户名密码认证")

if __name__ == "__main__":
    test_rtsp_features()