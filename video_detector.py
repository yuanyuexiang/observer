#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频流工具检测器 - 支持视频文件和实时摄像头检测
"""

import cv2
import os
import time
import threading
from datetime import datetime
from types import SimpleNamespace
import json

class VideoToolDetector:
    """视频流工具检测器"""
    
    def __init__(self):
        self.is_running = False
        self.detection_interval = 10  # 检测间隔（秒）
        self.frame_count = 0
        self.last_detection_time = 0
        
    def setup_detectors(self):
        """初始化检测器组件"""
        try:
            from production_tool_detector import ProductionToolDetector
            from professional_annotator import ProfessionalToolboxAnnotator
            
            # 使用与simple_cli相同的配置方式
            import logging
            
            class Config:
                def __init__(self):
                    self.model_name = 'ViT-B-32'
                    self.clip_model = 'ViT-B-32'
                    self.clip_pretrained = 'openai'
                    self.device = 'cpu'
                    self.confidence_threshold = 0.0
                    self.log_level = 'ERROR'
                    self.save_roi_images = True
                    self.output_dir = '.'
            
            config = Config()
            
            self.detector = ProductionToolDetector(config)
            self.annotator = ProfessionalToolboxAnnotator()
            self.workspace_config = self.detector.load_workspace_configuration('instances_default.json')
            
            print("✅ 检测器初始化完成")
            return True
            
        except Exception as e:
            print(f"❌ 检测器初始化失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def save_frame(self, frame, prefix="frame"):
        """保存视频帧为图片"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.jpg"
        cv2.imwrite(filename, frame)
        return filename
    
    def detect_frame(self, frame, frame_source="video"):
        """对单帧进行工具检测"""
        try:
            # 保存帧为临时图片
            temp_image = self.save_frame(frame, f"temp_{frame_source}")
            
            print(f"\n🔍 开始检测帧: {temp_image}")
            print(f"📅 检测时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 运行工具检测
            results = self.detector.run_full_detection(temp_image, self.workspace_config)
            analysis = self.detector.analyze_workspace_status(results)
            
            # 显示检测结果
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
            
            # 生成专业报告
            try:
                output_path = self.annotator.create_professional_status_report(
                    temp_image, results, analysis['completeness_rate']
                )
                if output_path:
                    print(f"📸 已生成专业检测报告: {output_path}")
            except Exception as e:
                print(f"⚠️ 报告生成失败: {e}")
            
            # 清理临时文件
            if os.path.exists(temp_image):
                os.remove(temp_image)
                
            return analysis
            
        except Exception as e:
            print(f"❌ 帧检测失败: {e}")
            return None
    
    def process_video_file(self, video_path, max_frames=None):
        """处理视频文件"""
        if not os.path.exists(video_path):
            print(f"❌ 视频文件不存在: {video_path}")
            return
        
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            print(f"❌ 无法打开视频文件: {video_path}")
            return
        
        # 获取视频信息
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        
        print(f"\n📹 开始处理视频文件: {video_path}")
        print(f"📊 视频信息: {frame_count} 帧, {fps:.2f} FPS, {duration:.2f} 秒")
        print(f"🔍 检测间隔: 每 {self.detection_interval} 秒")
        
        detection_count = 0
        processed_frames = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                current_time = processed_frames / fps if fps > 0 else 0
                
                # 每10秒检测一次
                if current_time >= detection_count * self.detection_interval:
                    print(f"\n{'='*50}")
                    print(f"📍 检测点 {detection_count + 1}: {current_time:.1f}秒")
                    
                    analysis = self.detect_frame(frame, f"video_{detection_count+1}")
                    if analysis:
                        detection_count += 1
                        
                        # 如果设置了最大帧数限制
                        if max_frames and detection_count >= max_frames:
                            print(f"\n🏁 达到最大检测帧数限制: {max_frames}")
                            break
                
                processed_frames += 1
                
                # 显示进度
                if processed_frames % 100 == 0:
                    progress = (processed_frames / frame_count) * 100 if frame_count > 0 else 0
                    print(f"📈 处理进度: {progress:.1f}% ({processed_frames}/{frame_count})")
        
        finally:
            cap.release()
            print(f"\n🎉 视频处理完成!")
            print(f"📊 总计检测了 {detection_count} 个时间点")
    
    def process_camera_stream(self, camera_id=0):
        """处理摄像头实时流"""
        cap = cv2.VideoCapture(camera_id)
        
        if not cap.isOpened():
            print(f"❌ 无法打开摄像头设备: {camera_id}")
            return
        
        print(f"\n📷 开始实时监控摄像头: {camera_id}")
        print(f"🔍 检测间隔: 每 {self.detection_interval} 秒")
        print(f"🚪 按 'q' 键退出，按 'd' 键立即检测")
        
        self.is_running = True
        detection_count = 0
        
        try:
            while self.is_running:
                ret, frame = cap.read()
                if not ret:
                    print("❌ 无法读取摄像头帧")
                    break
                
                # 显示实时画面
                cv2.imshow('工具检测实时监控', frame)
                
                current_time = time.time()
                
                # 定时检测或手动触发检测
                should_detect = (current_time - self.last_detection_time >= self.detection_interval)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\n👋 用户主动退出")
                    break
                elif key == ord('d'):
                    should_detect = True
                    print("\n🔍 手动触发检测")
                
                if should_detect:
                    detection_count += 1
                    print(f"\n{'='*50}")
                    print(f"📍 实时检测 {detection_count}")
                    
                    analysis = self.detect_frame(frame, f"camera_{detection_count}")
                    self.last_detection_time = current_time
                    
                    # 在窗口标题显示最新状态
                    if analysis:
                        completeness = analysis['completeness_rate']
                        window_title = f"工具检测实时监控 - 完整性: {completeness:.1f}%"
                        cv2.setWindowTitle('工具检测实时监控', window_title)
        
        finally:
            self.is_running = False
            cap.release()
            cv2.destroyAllWindows()
            print(f"\n🎉 实时监控结束!")
            print(f"📊 总计进行了 {detection_count} 次检测")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="视频流工具检测器")
    parser.add_argument('source', help='数据源: 图片路径、视频文件路径，或摄像头ID(0,1,2...)')
    parser.add_argument('--interval', type=int, default=10, help='检测间隔（秒，默认10秒）')
    parser.add_argument('--max-frames', type=int, help='最大检测帧数（仅用于视频文件）')
    
    args = parser.parse_args()
    
    # 初始化检测器
    video_detector = VideoToolDetector()
    video_detector.detection_interval = args.interval
    
    if not video_detector.setup_detectors():
        return
    
    source = args.source
    
    # 判断数据源类型
    if source.isdigit():
        # 摄像头设备
        camera_id = int(source)
        print(f"🎥 检测模式: 实时摄像头 (设备ID: {camera_id})")
        video_detector.process_camera_stream(camera_id)
    
    elif os.path.isfile(source):
        # 检查是否为视频文件
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        
        file_ext = os.path.splitext(source)[1].lower()
        
        if file_ext in video_extensions:
            print(f"🎬 检测模式: 视频文件")
            video_detector.process_video_file(source, args.max_frames)
        elif file_ext in image_extensions:
            print(f"🖼️ 检测模式: 静态图片")
            # 对单张图片进行检测
            frame = cv2.imread(source)
            if frame is not None:
                video_detector.detect_frame(frame, "image")
            else:
                print(f"❌ 无法读取图片: {source}")
        else:
            print(f"❌ 不支持的文件格式: {file_ext}")
    
    else:
        print(f"❌ 数据源不存在: {source}")

if __name__ == "__main__":
    main()