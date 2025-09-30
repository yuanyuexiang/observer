#!/usr/bin/env python3
"""
简单图片工具检测器 - 纯静态图片检测，无视频跟踪
支持单张图片检测和批量检测
"""
import cv2
import torch
from PIL import Image
import open_clip
import numpy as np
import os
import glob
from datetime import datetime
import argparse

class SimpleImageDetector:
    """简单图片工具检测器"""
    
    def __init__(self):
        # 初始化CLIP模型
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🔧 初始化CLIP模型 (设备: {self.device})")
        
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            "ViT-B-32", pretrained="openai"
        )
        self.model = self.model.to(self.device)
        self.tokenizer = open_clip.get_tokenizer("ViT-B-32")
        
        # 工具类别定义
        self.tool_descriptions = [
            "a metal hammer tool",
            "a screwdriver with handle", 
            "metal pliers for gripping",
            "a wrench for bolts",
            "a measuring tape tool",
            "a cutting tool knife",
            "a hex allen key tool",
            "a toolbox with screws"
        ]
        
        self.tool_names = [
            "hammer", "screwdriver", "pliers", "wrench", 
            "tape measure", "cutter", "hex key", "screw box"
        ]
        
        print("✅ 图片检测器初始化完成")
    
    def detect_tools_in_image(self, image_path, save_result=True):
        """检测单张图片中的工具"""
        print(f"\n🔍 分析图片: {image_path}")
        
        try:
            # 加载图片
            image = cv2.imread(image_path)
            if image is None:
                print(f"❌ 无法加载图片: {image_path}")
                return None
            
            # 转换为RGB并预处理
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image_pil = Image.fromarray(image_rgb)
            image_input = self.preprocess(image_pil).unsqueeze(0).to(self.device)
            
            # CLIP推理
            text_tokens = self.tokenizer(self.tool_descriptions).to(self.device)
            
            with torch.no_grad():
                image_features = self.model.encode_image(image_input)
                text_features = self.model.encode_text(text_tokens)
                
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
                text_features = text_features / text_features.norm(dim=-1, keepdim=True)
                
                similarities = (image_features @ text_features.T).softmax(dim=-1)[0]
            
            # 分析结果
            results = []
            for i, (tool_name, description, score) in enumerate(zip(self.tool_names, self.tool_descriptions, similarities)):
                results.append({
                    'tool': tool_name,
                    'description': description,
                    'score': score.item(),
                    'rank': i + 1
                })
            
            # 按分数排序
            results.sort(key=lambda x: x['score'], reverse=True)
            
            # 显示结果
            print(f"📊 检测结果 (按置信度排序):")
            for i, result in enumerate(results):
                icon = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "  "
                print(f"{icon} {result['tool']:12} - {result['score']:.4f} ({result['description']})")
            
            # 确定最可能的工具
            best_result = results[0]
            print(f"\n🎯 最可能的工具: {best_result['tool'].upper()} (置信度: {best_result['score']:.4f})")
            
            # 保存带标注的结果图片
            if save_result:
                self.save_annotated_image(image, image_path, best_result, results[:3])
            
            return {
                'image_path': image_path,
                'best_tool': best_result,
                'all_results': results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ 处理错误: {e}")
            return None
    
    def save_annotated_image(self, image, original_path, best_result, top_results):
        """保存带标注的结果图片"""
        try:
            annotated = image.copy()
            height, width = image.shape[:2]
            
            # 绘制结果信息
            # 主标题
            main_text = f"检测结果: {best_result['tool'].upper()}"
            font_scale = min(width / 800, 1.5)
            thickness = max(int(font_scale * 2), 2)
            
            # 主标题背景
            (text_width, text_height), _ = cv2.getTextSize(main_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
            cv2.rectangle(annotated, (20, 20), (20 + text_width + 20, 20 + text_height + 20), (0, 255, 0), -1)
            cv2.putText(annotated, main_text, (30, 20 + text_height), 
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)
            
            # 置信度
            conf_text = f"置信度: {best_result['score']:.3f}"
            cv2.putText(annotated, conf_text, (30, 20 + text_height + 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale * 0.6, (255, 255, 255), max(thickness - 1, 1))
            
            # 右侧显示前3名结果
            y_start = 100
            cv2.rectangle(annotated, (width - 250, y_start - 20), (width - 10, y_start + 120), (40, 40, 40), -1)
            cv2.putText(annotated, "TOP 3:", (width - 240, y_start), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            for i, result in enumerate(top_results):
                rank_text = f"{i+1}. {result['tool']}: {result['score']:.3f}"
                color = (0, 255, 0) if i == 0 else (255, 255, 255)
                cv2.putText(annotated, rank_text, (width - 240, y_start + 30 + i * 25), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            
            # 保存标注图片
            base_name = os.path.splitext(os.path.basename(original_path))[0]
            output_path = f"{base_name}_detected.jpg"
            cv2.imwrite(output_path, annotated)
            print(f"💾 已保存标注图片: {output_path}")
            
        except Exception as e:
            print(f"❌ 保存标注图片失败: {e}")
    
    def batch_detect(self, folder_path, pattern="*.jpg"):
        """批量检测文件夹中的图片"""
        print(f"\n📁 批量检测文件夹: {folder_path}")
        print(f"🔍 搜索模式: {pattern}")
        
        # 查找图片文件
        search_pattern = os.path.join(folder_path, pattern)
        image_files = glob.glob(search_pattern)
        
        if not image_files:
            print(f"❌ 未找到匹配的图片文件: {search_pattern}")
            return []
        
        print(f"📸 找到 {len(image_files)} 张图片")
        
        results = []
        for i, image_file in enumerate(image_files, 1):
            print(f"\n[{i}/{len(image_files)}] 处理: {os.path.basename(image_file)}")
            result = self.detect_tools_in_image(image_file)
            if result:
                results.append(result)
        
        # 汇总报告
        print(f"\n📋 批量检测完成报告:")
        print(f"总计处理: {len(image_files)} 张图片")
        print(f"成功检测: {len(results)} 张")
        
        if results:
            print(f"\n🏆 检测结果汇总:")
            tool_counts = {}
            for result in results:
                tool = result['best_tool']['tool']
                tool_counts[tool] = tool_counts.get(tool, 0) + 1
            
            for tool, count in sorted(tool_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"  {tool}: {count} 张图片")
        
        return results
    
    def interactive_mode(self):
        """交互式检测模式"""
        print("\n🎯 进入交互式检测模式")
        print("输入图片路径进行检测，输入 'quit' 退出")
        
        while True:
            try:
                user_input = input("\n📷 请输入图片路径 (或 'quit' 退出): ").strip()
                
                if user_input.lower() in ['quit', 'q', 'exit']:
                    print("👋 退出交互模式")
                    break
                
                if not user_input:
                    continue
                
                if os.path.isfile(user_input):
                    self.detect_tools_in_image(user_input)
                elif os.path.isdir(user_input):
                    self.batch_detect(user_input)
                else:
                    print(f"❌ 文件或文件夹不存在: {user_input}")
                    
            except KeyboardInterrupt:
                print("\n👋 退出交互模式")
                break
            except Exception as e:
                print(f"❌ 错误: {e}")


def main():
    parser = argparse.ArgumentParser(description='简单图片工具检测器')
    parser.add_argument('input', nargs='?', help='图片文件路径或文件夹路径')
    parser.add_argument('--batch', action='store_true', help='批量处理模式')
    parser.add_argument('--pattern', default='*.jpg', help='批量处理时的文件模式 (默认: *.jpg)')
    parser.add_argument('--interactive', '-i', action='store_true', help='交互式模式')
    
    args = parser.parse_args()
    
    # 创建检测器
    detector = SimpleImageDetector()
    
    if args.interactive:
        # 交互式模式
        detector.interactive_mode()
    elif args.input:
        if os.path.isfile(args.input):
            # 单个文件检测
            detector.detect_tools_in_image(args.input)
        elif os.path.isdir(args.input):
            # 文件夹批量检测
            detector.batch_detect(args.input, args.pattern)
        else:
            print(f"❌ 文件或文件夹不存在: {args.input}")
    else:
        # 默认交互模式
        detector.interactive_mode()


if __name__ == "__main__":
    main()