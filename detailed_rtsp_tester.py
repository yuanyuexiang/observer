#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细RTSP路径测试工具
"""

import cv2
import time

def test_rtsp_paths_detailed():
    """详细测试8080端口的各种RTSP路径"""
    ip = "192.168.3.61"
    port = 8080
    
    print(f"🔍 详细测试 RTSP 路径")
    print(f"📡 摄像头: {ip}:{port}")
    print("=" * 50)
    
    # 扩展路径列表
    test_paths = [
        # 基础路径
        '/stream',
        '/live', 
        '/video',
        '/cam',
        '/camera',
        '/h264',
        '/h264.sdp',
        '/test.sdp',
        '/main.sdp',
        '/stream.sdp',
        '/',
        
        # 常见厂商路径
        '/h264/ch1/main/av_stream',    # 海康威视
        '/cam/realmonitor?channel=1',   # 大华
        '/videostream.cgi',             # 通用CGI
        '/video.mjpg',                  # MJPEG流
        '/cgi-bin/hi3510/param.cgi',    # 海思芯片
        '/onvif/device_service',        # ONVIF
        
        # 数字路径
        '/1',
        '/0',
        '/ch1',
        '/channel1',
        '/stream1',
        '/video1',
        
        # 特殊格式
        '/h264_ulaw.sdp',
        '/h264_pcm.sdp',
        '/live.sdp',
        '/stream0',
        '/preview_01_sub.sdp',
        '/preview_01_main.sdp',
    ]
    
    successful_urls = []
    
    for path in test_paths:
        rtsp_url = f"rtsp://{ip}:{port}{path}"
        print(f"🧪 测试: {rtsp_url}")
        
        success, info = test_rtsp_with_info(rtsp_url)
        if success:
            successful_urls.append(rtsp_url)
            print(f"   ✅ 成功! {info}")
        else:
            print(f"   ❌ 失败: {info}")
    
    print("\n" + "=" * 50)
    if successful_urls:
        print(f"🎉 找到 {len(successful_urls)} 个可用的RTSP地址:")
        for i, url in enumerate(successful_urls, 1):
            print(f"   {i}. {url}")
        
        print(f"\n🚀 立即测试第一个地址:")
        best_url = successful_urls[0]
        print(f"python3 simple_cli.py video {best_url}")
        
    else:
        print("😞 仍然没有找到可用的RTSP地址")
        print("\n🔧 进一步调试建议:")
        print("   1. 查看摄像头说明书")
        print("   2. 尝试用VLC打开 rtsp://192.168.3.61:8080")
        print("   3. 检查摄像头是否需要启用RTSP服务")
        print("   4. 查看摄像头厂商的默认RTSP路径")

def test_rtsp_with_info(rtsp_url, timeout=3):
    """测试RTSP地址并返回详细信息"""
    try:
        cap = cv2.VideoCapture(rtsp_url)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        start_time = time.time()
        
        if cap.isOpened():
            # 尝试读取帧
            ret, frame = cap.read()
            if ret and frame is not None:
                height, width = frame.shape[:2]
                elapsed = time.time() - start_time
                cap.release()
                return True, f"分辨率: {width}x{height}, 响应时间: {elapsed:.2f}s"
            else:
                cap.release()
                return False, "无法读取视频帧"
        else:
            cap.release()
            return False, "无法打开流"
    
    except Exception as e:
        return False, f"异常: {str(e)[:50]}"

def main():
    """主函数"""
    print("🔍 详细RTSP路径测试工具")
    print("=" * 50)
    test_rtsp_paths_detailed()

if __name__ == "__main__":
    main()