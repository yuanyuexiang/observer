#!/usr/bin/env python3
"""
视频流工具检测系统
支持摄像头实时检测和视频文件检测
"""
import cv2
import time
import json
import threading
from datetime import datetime
from pathlib import Path
from production_tool_detector import ProductionToolDetector, SystemConfig
import numpy as np

class VideoStreamDetector:
    """视频流工具检测器"""
    
    def __init__(self, config: SystemConfig, detection_interval=2.0):
        """
        初始化视频流检测器
        
        Args:
            config: 系统配置
            detection_interval: 检测间隔（秒）
        """
        self.detector = ProductionToolDetector(config)
        self.detection_interval = detection_interval
        self.last_detection_time = 0
        self.last_results = None
        self.is_detecting = False
        
        # 加载工作空间配置
        workspace_config_path = Path("instances_default.json")
        if workspace_config_path.exists():
            # 使用detector的方法来正确解析COCO格式
            self.workspace_config = self.detector.load_workspace_configuration("instances_default.json")
        else:
            raise FileNotFoundError("工作空间配置文件 instances_default.json 未找到")
    
    def detect_frame_async(self, frame):
        """异步检测帧"""
        if self.is_detecting:
            return
            
        current_time = time.time()
        if current_time - self.last_detection_time < self.detection_interval:
            return
            
        self.is_detecting = True
        self.last_detection_time = current_time
        
        # 在后台线程中运行检测
        detection_thread = threading.Thread(
            target=self._detect_frame_worker,
            args=(frame.copy(),)
        )
        detection_thread.daemon = True
        detection_thread.start()
    
    def _detect_frame_worker(self, frame):
        """检测工作线程"""
        try:
            # 保存临时图片
            temp_path = "temp_frame.jpg"
            cv2.imwrite(temp_path, frame)
            
            # 运行检测
            results = self.detector.run_full_detection(temp_path, self.workspace_config)
            self.last_results = results
            
            # 清理临时文件
            Path(temp_path).unlink(missing_ok=True)
            
        except Exception as e:
            print(f"❌ 检测错误: {e}")
        finally:
            self.is_detecting = False
    
    def draw_results_overlay(self, frame):
        """在帧上绘制检测结果覆盖层"""
        if not self.last_results:
            return frame
            
        height, width = frame.shape[:2]
        overlay = frame.copy()
        
        # 首先绘制所有工具的检测框
        for result in self.last_results:
            if hasattr(result, 'bbox') and result.bbox and len(result.bbox) >= 4:
                # 获取bbox坐标 [x, y, width, height]
                x, y, w, h = result.bbox
                x1, y1 = int(x), int(y)
                x2, y2 = int(x + w), int(y + h)
                
                # 根据检测状态选择颜色
                if result.status == "present":
                    bbox_color = (0, 255, 0)  # 绿色
                    text_bg_color = (0, 200, 0)
                elif result.status == "missing":
                    bbox_color = (0, 0, 255)  # 红色
                    text_bg_color = (0, 0, 200)
                else:  # uncertain
                    bbox_color = (0, 255, 255)  # 黄色
                    text_bg_color = (0, 200, 200)
                
                # 绘制检测框
                cv2.rectangle(overlay, (x1, y1), (x2, y2), bbox_color, 3)
                
                # 绘制工具名称背景
                tool_text = f"{result.tool_name}"
                text_size = cv2.getTextSize(tool_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                cv2.rectangle(overlay, (x1, y1 - 30), (x1 + text_size[0] + 10, y1), text_bg_color, -1)
                
                # 绘制工具名称
                cv2.putText(overlay, tool_text, (x1 + 5, y1 - 8), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # 绘制置信度（在框的右下角）
                conf_text = f"{result.confidence:+.3f}"
                conf_size = cv2.getTextSize(conf_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
                cv2.rectangle(overlay, (x2 - conf_size[0] - 10, y2), (x2, y2 + 20), text_bg_color, -1)
                cv2.putText(overlay, conf_text, (x2 - conf_size[0] - 5, y2 + 15), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # 创建半透明背景
        result_bg = np.zeros((height, width, 3), dtype=np.uint8)
        
        # 统计信息
        present_count = sum(1 for r in self.last_results if r.status == "present")
        missing_count = sum(1 for r in self.last_results if r.status == "missing")
        uncertain_count = sum(1 for r in self.last_results if r.status == "uncertain")
        total_count = len(self.last_results)
        
        # 绘制状态栏
        status_height = 200
        cv2.rectangle(result_bg, (0, 0), (width, status_height), (50, 50, 50), -1)
        
        # 标题
        cv2.putText(overlay, "Tool Detection System", (20, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # 统计信息
        stats_text = f"Total: {total_count} | Present: {present_count} | Missing: {missing_count} | Uncertain: {uncertain_count}"
        cv2.putText(overlay, stats_text, (20, 65), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # 完整性百分比
        completeness = (present_count / total_count * 100) if total_count > 0 else 0
        completeness_text = f"Completeness: {completeness:.1f}%"
        color = (0, 255, 0) if completeness >= 90 else (0, 255, 255) if completeness >= 70 else (0, 0, 255)
        cv2.putText(overlay, completeness_text, (20, 95), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        # 详细工具状态
        y_offset = 130
        for i, result in enumerate(self.last_results):
            if i >= 8:  # 最多显示8个工具
                break
                
            status_icon = "✓" if result.status == "present" else "✗" if result.status == "missing" else "?"
            status_color = (0, 255, 0) if result.status == "present" else (0, 0, 255) if result.status == "missing" else (0, 255, 255)
            
            tool_text = f"{status_icon} {result.tool_name}"
            cv2.putText(overlay, tool_text, (20, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 1)
            y_offset += 20
        
        # 混合覆盖层
        cv2.addWeighted(overlay, 0.8, result_bg, 0.3, 0, overlay)
        
        # 添加检测状态指示器
        if self.is_detecting:
            cv2.circle(overlay, (width - 30, 30), 10, (0, 255, 255), -1)  # 黄色：检测中
        else:
            cv2.circle(overlay, (width - 30, 30), 10, (0, 255, 0), -1)   # 绿色：就绪
        
        return overlay
    
    def run_camera_detection(self, camera_id=0):
        """运行摄像头检测"""
        print(f"🎥 启动摄像头检测 (设备ID: {camera_id})")
        print("按 'q' 退出, 按 's' 保存当前帧, 按 'r' 手动触发检测")
        
        cap = cv2.VideoCapture(camera_id)
        if not cap.isOpened():
            print(f"❌ 无法打开摄像头 {camera_id}")
            return
        
        # 设置摄像头参数
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ 无法读取摄像头画面")
                break
            
            # 异步检测
            self.detect_frame_async(frame)
            
            # 绘制结果覆盖层
            display_frame = self.draw_results_overlay(frame)
            
            # 显示画面
            cv2.imshow('Tool Detection - Real Time', display_frame)
            
            # 处理按键
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # 保存当前帧
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"capture_{timestamp}.jpg"
                cv2.imwrite(filename, frame)
                print(f"📸 已保存: {filename}")
            elif key == ord('r'):
                # 手动触发检测
                self.last_detection_time = 0
                print("🔄 手动触发检测...")
        
        cap.release()
        cv2.destroyAllWindows()
        print("🎥 摄像头检测已停止")
    
    def run_video_file_detection(self, video_path):
        """运行视频文件检测"""
        print(f"🎬 启动视频文件检测: {video_path}")
        
        if not Path(video_path).exists():
            print(f"❌ 视频文件不存在: {video_path}")
            return
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"❌ 无法打开视频文件: {video_path}")
            return
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        print(f"视频信息: {total_frames} 帧, {fps:.2f} FPS")
        print("按 'q' 退出, 按 's' 保存当前帧, 按空格暂停/继续")
        
        frame_count = 0
        paused = False
        
        while True:
            if not paused:
                ret, frame = cap.read()
                if not ret:
                    print("🎬 视频播放完毕")
                    break
                frame_count += 1
            
            # 异步检测
            if not paused:
                self.detect_frame_async(frame)
            
            # 绘制结果覆盖层
            display_frame = self.draw_results_overlay(frame)
            
            # 添加进度条
            progress = frame_count / total_frames
            bar_width = display_frame.shape[1] - 40
            cv2.rectangle(display_frame, (20, display_frame.shape[0] - 30), 
                         (20 + int(bar_width * progress), display_frame.shape[0] - 20), 
                         (0, 255, 0), -1)
            
            # 显示画面
            cv2.imshow('Tool Detection - Video File', display_frame)
            
            # 控制播放速度
            delay = int(1000 / fps) if fps > 0 else 33
            key = cv2.waitKey(delay) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('s'):
                # 保存当前帧
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"video_frame_{frame_count}_{timestamp}.jpg"
                cv2.imwrite(filename, frame)
                print(f"📸 已保存: {filename}")
            elif key == ord(' '):
                paused = not paused
                print(f"⏸️ {'暂停' if paused else '继续'}")
        
        cap.release()
        cv2.destroyAllWindows()
        print("🎬 视频检测已停止")

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("""
🎥 视频流工具检测系统

使用方法:
  python video_stream_detector.py camera [camera_id]     # 摄像头检测 (默认ID=0)
  python video_stream_detector.py video <video_path>     # 视频文件检测

控制键:
  q - 退出
  s - 保存当前帧
  r - 手动触发检测 (仅摄像头模式)
  空格 - 暂停/继续 (仅视频文件模式)

示例:
  python video_stream_detector.py camera 0
  python video_stream_detector.py video sample_video.mp4
        """)
        return
    
    command = sys.argv[1].lower()
    
    # 配置检测系统
    config = SystemConfig(
        confidence_threshold=0.0005,
        uncertainty_threshold=-0.0001,
        save_roi_images=False,
        log_level="ERROR"  # 减少控制台输出
    )
    
    detector = VideoStreamDetector(config, detection_interval=1.5)  # 1.5秒检测间隔
    
    try:
        if command == "camera":
            camera_id = int(sys.argv[2]) if len(sys.argv) > 2 else 0
            detector.run_camera_detection(camera_id)
        elif command == "video":
            if len(sys.argv) < 3:
                print("❌ 请提供视频文件路径")
                return
            video_path = sys.argv[2]
            detector.run_video_file_detection(video_path)
        else:
            print(f"❌ 未知命令: {command}")
            
    except KeyboardInterrupt:
        print("\n👋 用户中断，退出系统")
    except Exception as e:
        print(f"❌ 运行错误: {e}")

if __name__ == "__main__":
    main()