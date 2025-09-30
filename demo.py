#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具检测系统演示脚本
展示所有三种检测模式的功能
"""

import os
import sys
import subprocess
import time

def run_demo():
    """运行完整演示"""
    print("🔧 工具检测系统演示")
    print("=" * 50)
    
    # 检查测试图片是否存在
    test_images = ['test.jpg', 'test2.jpg', 'test3.jpg']
    available_images = [img for img in test_images if os.path.exists(img)]
    
    if not available_images:
        print("❌ 错误：没有找到测试图片")
        return
    
    print(f"📸 找到测试图片: {', '.join(available_images)}")
    print()
    
    # 演示每种模式
    modes = [
        ('detect', '基础检测模式', '识别图片中的主要工具类型'),
        ('check', '工具箱状态检查', '检查所有工具是否在指定位置'),
        ('enhanced', '增强检测模式', '发现放错位置的工具')
    ]
    
    for mode, title, description in modes:
        print(f"🔍 {title}")
        print(f"   {description}")
        print("-" * 30)
        
        for image in available_images:
            print(f"\n▶️  处理图片: {image}")
            
            try:
                # 运行检测命令
                cmd = ['python', 'simple_cli.py', mode, image]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    # 简化输出，只显示关键信息
                    output_lines = result.stdout.split('\n')
                    key_lines = []
                    
                    for line in output_lines:
                        if any(keyword in line for keyword in ['检测结果', '置信度', '完整性', '建议', '生成', '位置错误', '缺失工具']):
                            key_lines.append(f"   {line.strip()}")
                    
                    if key_lines:
                        print("\n".join(key_lines))
                    else:
                        print("   ✅ 检测完成")
                        
                else:
                    print(f"   ❌ 检测失败: {result.stderr.strip()}")
                    
            except subprocess.TimeoutExpired:
                print("   ⏰ 检测超时")
            except Exception as e:
                print(f"   ❌ 运行错误: {e}")
            
            time.sleep(1)  # 短暂延迟
        
        print("\n" + "=" * 50)
        input("按回车键继续下一个模式...")
        print()
    
    # 显示生成的文件
    print("📁 生成的文件:")
    print("-" * 20)
    
    output_files = []
    for pattern in ['*_detected.jpg', '*_status.jpg', '*_enhanced*.jpg']:
        try:
            result = subprocess.run(['ls', pattern], capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                output_files.extend(result.stdout.strip().split('\n'))
        except:
            pass
    
    if output_files:
        for file in sorted(set(output_files)):
            if file.strip():
                size = os.path.getsize(file.strip()) if os.path.exists(file.strip()) else 0
                print(f"   📄 {file.strip()} ({size:,} bytes)")
    else:
        print("   (没有找到输出文件)")
    
    print("\n🎉 演示完成！")
    print("\n💡 提示:")
    print("   - 查看生成的图片文件了解检测结果")
    print("   - 使用 'python simple_cli.py <mode> <image>' 进行单独检测")
    print("   - 阅读 '系统说明.md' 了解详细使用方法")

if __name__ == "__main__":
    # 检查是否在正确的目录
    if not os.path.exists('simple_cli.py'):
        print("❌ 错误：请在包含 simple_cli.py 的目录中运行此脚本")
        sys.exit(1)
    
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n\n👋 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")