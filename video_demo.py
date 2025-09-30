#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频检测系统使用演示和测试脚本
"""

import os
import subprocess
import time

def test_video_detection_modes():
    """测试视频检测的各种模式"""
    print("🎥 视频流工具检测系统演示")
    print("=" * 60)
    
    print("\n✨ 新增功能特性:")
    print("   📷 实时摄像头监控 - 每10秒自动检测 + 手动触发")
    print("   🎬 视频文件批量处理 - 按时间间隔采样检测")
    print("   🖼️ 静态图片处理 - 兼容原有图片检测功能")
    print("   📊 专业报告生成 - 每次检测都生成完整的状态报告")
    
    print(f"\n{'='*60}")
    
    # 测试不同的数据源类型
    test_cases = [
        {
            'mode': '静态图片处理',
            'command': 'python simple_cli.py video test.jpg',
            'description': '将静态图片作为单帧视频处理',
            'available': os.path.exists('test.jpg')
        },
        {
            'mode': '摄像头实时监控', 
            'command': 'python simple_cli.py video 0',
            'description': '连接摄像头0进行实时监控（按q退出，按d手动检测）',
            'available': True,  # 无法提前检测摄像头是否可用
            'note': '⚠️ 需要连接摄像头设备'
        },
        {
            'mode': '自定义检测间隔',
            'command': 'python simple_cli.py video 0 --interval 5',
            'description': '每5秒进行一次自动检测',
            'available': True,
            'note': '⚠️ 需要连接摄像头设备'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📱 测试模式 {i}: {test_case['mode']}")
        print(f"   命令: {test_case['command']}")
        print(f"   说明: {test_case['description']}")
        
        if not test_case['available']:
            print("   ❌ 跳过：所需文件不存在")
            continue
            
        if test_case.get('note'):
            print(f"   {test_case['note']}")
        
        # 只演示静态图片模式，摄像头模式需要用户手动测试
        if 'test.jpg' in test_case['command']:
            print(f"   ▶️ 执行演示...")
            
            try:
                result = subprocess.run(
                    test_case['command'].split(),
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    # 显示关键输出信息
                    lines = result.stdout.split('\n')
                    key_info = []
                    
                    for line in lines:
                        if any(keyword in line for keyword in [
                            '完整性', '在位工具', '缺失工具', '生成专业检测报告', '总计检测了'
                        ]):
                            key_info.append(f"     {line.strip()}")
                    
                    if key_info:
                        print("   ✅ 执行成功：")
                        print('\n'.join(key_info))
                    else:
                        print("   ✅ 执行成功")
                else:
                    print(f"   ❌ 执行失败：{result.stderr.strip()}")
                    
            except subprocess.TimeoutExpired:
                print("   ⏰ 执行超时")
            except Exception as e:
                print(f"   ❌ 执行错误：{e}")
        else:
            print("   💡 摄像头模式需要手动测试")
    
    print(f"\n{'='*60}")
    print("🎯 视频检测系统特点总结：")
    print()
    print("📊 数据源支持：")
    print("   • 静态图片 (.jpg, .png, .bmp 等)")
    print("   • 视频文件 (.mp4, .avi, .mov 等)")  
    print("   • 实时摄像头 (USB摄像头, 内置摄像头)")
    print()
    print("⚙️ 检测配置：")
    print("   • 可调节检测间隔 (默认10秒)")
    print("   • 视频文件最大帧数限制")
    print("   • 实时手动检测触发")
    print()
    print("📋 输出报告：")
    print("   • 专业状态报告图片")
    print("   • 竖直列表布局")
    print("   • 状态颜色编码")
    print("   • 完整性进度条")
    print()
    print("🎮 操作控制：")
    print("   • 实时模式：按 'q' 退出，按 'd' 手动检测")
    print("   • 批量模式：自动按间隔检测")
    print("   • 智能采样：避免重复检测相似帧")
    
    print(f"\n{'='*60}")
    print("💡 使用建议：")
    print()
    print("🔧 工业应用场景：")
    print("   • 生产线实时监控：python simple_cli.py video 0 --interval 30")
    print("   • 质量检查记录：python simple_cli.py video inspection.mp4")
    print("   • 班次交接检查：python simple_cli.py video test.jpg")
    print()
    print("📱 测试和调试：")
    print("   • 快速检测：python simple_cli.py video 0 --interval 5")
    print("   • 批量验证：python simple_cli.py video video.mp4 --max-frames 10")
    print("   • 单次检查：python simple_cli.py check test.jpg")

if __name__ == "__main__":
    try:
        test_video_detection_modes()
    except KeyboardInterrupt:
        print("\n\n👋 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")