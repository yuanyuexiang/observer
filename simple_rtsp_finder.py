#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化RTSP地址测试工具 - 无需用户名密码
"""

import cv2
import time

def test_rtsp_addresses_simple(base_ip):
    """测试常见的无认证RTSP地址组合"""
    print(f"🔍 测试摄像头IP: {base_ip}")
    print("🔓 测试无认证RTSP地址")
    print("=" * 50)
    
    # 常见端口和路径组合
    test_combinations = [
        # 端口554 - RTSP标准端口
        (554, '/stream'),
        (554, '/live'),
        (554, '/video'),
        (554, '/cam'),
        (554, '/h264'),
        (554, '/'),
        
        # 端口8080 - 常见web端口
        (8080, '/h264.sdp'),
        (8080, '/stream'),
        (8080, '/video'),
        (8080, '/live'),
        (8080, '/test.sdp'),
        (8080, '/'),
        
        # 其他常见端口
        (8554, '/stream'),
        (1935, '/live'),
        (5554, '/video'),
    ]
    
    successful_urls = []
    
    for port, path in test_combinations:
        rtsp_url = f"rtsp://{base_ip}:{port}{path}"
        print(f"🧪 测试: {rtsp_url}")
        
        success = quick_test_rtsp(rtsp_url)
        if success:
            successful_urls.append(rtsp_url)
            print(f"   ✅ 连接成功!")
        else:
            print(f"   ❌ 连接失败")
    
    print("\n" + "=" * 50)
    if successful_urls:
        print(f"🎉 找到 {len(successful_urls)} 个可用的RTSP地址:")
        for i, url in enumerate(successful_urls, 1):
            print(f"   {i}. {url}")
        
        print(f"\n💡 推荐使用:")
        best_url = successful_urls[0]
        print(f"   {best_url}")
        
        print(f"\n📋 测试命令:")
        print(f"   python3 simple_cli.py video {best_url}")
        
    else:
        print("😞 没有找到可用的RTSP地址")
        print("\n🔧 可能的问题:")
        print("   • 摄像头RTSP服务未启用")
        print("   • IP地址不正确")
        print("   • 网络连接问题")
        print("   • 需要特殊的路径格式")
        
        print(f"\n💡 手动检查建议:")
        print("   1. ping 192.168.3.61 确认网络连通")
        print("   2. 访问 http://192.168.3.61 查看web界面")
        print("   3. 查看摄像头说明书中的RTSP设置")

def quick_test_rtsp(rtsp_url, timeout=3):
    """快速测试RTSP地址（3秒超时）"""
    try:
        cap = cv2.VideoCapture(rtsp_url)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        cap.set(cv2.CAP_PROP_TIMEOUT, timeout * 1000)  # 设置超时
        
        start_time = time.time()
        success = False
        
        # 快速检测
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                success = True
        
        cap.release()
        return success
        
    except Exception:
        return False

def main():
    """主函数"""
    print("🔍 简化RTSP地址测试工具")
    print("=" * 50)
    
    # 根据您之前的失败地址
    base_ip = "192.168.3.61"
    
    print(f"📍 基于您的摄像头IP: {base_ip}")
    print(f"❌ 失败地址: rtsp://192.168.3.61:8080/test.sdp")
    print(f"🔍 现在测试其他可能的地址...\n")
    
    test_rtsp_addresses_simple(base_ip)

if __name__ == "__main__":
    main()