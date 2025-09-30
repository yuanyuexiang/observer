#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版命令行工具
"""
import sys
import os

def cmd_video(source, interval=10, max_frames=None):
    """视频流检测命令"""
    try:
        from video_detector import VideoToolDetector
        
        print(f"🎥 开始视频流工具检测")
        print(f"📍 数据源: {source}")
        print(f"⏱️ 检测间隔: {interval}秒")
        if max_frames:
            print(f"🔢 最大帧数: {max_frames}")
        
        # 初始化视频检测器
        video_detector = VideoToolDetector()
        video_detector.detection_interval = interval
        
        if not video_detector.setup_detectors():
            return
        
        # 判断数据源类型并处理
        if source.isdigit():
            # 摄像头设备
            camera_id = int(source)
            video_detector.process_camera_stream(camera_id)
        elif os.path.isfile(source):
            # 视频文件
            video_detector.process_video_file(source, max_frames)
        else:
            print(f"❌ 数据源不存在: {source}")
            
    except Exception as e:
        print(f"视频检测失败: {e}")
        import traceback
        traceback.print_exc()

def show_help():
    """显示帮助信息"""
    print("""
🔧 智能工具检测系统 v2.0

📋 可用命令:
  detect <image_path>                    - 基础工具检测
  check <image_path>                     - 工具箱状态检查  
  enhanced <image_path>                  - 增强检测（检测位置错误）
  video <source> [options]               - 视频流工具检测

📱 video命令选项:
  <source>                               - 数据源：
                                          • 摄像头ID: 0, 1, 2... (实时监控)
                                          • 视频文件路径 (批量检测)
  --interval <seconds>                   - 检测间隔（默认10秒）
  --max-frames <number>                  - 最大检测帧数（仅视频文件）

💡 使用示例:
  python simple_cli.py detect test.jpg                    # 检测图片中的工具
  python simple_cli.py check test2.jpg                    # 检查工具箱状态
  python simple_cli.py enhanced test3.jpg                 # 检测工具位置错误
  python simple_cli.py video 0                            # 实时监控摄像头0
  python simple_cli.py video 0 --interval 5               # 每5秒检测一次
  python simple_cli.py video video.mp4                    # 检测视频文件
  python simple_cli.py video video.mp4 --max-frames 5     # 最多检测5帧

🎥 视频检测特性:
  • 实时摄像头监控 - 按 'q' 退出，按 'd' 手动检测
  • 视频文件批量处理 - 按时间间隔自动检测
  • 专业报告生成 - 每次检测都生成完整报告
  • 智能帧采样 - 避免重复检测相似帧
    """)

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
            
            # 创建改进的标注图片
            try:
                from improved_annotator import ImprovedAnnotator
                annotator = ImprovedAnnotator()
                output_path = annotator.annotate_detection(
                    image_path, 
                    best_tool['tool'], 
                    best_tool['score']
                )
                if output_path:
                    print(f"📸 已生成检测结果图片: {output_path}")
            except Exception as e:
                print(f"⚠️ 图片标注失败: {e}")
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
        
        # 创建专业的工具箱状态标注图片
        try:
            from professional_annotator import ProfessionalToolboxAnnotator
            annotator = ProfessionalToolboxAnnotator()
            output_path = annotator.create_professional_status_report(
                image_path, 
                results,
                analysis['completeness_rate']
            )
            if output_path:
                print(f"📸 已生成专业工具箱状态报告: {output_path}")
        except Exception as e:
            print(f"⚠️ 图片标注失败: {e}")
            # 备用方案：使用原来的简单标注
            try:
                from improved_annotator import ImprovedAnnotator
                backup_annotator = ImprovedAnnotator()
                backup_output = backup_annotator.annotate_toolbox_status(
                    image_path, 
                    present_tools, 
                    missing_tools,
                    analysis['completeness_rate']
                )
                if backup_output:
                    print(f"📸 已生成工具箱状态图片: {backup_output}")
            except Exception as backup_e:
                print(f"⚠️ 备用标注也失败: {backup_e}")
        
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
        
        # 创建增强标注图片
        try:
            from enhanced_annotator import EnhancedAnnotator
            import json
            
            # 加载工作空间配置
            with open('instances_default.json', 'r') as f:
                data = json.load(f)
            workspace_config = []
            categories = {cat['id']: cat['name'] for cat in data['categories']}
            for ann in data['annotations']:
                workspace_config.append({
                    'name': categories[ann['category_id']],
                    'bbox': ann['bbox']
                })
            
            annotator = EnhancedAnnotator()
            output_path = annotator.create_enhanced_annotation(image_path, results, workspace_config)
            if output_path:
                print(f"📸 已生成增强检测可视化图片: {output_path}")
                
        except Exception as e:
            print(f"⚠️ 图片标注失败: {e}")
        
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
    
    elif command == "video":
        if len(sys.argv) < 3:
            print("错误: 请提供数据源")
            print("用法: python simple_cli.py video <source> [--interval <seconds>] [--max-frames <number>]")
            return
        
        source = sys.argv[2]
        interval = 10
        max_frames = None
        
        # 解析可选参数
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == '--interval' and i + 1 < len(sys.argv):
                try:
                    interval = int(sys.argv[i + 1])
                    i += 2
                except ValueError:
                    print("错误: interval 必须是整数")
                    return
            elif sys.argv[i] == '--max-frames' and i + 1 < len(sys.argv):
                try:
                    max_frames = int(sys.argv[i + 1])
                    i += 2
                except ValueError:
                    print("错误: max-frames 必须是整数")
                    return
            else:
                print(f"未知参数: {sys.argv[i]}")
                return
        
        cmd_video(source, interval, max_frames)
    
    elif command in ["help", "-h", "--help"]:
        show_help()
    
    else:
        print(f"未知命令: {command}")
        show_help()

if __name__ == "__main__":
    main()