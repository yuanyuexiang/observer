#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RTSP摄像头工具检测快速启动器
"""

import subprocess
import sys

def show_menu():
    """显示选择菜单"""
    print("🎥 RTSP摄像头工具检测系统")
    print("=" * 40)
    print("📡 摄像头: 192.168.3.61:8080")
    print("")
    print("请选择RTSP流:")
    print("1. h264.sdp (主推荐)")
    print("2. h264_ulaw.sdp (带μ-law音频)")  
    print("3. h264_pcm.sdp (带PCM音频)")
    print("4. 退出")
    print("")

def get_rtsp_url(choice):
    """根据选择返回RTSP地址"""
    urls = {
        '1': 'rtsp://192.168.3.61:8080/h264.sdp',
        '2': 'rtsp://192.168.3.61:8080/h264_ulaw.sdp', 
        '3': 'rtsp://192.168.3.61:8080/h264_pcm.sdp'
    }
    return urls.get(choice)

def get_interval():
    """获取检测间隔"""
    print("🕐 请输入检测间隔（秒）:")
    print("  推荐值: 10-30秒")
    print("  回车使用默认值(10秒)")
    
    interval_input = input("检测间隔: ").strip()
    if not interval_input:
        return 10
    
    try:
        interval = int(interval_input)
        if interval < 5:
            print("⚠️ 间隔太短，使用最小值5秒")
            return 5
        elif interval > 300:
            print("⚠️ 间隔太长，使用最大值300秒")
            return 300
        return interval
    except ValueError:
        print("⚠️ 输入无效，使用默认值10秒")
        return 10

def start_detection(rtsp_url, interval):
    """启动工具检测"""
    print(f"\n🚀 启动RTSP工具检测")
    print(f"📡 RTSP地址: {rtsp_url}")
    print(f"⏱️ 检测间隔: {interval}秒")
    print(f"🎮 按 'q' 退出，按 'd' 手动检测")
    print("=" * 40)
    
    cmd = ['python3', 'simple_cli.py', 'video', rtsp_url, '--interval', str(interval)]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 用户中断")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")

def main():
    """主函数"""
    try:
        while True:
            show_menu()
            choice = input("请选择 (1-4): ").strip()
            
            if choice == '4':
                print("👋 再见!")
                break
            
            rtsp_url = get_rtsp_url(choice)
            if not rtsp_url:
                print("❌ 无效选择，请重新输入")
                continue
            
            interval = get_interval()
            start_detection(rtsp_url, interval)
            
            # 询问是否继续
            restart = input("\n🔄 是否重新启动? (y/N): ").strip().lower()
            if restart not in ['y', 'yes', '是']:
                break
                
    except KeyboardInterrupt:
        print("\n👋 用户中断，再见!")

if __name__ == "__main__":
    main()