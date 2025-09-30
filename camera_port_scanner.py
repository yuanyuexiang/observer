#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
摄像头端口扫描工具
"""

import socket
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

def scan_port(ip, port, timeout=1):
    """扫描单个端口"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return port if result == 0 else None
    except:
        return None

def scan_camera_ports(ip):
    """扫描摄像头常用端口"""
    print(f"🔍 扫描摄像头 {ip} 的开放端口...")
    
    # 摄像头常用端口
    common_ports = [
        # RTSP相关
        554,    # RTSP标准端口
        8080,   # 常见RTSP端口
        8554,   # 备用RTSP端口
        1935,   # RTMP端口
        5554,   # 备用视频端口
        
        # Web管理界面
        80,     # HTTP
        443,    # HTTPS
        8081,   # 备用HTTP
        8443,   # 备用HTTPS
        81,     # 备用HTTP
        8088,   # 备用HTTP
        9090,   # 管理端口
        
        # 其他常见端口
        23,     # Telnet
        21,     # FTP
        22,     # SSH
        25,     # SMTP
        53,     # DNS
        110,    # POP3
        995,    # POP3S
        143,    # IMAP
        993,    # IMAPS
        
        # 摄像头特有端口
        37777,  # 海康威视
        8000,   # 海康威视web
        65001,  # 大华
        3702,   # ONVIF
        8899,   # 小米摄像头
        6667,   # 360摄像头
    ]
    
    open_ports = []
    
    print(f"📡 扫描 {len(common_ports)} 个常用端口...")
    
    # 使用线程池并发扫描
    with ThreadPoolExecutor(max_workers=50) as executor:
        future_to_port = {executor.submit(scan_port, ip, port): port for port in common_ports}
        
        for future in as_completed(future_to_port):
            port = future_to_port[future]
            try:
                result = future.result()
                if result:
                    open_ports.append(result)
                    print(f"✅ 端口 {result} 开放")
            except Exception as e:
                pass
    
    print(f"\n🎯 扫描结果:")
    if open_ports:
        print(f"找到 {len(open_ports)} 个开放端口:")
        
        # 分类显示端口
        rtsp_ports = [p for p in open_ports if p in [554, 8080, 8554, 1935, 5554]]
        web_ports = [p for p in open_ports if p in [80, 443, 8081, 8443, 81, 8088, 9090]]
        other_ports = [p for p in open_ports if p not in rtsp_ports + web_ports]
        
        if rtsp_ports:
            print(f"📡 RTSP/视频端口: {rtsp_ports}")
        if web_ports:
            print(f"🌐 Web管理端口: {web_ports}")
        if other_ports:
            print(f"🔧 其他端口: {other_ports}")
            
        # 生成建议的RTSP地址
        if rtsp_ports:
            print(f"\n💡 建议测试的RTSP地址:")
            for port in rtsp_ports:
                for path in ['/stream', '/live', '/video', '/h264.sdp', '/cam', '/']:
                    rtsp_url = f"rtsp://{ip}:{port}{path}"
                    print(f"   {rtsp_url}")
        
        # 生成web访问建议
        if web_ports:
            print(f"\n🌐 尝试访问web管理界面:")
            for port in web_ports:
                if port == 443 or port == 8443:
                    print(f"   https://{ip}:{port}")
                else:
                    print(f"   http://{ip}:{port}")
    else:
        print("😞 没有找到开放的端口")
        print("💡 可能的原因:")
        print("   • 摄像头处于睡眠模式")
        print("   • 防火墙阻止端口扫描")
        print("   • 摄像头使用非标准端口")

def main():
    """主函数"""
    ip = "192.168.3.61"
    print("🔍 摄像头端口扫描工具")
    print("=" * 40)
    scan_camera_ports(ip)

if __name__ == "__main__":
    main()