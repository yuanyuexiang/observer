#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专业工具箱标注演示脚本
展示新的竖直列表报告和彩色状态边框功能
"""

import os
import subprocess
import time

def show_professional_annotation_demo():
    """展示专业标注功能"""
    print("🎨 专业工具箱状态报告演示")
    print("=" * 60)
    print()
    print("✨ 新功能特点:")
    print("   📋 竖直列表布局 - 更清晰的工具状态展示")
    print("   🎨 状态颜色编码:")
    print("      ✅ 绿色 - 工具在位")  
    print("      ❌ 红色 - 工具缺失")
    print("      ⚠️  黄色 - 检测不确定")
    print("      🔧 橙色 - 检测错误")
    print("   📊 完整性进度条")
    print("   🖼️  保持原图完整 - 避免定位错误问题")
    print("   📄 专业报告面板")
    print()
    print("-" * 60)
    
    # 测试图片和预期结果
    test_cases = [
        {
            'image': 'test.jpg',
            'description': '完美工具箱 (100%完整性)',
            'expected': '✅ 所有工具都在正确位置'
        },
        {
            'image': 'test2.jpg', 
            'description': '有缺失工具的工具箱 (77.8%完整性)',
            'expected': '❌ 缺失十字螺丝刀，🤔 螺丝盒检测不确定'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        image_path = test_case['image']
        
        if not os.path.exists(image_path):
            print(f"⚠️  跳过 {image_path} - 文件不存在")
            continue
            
        print(f"\n📸 测试 {i}: {test_case['description']}")
        print(f"   图片: {image_path}")
        print(f"   预期: {test_case['expected']}")
        print()
        
        # 运行专业检测
        try:
            cmd = ['python', 'simple_cli.py', 'check', image_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # 提取关键信息
                lines = result.stdout.split('\n')
                
                # 查找状态摘要
                for line in lines:
                    if any(keyword in line for keyword in ['在位工具', '缺失工具', '完整性', '生成专业']):
                        print(f"   {line.strip()}")
                
                # 查找生成的文件
                output_file = f"{os.path.splitext(image_path)[0]}_professional_status.jpg"
                if os.path.exists(output_file):
                    file_size = os.path.getsize(output_file)
                    print(f"   📄 生成报告: {output_file} ({file_size:,} bytes)")
                    
                    # 显示特点说明
                    if 'test.jpg' in image_path:
                        print("   🎨 报告特点: 全绿色列表，100%进度条，保持原图完整")
                    elif 'test2.jpg' in image_path:
                        print("   🎨 报告特点: 红色缺失项，黄色不确定项，77.8%进度条，保持原图完整")
                        
                else:
                    print("   ❌ 报告文件未找到")
                    
            else:
                print(f"   ❌ 检测失败: {result.stderr.strip()}")
                
        except subprocess.TimeoutExpired:
            print("   ⏰ 检测超时")
        except Exception as e:
            print(f"   ❌ 运行错误: {e}")
        
        if i < len(test_cases):
            print("\n" + "-" * 40)
            input("按回车键继续下一个测试...")
    
    print("\n" + "=" * 60)
    print("🎉 专业标注演示完成！")
    print()
    print("📋 改进总结:")
    print("   ✅ 从横向文本改为竖直列表布局")
    print("   ✅ 添加状态颜色编码 (绿/红/黄/橙)")
    print("   ✅ 保持原图完整，避免定位错误")
    print("   ✅ 添加完整性进度条可视化")
    print("   ✅ 专业报告面板设计")
    print("   ✅ 统一使用中文工具名称")
    print("   ✅ 适应各种图片方向和拍摄角度")
    print()
    print("💡 使用方法:")
    print("   python simple_cli.py check <图片路径>")
    print("   生成的专业报告文件名: <原文件名>_professional_status.jpg")

if __name__ == "__main__":
    try:
        show_professional_annotation_demo()
    except KeyboardInterrupt:
        print("\n\n👋 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")