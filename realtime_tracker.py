#!/usr/bin/env python3
"""
实时工具跟踪检测系统
支持动态目标跟踪和实时检测框渲染
"""
import cv2
import time
import json
import threading
from datetime import datetime
from pathlib import Path
from production_tool_detector import ProductionToolDetector, SystemConfig
import numpy as np
import torch
from PIL import Image
import open_clip

class RealTimeTracker:
    """实时工具跟踪器"""
    
    def __init__(self, config: SystemConfig, detection_interval=1.0):
        """
        初始化实时跟踪器
        
        Args:
            config: 系统配置
            detection_interval: 检测间隔（秒）
        """
        self.config = config
        self.detection_interval = detection_interval
        self.last_detection_time = 0
        self.detected_objects = []  # 存储检测到的对象位置和状态
        self.is_detecting = False
        
        # 初始化CLIP模型
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            config.model_name, pretrained="openai"
        )
        self.model = self.model.to(self.device)
        self.tokenizer = open_clip.get_tokenizer(config.model_name)
        
        # 工具类别和模板
        self.tool_categories = [
            "hammer", "pliers", "wrench", "flat_screwdriver", 
            "cross_screwdriver", "cutter", "tape_measure", "hex_key_set", "screw_box"
        ]
        
        # 为每个工具创建文本模板
        self.tool_templates = {}
        for tool in self.tool_categories:
            self.tool_templates[tool] = {
                "positive": [tool, f"a {tool}", f"{tool} tool"],
                "negative": ["empty space", "background", "nothing", "absent"]
            }
    
    def sliding_window_detection(self, frame, window_size=200, stride=100):
        """使用滑动窗口在帧中检测工具"""
        height, width = frame.shape[:2]
        detections = []
        
        # 转换为PIL图像
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        for y in range(0, height - window_size, stride):
            for x in range(0, width - window_size, stride):
                # 提取窗口
                window = frame_rgb[y:y+window_size, x:x+window_size]
                window_pil = Image.fromarray(window)
                
                # 预处理
                image_input = self.preprocess(window_pil).unsqueeze(0).to(self.device)
                
                # 对每个工具类别进行检测
                best_tool = None
                best_confidence = -1.0
                
                for tool_name in self.tool_categories:
                    templates = self.tool_templates[tool_name]
                    all_texts = templates["positive"] + templates["negative"]
                    text_tokens = self.tokenizer(all_texts).to(self.device)
                    
                    with torch.no_grad():
                        image_features = self.model.encode_image(image_input)
                        text_features = self.model.encode_text(text_tokens)
                        
                        # 归一化
                        image_features = image_features / image_features.norm(dim=-1, keepdim=True)
                        text_features = text_features / text_features.norm(dim=-1, keepdim=True)
                        
                        # 计算相似度
                        similarities = (image_features @ text_features.T).softmax(dim=-1)
                        
                        # 分析结果
                        pos_count = len(templates["positive"])
                        positive_scores = similarities[0][:pos_count]
                        negative_scores = similarities[0][pos_count:]
                        
                        avg_positive = positive_scores.mean().item()
                        avg_negative = negative_scores.mean().item()
                        confidence = avg_positive - avg_negative
                        
                        # 只保留高置信度的检测
                        if confidence > self.config.confidence_threshold and confidence > best_confidence:
                            best_confidence = confidence
                            best_tool = tool_name
                
                # 如果检测到工具，记录位置
                if best_tool and best_confidence > 0.002:  # 提高阈值避免误检
                    detections.append({
                        'tool_name': best_tool,
                        'confidence': best_confidence,
                        'bbox': [x, y, window_size, window_size],
                        'center': [x + window_size//2, y + window_size//2]
                    })
        
        return detections
    
    def non_max_suppression(self, detections, iou_threshold=0.3):
        """非极大值抑制，去除重叠的检测框"""
        if not detections:
            return []
        
        # 按置信度排序
        detections = sorted(detections, key=lambda x: x['confidence'], reverse=True)
        
        final_detections = []
        for detection in detections:
            bbox1 = detection['bbox']
            should_keep = True
            
            for kept_detection in final_detections:
                bbox2 = kept_detection['bbox']
                
                # 计算IoU
                x1_inter = max(bbox1[0], bbox2[0])
                y1_inter = max(bbox1[1], bbox2[1])
                x2_inter = min(bbox1[0] + bbox1[2], bbox2[0] + bbox2[2])
                y2_inter = min(bbox1[1] + bbox1[3], bbox2[1] + bbox2[3])
                
                if x2_inter > x1_inter and y2_inter > y1_inter:
                    intersection = (x2_inter - x1_inter) * (y2_inter - y1_inter)
                    area1 = bbox1[2] * bbox1[3]
                    area2 = bbox2[2] * bbox2[3]
                    union = area1 + area2 - intersection
                    
                    if intersection / union > iou_threshold:
                        should_keep = False
                        break
            
            if should_keep:
                final_detections.append(detection)
        
        return final_detections
    
    def detect_frame_async(self, frame):
        """异步检测帧中的工具"""
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
            # 缩放帧以提高检测速度
            scale_factor = 0.5
            small_frame = cv2.resize(frame, None, fx=scale_factor, fy=scale_factor)
            
            # 滑动窗口检测
            detections = self.sliding_window_detection(small_frame, window_size=100, stride=50)
            
            # 将坐标缩放回原始尺寸
            for det in detections:
                det['bbox'] = [int(x / scale_factor) for x in det['bbox']]
                det['center'] = [int(x / scale_factor) for x in det['center']]
            
            # 非极大值抑制
            self.detected_objects = self.non_max_suppression(detections, iou_threshold=0.3)
            
        except Exception as e:
            print(f"❌ 检测错误: {e}")
        finally:
            self.is_detecting = False
    
    def draw_tracking_overlay(self, frame):
        """绘制跟踪覆盖层"""
        overlay = frame.copy()
        height, width = frame.shape[:2]
        
        # 绘制检测到的工具
        for detection in self.detected_objects:
            x, y, w, h = detection['bbox']
            tool_name = detection['tool_name']
            confidence = detection['confidence']
            
            # 根据置信度选择颜色
            if confidence > 0.005:
                color = (0, 255, 0)  # 绿色 - 高置信度
            elif confidence > 0.002:
                color = (0, 255, 255)  # 黄色 - 中等置信度
            else:
                color = (255, 0, 0)  # 蓝色 - 低置信度
            
            # 绘制检测框
            cv2.rectangle(overlay, (x, y), (x + w, y + h), color, 2)
            
            # 绘制工具名称和置信度
            label = f"{tool_name}: {confidence:.3f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            
            # 背景矩形
            cv2.rectangle(overlay, (x, y - 25), (x + label_size[0] + 10, y), color, -1)
            
            # 文本
            cv2.putText(overlay, label, (x + 5, y - 8), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # 绘制状态栏
        status_bg = np.zeros((100, width, 3), dtype=np.uint8)
        cv2.rectangle(status_bg, (0, 0), (width, 100), (50, 50, 50), -1)
        
        # 统计信息
        tool_count = len(self.detected_objects)
        status_text = f"Real-time Tracking | Detected Objects: {tool_count}"
        cv2.putText(overlay, status_text, (20, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # 检测状态
        status_color = (0, 255, 255) if self.is_detecting else (0, 255, 0)
        status_indicator = "DETECTING..." if self.is_detecting else "READY"
        cv2.putText(overlay, status_indicator, (20, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
        
        # 混合状态栏
        overlay[:100] = cv2.addWeighted(overlay[:100], 0.7, status_bg, 0.3, 0)
        
        return overlay
    
    def run_camera_tracking(self, camera_id=0):
        """运行摄像头实时跟踪"""
        print(f"🎥 启动实时工具跟踪 (设备ID: {camera_id})")
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
            
            # 绘制跟踪覆盖层
            display_frame = self.draw_tracking_overlay(frame)
            
            # 显示画面
            cv2.imshow('Real-time Tool Tracking', display_frame)
            
            # 处理按键
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # 保存当前帧
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"tracking_capture_{timestamp}.jpg"
                cv2.imwrite(filename, display_frame)
                print(f"📸 已保存: {filename}")
            elif key == ord('r'):
                # 手动触发检测
                self.last_detection_time = 0
                print("🔄 手动触发检测...")
        
        cap.release()
        cv2.destroyAllWindows()
        print("🎥 实时跟踪已停止")

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("""
🎯 实时工具跟踪系统

使用方法:
  python realtime_tracker.py camera [camera_id]     # 摄像头实时跟踪 (默认ID=0)

控制键:
  q - 退出
  s - 保存当前帧
  r - 手动触发检测

特性:
  • 实时目标检测和跟踪
  • 动态检测框跟随工具移动
  • 滑动窗口扫描整个画面
  • 非极大值抑制去除重复检测
  • 置信度颜色编码

示例:
  python realtime_tracker.py camera 0
        """)
        return
    
    command = sys.argv[1].lower()
    
    if command != "camera":
        print("❌ 当前只支持摄像头模式")
        return
    
    # 配置检测系统
    config = SystemConfig(
        confidence_threshold=0.0005,
        uncertainty_threshold=-0.0001,
        save_roi_images=False,
        log_level="ERROR"
    )
    
    camera_id = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    tracker = RealTimeTracker(config, detection_interval=0.8)  # 更频繁的检测
    
    try:
        tracker.run_camera_tracking(camera_id)
    except KeyboardInterrupt:
        print("\n👋 用户中断，退出系统")
    except Exception as e:
        print(f"❌ 运行错误: {e}")

if __name__ == "__main__":
    main()