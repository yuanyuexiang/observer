#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RTSP地址测试工具 - 帮助找到正确的RTSP地址
"""

import cv2
import time

def test_rtsp_addresses(base_ip, port_list=[554, 8080, 1935, 8554], path_list=['/stream', '/h264.sdp', '/video', '/live', '/cam', '/test.sdp']):
    """测试常见RTSP地址组合"""
    print(f"🔍 测试IP地址: {base_ip}")
    print(f"🔌 测试端口: {port_list}")
    print(f"📂 测试路径: {path_list}")
    print("=" * 60)
    
    successful_urls = []
    
    for port in port_list:
        for path in path_list:
            rtsp_url = f"rtsp://{base_ip}:{port}{path}"
            print(f"\n🧪 测试: {rtsp_url}")
            
            success = test_single_rtsp(rtsp_url, timeout=5)
            if success:
                successful_urls.append(rtsp_url)
                print(f"✅ 成功连接!")
            else:
                print(f"❌ 连接失败")
    
    print("\n" + "=" * 60)
    if successful_urls:
        print(f"🎉 找到 {len(successful_urls)} 个可用的RTSP地址:")
        for url in successful_urls:
            print(f"   ✅ {url}")
        print(f"\n💡 建议使用第一个地址: {successful_urls[0]}")
    else:
        print("😞 没有找到可用的RTSP地址")
        print("\n🔧 建议检查:")
        print("   • 摄像头IP地址是否正确")
        print("   • 摄像头是否支持RTSP")
        print("   • 网络连接是否正常")
        print("   • 是否需要用户名密码")

def test_single_rtsp(rtsp_url, timeout=5):
    """测试单个RTSP地址"""
    try:
        cap = cv2.VideoCapture(rtsp_url)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    cap.release()
                    return True
            time.sleep(0.1)
        
        cap.release()
        return False
        
    except Exception as e:
        return False

def test_with_credentials(base_ip, username="admin", password="admin"):
    """测试带认证的RTSP地址"""
    print(f"\n🔐 测试带认证的RTSP地址")
    print(f"👤 用户名: {username}")
    print(f"🔑 密码: {password}")
    
    auth_urls = [
        f"rtsp://{username}:{password}@{base_ip}:554/stream",
        f"rtsp://{username}:{password}@{base_ip}:8080/h264.sdp",
        f"rtsp://{username}:{password}@{base_ip}:554/live",
        f"rtsp://{username}:{password}@{base_ip}:8080/video",
    ]
    
    successful_urls = []
    for url in auth_urls:
        print(f"\n🧪 测试: {url}")
        success = test_single_rtsp(url, timeout=5)
        if success:
            successful_urls.append(url)
            print(f"✅ 认证成功!")
        else:
            print(f"❌ 认证失败")
    
    return successful_urls

def main():
    """主函数"""
    print("🔍 RTSP地址自动发现工具")
    print("=" * 60)
    
    # 从用户的失败地址推断基础IP
    failed_url = "rtsp://192.168.3.61:8080/test.sdp"
    base_ip = "192.168.3.61"
    
    print(f"📍 基于失败地址分析: {failed_url}")
    print(f"🌐 提取IP地址: {base_ip}")
    
    # 测试无认证地址
    print(f"\n1️⃣ 测试无认证RTSP地址")
    test_rtsp_addresses(base_ip)
    
    # 测试常见认证组合
    print(f"\n2️⃣ 测试常见用户名密码组合")
    common_credentials = [
        ("admin", "admin"),
        ("admin", "123456"),
        ("admin", "password"),
        ("root", "root"),
        ("user", "user"),
    ]
    
    all_successful = []
    for username, password in common_credentials:
        successful = test_with_credentials(base_ip, username, password)
        all_successful.extend(successful)
    
    # 最终结果
    print(f"\n🎯 最终结果:")
    if all_successful:
        print(f"🎉 总共找到 {len(all_successful)} 个可用地址:")
        for i, url in enumerate(all_successful, 1):
            print(f"   {i}. {url}")
        
        print(f"\n📋 推荐测试命令:")
        best_url = all_successful[0]
        print(f"python3 simple_cli.py video {best_url}")
    else:
        print("😞 未找到可用的RTSP地址")
        print("\n💡 手动检查建议:")
        print("   • 登录摄像头web管理界面")
        print("   • 查看RTSP设置页面")
        print("   • 确认RTSP服务已启用")
        print("   • 记录正确的端口和路径")

if __name__ == "__main__":
    main()