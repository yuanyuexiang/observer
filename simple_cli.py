#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版命令行工具
"""
import sys
import os

def show_help():
    """显示帮助信息"""
    print("\n工具检测系统 - 命令行工具")
    print("=" * 40)
    print("使用方法:")
    print("  python simple_cli.py <command> [options]")
    print("\n命令:")
    print("  detect <image>        简单检测图片中的工具")
    print("  check <image>         详细检测工具箱中缺失的工具")
    print("  enhanced <image>      增强检测，包括错位工具")
    print("  help                  显示帮助信息")
    print("\n示例:")
    print("  python simple_cli.py detect test.jpg    # 简单分类")
    print("  python simple_cli.py check test.jpg     # 缺失检测")
    print("  python simple_cli.py enhanced test.jpg  # 错位检测")
    print("")

def cmd_detect(image_path):
    """检测命令"""
    if not os.path.exists(image_path):
        print(f"错误: 图片文件不存在: {image_path}")
        return
    
    print(f"开始检测图片: {image_path}")
    
    try:
        # 导入并运行简单检测器
        from simple_image_detector import SimpleImageDetector
        
        # 创建检测器实例
        detector = SimpleImageDetector()
        
        # 运行检测
        result = detector.detect_tools_in_image(image_path)
        
        if result:
            best_tool = result['best_tool']
            all_results = result['all_results']
            
            print(f"\n检测完成!")
            print(f"图片: {result['image_path']}")
            print(f"最可能的工具: {best_tool['tool'].upper()}")
            print(f"置信度: {best_tool['score']:.4f}")
            print(f"描述: {best_tool['description']}")
            
            print(f"\n完整排序结果:")
            for i, pred in enumerate(all_results, 1):
                icon = "[1]" if i == 1 else "[2]" if i == 2 else "[3]" if i == 3 else f"[{i}]"
                print(f"{icon} {pred['tool']:12} - {pred['score']:.4f} ({pred['description']})")
        else:
            print("检测失败")
        
    except Exception as e:
        print(f"检测失败: {e}")
        import traceback
        traceback.print_exc()

def cmd_check(image_path):
    """详细检测工具箱中的缺失工具"""
    if not os.path.exists(image_path):
        print(f"错误: 图片文件不存在: {image_path}")
        return
    
    print(f"开始详细检测工具箱: {image_path}")
    
    try:
        # 导入production检测器
        from production_tool_detector import ProductionToolDetector, SystemConfig
        
        config = SystemConfig(
            confidence_threshold=0.0001,
            uncertainty_threshold=-0.0001,
            save_roi_images=False,
            log_level='ERROR'
        )
        
        detector = ProductionToolDetector(config)
        workspace_config = detector.load_workspace_configuration('instances_default.json')
        results = detector.run_full_detection(image_path, workspace_config)
        
        print(f"\n=== 工具检测结果 ===")
        missing_tools = []
        present_tools = []
        
        for result in results:
            status_icon = {'present': '✅', 'missing': '❌', 'uncertain': '🤔', 'error': '⚠️'}.get(result.status, '?')
            print(f"{result.tool_name:15} {status_icon} {result.status:10} (置信度: {result.confidence:+.4f})")
            
            if result.status == 'missing':
                missing_tools.append(result.tool_name)
            elif result.status == 'present':
                present_tools.append(result.tool_name)
        
        analysis = detector.analyze_workspace_status(results)
        print(f"\n=== 工具箱状态摘要 ===")
        print(f"总工具数: {analysis['total_tools']}")
        print(f"在位工具: {analysis['present_tools']} ✅")
        print(f"缺失工具: {analysis['missing_tools']} ❌")
        print(f"完整性: {analysis['completeness_rate']:.1f}%")
        print(f"整体状态: {analysis['overall_status']}")
        
        if missing_tools:
            print(f"\n⚠️  缺失的工具:")
            for tool in missing_tools:
                print(f"   - {tool}")
        else:
            print(f"\n🎉 所有工具都在工具箱中!")
        
        if analysis.get('alerts'):
            print(f"\n🚨 警报:")
            for alert in analysis['alerts']:
                print(f"  {alert['message']}")
        
    except Exception as e:
        print(f"检测失败: {e}")
        import traceback
        traceback.print_exc()

def cmd_enhanced(image_path):
    """增强检测工具箱中的错位工具"""
    if not os.path.exists(image_path):
        print(f"错误: 图片文件不存在: {image_path}")
        return
    
    print(f"开始增强检测工具箱: {image_path}")
    
    try:
        from enhanced_detector import EnhancedToolDetector
        
        detector = EnhancedToolDetector()
        results = detector.detect_with_misplacement_check(image_path)
        
        print(f"\n=== 增强检测结果 ===")
        
        correct_count = 0
        misplaced_count = 0
        missing_count = 0
        
        for result in results:
            if result.actual_status == 'correct':
                icon = '✅'
                status_text = '在正确位置'
                correct_count += 1
            elif result.actual_status == 'misplaced':
                icon = '🔄'
                status_text = f'位置错误 (在{result.found_at}发现)'
                misplaced_count += 1
            else:
                icon = '❌'
                status_text = '检测困难/缺失'
                missing_count += 1
            
            print(f"{result.tool_name:15} {icon} {status_text}")
        
        print(f"\n=== 状态统计 ===")
        print(f"正确位置: {correct_count} ✅")
        print(f"位置错误: {misplaced_count} 🔄")
        print(f"检测困难: {missing_count} ❌")
        
        if misplaced_count > 0:
            print(f"\n💡 建议: 有 {misplaced_count} 个工具需要重新整理到正确位置")
        
    except Exception as e:
        print(f"增强检测失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "detect":
        if len(sys.argv) < 3:
            print("错误: 请提供图片路径")
            print("用法: python simple_cli.py detect <image_path>")
            return
        cmd_detect(sys.argv[2])
    
    elif command == "check":
        if len(sys.argv) < 3:
            print("错误: 请提供图片路径")
            print("用法: python simple_cli.py check <image_path>")
            return
        cmd_check(sys.argv[2])
    
    elif command == "enhanced":
        if len(sys.argv) < 3:
            print("错误: 请提供图片路径")
            print("用法: python simple_cli.py enhanced <image_path>")
            return
        cmd_enhanced(sys.argv[2])
    
    elif command in ["help", "-h", "--help"]:
        show_help()
    
    else:
        print(f"未知命令: {command}")
        show_help()

if __name__ == "__main__":
    main()