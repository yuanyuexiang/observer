#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强检测结果的全图标注功能
"""
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
import json

class EnhancedAnnotator:
    """增强检测结果标注器"""
    
    def __init__(self):
        self.font_path = self._find_chinese_font()
        
        # 工具名称中英文对照
        self.tool_names_zh = {
            'hammer': '锤子',
            'flat_screwdriver': '一字螺丝刀',
            'cross_screwdriver': '十字螺丝刀', 
            'pliers': '钳子',
            'wrench': '扳手',
            'tape_measure': '卷尺',
            'cutter': '切割工具',
            'hex_key_set': '六角扳手套装',
            'screw_box': '螺丝盒'
        }
        
        # 状态颜色
        self.status_colors = {
            'correct': (0, 255, 0),      # 绿色 - 正确位置
            'misplaced': (255, 165, 0),  # 橙色 - 位置错误  
            'missing': (255, 0, 0)       # 红色 - 缺失
        }
        
    def _find_chinese_font(self):
        """查找中文字体"""
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc", 
            "/System/Library/Fonts/Helvetica.ttc"
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                return font_path
        return None
    
    def create_enhanced_annotation(self, image_path, enhanced_results, workspace_config):
        """创建增强检测结果的标注图片"""
        try:
            # 加载图片
            image = Image.open(image_path)
            width, height = image.size
            draw = ImageDraw.Draw(image)
            
            # 设置字体
            title_font_size = max(int(width / 30), 18)
            detail_font_size = max(int(width / 40), 14)
            
            if self.font_path:
                title_font = ImageFont.truetype(self.font_path, title_font_size)
                detail_font = ImageFont.truetype(self.font_path, detail_font_size)
            else:
                title_font = ImageFont.load_default()
                detail_font = ImageFont.load_default()
            
            # 1. 绘制ROI边界框和状态
            for i, result in enumerate(enhanced_results):
                # 获取对应的工具配置
                tool_config = None
                for config in workspace_config:
                    if config['name'] == result.tool_name:
                        tool_config = config
                        break
                
                if not tool_config:
                    continue
                    
                bbox = tool_config['bbox']
                x, y, w, h = [int(v) for v in bbox]
                
                # 根据状态选择颜色
                color = self.status_colors.get(result.actual_status, (128, 128, 128))
                
                # 绘制边界框
                draw.rectangle([(x, y), (x + w, y + h)], outline=color, width=3)
                
                # 工具名称标签
                tool_zh = self.tool_names_zh.get(result.tool_name, result.tool_name)
                
                # 状态图标
                status_icons = {
                    'correct': '✅',
                    'misplaced': '🔄',
                    'missing': '❌'
                }
                status_icon = status_icons.get(result.actual_status, '?')
                
                # 标签背景
                label_text = f"{status_icon} {tool_zh}"
                label_bbox = draw.textbbox((0, 0), label_text, font=detail_font)
                label_width = label_bbox[2] - label_bbox[0] + 10
                label_height = label_bbox[3] - label_bbox[1] + 6
                
                # 标签位置（在边界框上方）
                label_x = x
                label_y = max(y - label_height - 5, 0)
                
                # 绘制标签背景
                draw.rectangle([(label_x, label_y), (label_x + label_width, label_y + label_height)], 
                              fill=color, outline=(0, 0, 0))
                
                # 绘制标签文字
                draw.text((label_x + 5, label_y + 3), label_text, 
                         font=detail_font, fill=(255, 255, 255))
            
            # 2. 右侧状态面板
            panel_width = min(width // 4, 320)
            panel_height = min(height - 40, 400)
            panel_x = width - panel_width - 20
            panel_y = 20
            
            # 半透明背景
            overlay = Image.new('RGBA', (panel_width, panel_height), (0, 0, 0, 200))
            image.paste(overlay, (panel_x, panel_y), overlay)
            
            # 面板标题
            panel_title = "工具箱状态检测"
            draw.text((panel_x + 15, panel_y + 15), panel_title, 
                     font=title_font, fill=(255, 255, 255))
            
            # 统计信息
            correct_count = sum(1 for r in enhanced_results if r.actual_status == 'correct')
            misplaced_count = sum(1 for r in enhanced_results if r.actual_status == 'misplaced')
            missing_count = sum(1 for r in enhanced_results if r.actual_status == 'missing')
            
            stats_y = panel_y + 50
            stats_lines = [
                f"✅ 正确位置: {correct_count}",
                f"🔄 位置错误: {misplaced_count}", 
                f"❌ 检测困难: {missing_count}",
                f"📊 总计: {len(enhanced_results)}"
            ]
            
            for i, line in enumerate(stats_lines):
                draw.text((panel_x + 15, stats_y + i * 25), line, 
                         font=detail_font, fill=(255, 255, 255))
            
            # 3. 详细列表
            details_y = stats_y + len(stats_lines) * 25 + 20
            draw.text((panel_x + 15, details_y), "详细状态:", 
                     font=detail_font, fill=(200, 200, 200))
            
            list_y = details_y + 25
            for i, result in enumerate(enhanced_results[:8]):  # 最多显示8个
                tool_zh = self.tool_names_zh.get(result.tool_name, result.tool_name)
                status_icon = status_icons.get(result.actual_status, '?')
                
                if result.actual_status == 'misplaced' and result.found_at:
                    status_text = f"{status_icon} {tool_zh[:6]}→错位"
                else:
                    status_text = f"{status_icon} {tool_zh[:8]}"
                
                color = self.status_colors.get(result.actual_status, (255, 255, 255))
                draw.text((panel_x + 15, list_y + i * 20), status_text, 
                         font=detail_font, fill=color)
            
            # 4. 底部信息栏
            bottom_text = f"增强检测 | 图片: {os.path.basename(image_path)}"
            draw.text((20, height - 30), bottom_text, 
                     font=detail_font, fill=(200, 200, 200))
            
            # 保存标注图片
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            output_path = f"{base_name}_enhanced_detected.jpg"
            image.save(output_path, 'JPEG', quality=95)
            
            print(f"💾 已保存增强检测标注图片: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ 创建增强标注图片失败: {e}")
            return None

def test_enhanced_annotation():
    """测试增强标注功能"""
    from enhanced_detector import EnhancedToolDetector
    import json
    
    detector = EnhancedToolDetector()
    annotator = EnhancedAnnotator()
    
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
    
    # 测试图片
    test_images = ['test.jpg', 'test2.jpg', 'test3.jpg']
    
    for image_path in test_images:
        if os.path.exists(image_path):
            print(f"\n🔍 处理增强检测: {image_path}")
            
            # 增强检测
            results = detector.detect_with_misplacement_check(image_path)
            
            if results:
                # 创建增强标注
                output_path = annotator.create_enhanced_annotation(image_path, results, workspace_config)
                if output_path:
                    print(f"✅ 成功创建增强标注: {output_path}")

if __name__ == "__main__":
    test_enhanced_annotation()