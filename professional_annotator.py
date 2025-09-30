#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专业工具箱状态标注器 - 创建美观的竖直列表报告
"""
import json
import os
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np

class ProfessionalToolboxAnnotator:
    """专业工具箱状态标注器"""
    
    def __init__(self):
        self.font_path = self._find_chinese_font()
        self.tool_names_zh = {
            'hammer': '锤子',
            'flat_screwdriver': '一字螺丝刀',
            'cross_screwdriver': '十字螺丝刀',
            'cutter': '切割工具',
            'tape_measure': '卷尺',
            'hex_key_set': '六角扳手套装',
            'screw_box': '螺丝盒',
            'pliers': '钳子',
            'wrench': '扳手'
        }
        
        # 状态颜色配置
        self.status_colors = {
            'present': (0, 200, 0),      # 绿色
            'missing': (255, 50, 50),    # 红色
            'uncertain': (255, 200, 0),  # 黄色
            'error': (255, 100, 0)       # 橙色
        }
        
        # 状态图标
        self.status_icons = {
            'present': '✅',
            'missing': '❌',
            'uncertain': '⚠️',
            'error': '🔧'
        }
        
    def _find_chinese_font(self):
        """查找中文字体"""
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Arial.ttf"
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                return font_path
        return None
    
    def get_chinese_font(self, size=24):
        """获取中文字体"""
        if self.font_path:
            return ImageFont.truetype(self.font_path, size)
        else:
            return ImageFont.load_default()
    
    def load_workspace_config(self, config_file='instances_default.json'):
        """加载工作空间配置（保留此方法以备将来可能需要）"""
        if not os.path.exists(config_file):
            return {}
        
        try:
            with open(config_file, 'r') as f:
                data = json.load(f)
            
            # 创建类别映射
            categories = {cat['id']: cat['name'] for cat in data['categories']}
            
            # 创建工具位置映射
            tool_positions = {}
            for ann in data['annotations']:
                tool_name = categories[ann['category_id']]
                bbox = ann['bbox']  # [x, y, width, height]
                tool_positions[tool_name] = {
                    'bbox': bbox,
                    'center': (bbox[0] + bbox[2]//2, bbox[1] + bbox[3]//2)
                }
            
            return tool_positions
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return {}
    
    def create_professional_status_report(self, image_path, detection_results, completeness_rate):
        """创建专业的工具箱状态报告"""
        # 加载图片
        image = Image.open(image_path)
        original_image = image.copy()
        
        # 处理检测结果，按状态分组
        tools_by_status = {
            'present': [],
            'missing': [],
            'uncertain': [],
            'error': []
        }
        
        for result in detection_results:
            status = result.status
            tool_name = result.tool_name
            tool_zh = self.tool_names_zh.get(tool_name, tool_name)
            confidence = result.confidence
            
            tools_by_status[status].append({
                'name': tool_name,
                'name_zh': tool_zh,
                'confidence': confidence
            })
        
        # 创建右侧报告面板（不再在图片上画边框）
        panel_width = 400
        panel_height = image.height
        
        # 扩展图片宽度以容纳报告面板
        new_width = image.width + panel_width
        new_image = Image.new('RGB', (new_width, panel_height), (250, 250, 250))
        new_image.paste(image, (0, 0))  # 使用原始图片，不加任何边框
        
        draw = ImageDraw.Draw(new_image)
        
        # 设置字体
        font_title = self.get_chinese_font(size=32)
        font_subtitle = self.get_chinese_font(size=24)
        font_item = self.get_chinese_font(size=20)
        font_small = self.get_chinese_font(size=16)
        
        # 报告面板背景
        panel_x = image.width
        draw.rectangle([panel_x, 0, new_width, panel_height], fill=(248, 248, 248), outline=(200, 200, 200), width=2)
        
        # 报告标题
        title = "工具箱状态报告"
        title_bbox = draw.textbbox((0, 0), title, font=font_title)
        title_w = title_bbox[2] - title_bbox[0]
        title_x = panel_x + (panel_width - title_w) // 2
        draw.text((title_x, 20), title, font=font_title, fill=(50, 50, 50))
        
        # 完整性指示器
        completeness_text = f"完整性: {completeness_rate:.1f}%"
        comp_color = (0, 150, 0) if completeness_rate >= 90 else (255, 150, 0) if completeness_rate >= 70 else (200, 50, 50)
        comp_bbox = draw.textbbox((0, 0), completeness_text, font=font_subtitle)
        comp_w = comp_bbox[2] - comp_bbox[0]
        comp_x = panel_x + (panel_width - comp_w) // 2
        draw.text((comp_x, 60), completeness_text, font=font_subtitle, fill=comp_color)
        
        # 绘制完整性进度条
        bar_x = panel_x + 30
        bar_y = 100
        bar_width = panel_width - 60
        bar_height = 20
        
        # 背景条
        draw.rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height], 
                      fill=(220, 220, 220), outline=(180, 180, 180))
        
        # 完整性条
        progress_width = int(bar_width * completeness_rate / 100)
        draw.rectangle([bar_x, bar_y, bar_x + progress_width, bar_y + bar_height], 
                      fill=comp_color)
        
        # 工具状态列表
        y_pos = 150
        
        # 状态顺序：在位 -> 缺失 -> 不确定 -> 错误
        status_order = ['present', 'missing', 'uncertain', 'error']
        status_titles = {
            'present': '✅ 在位工具',
            'missing': '❌ 缺失工具', 
            'uncertain': '⚠️ 不确定',
            'error': '🔧 检测错误'
        }
        
        for status in status_order:
            tools = tools_by_status[status]
            if not tools:
                continue
                
            # 状态分组标题
            status_title = f"{status_titles[status]} ({len(tools)})"
            draw.text((panel_x + 20, y_pos), status_title, font=font_subtitle, 
                     fill=self.status_colors[status])
            y_pos += 35
            
            # 工具列表
            for tool in tools:
                # 工具名称
                tool_text = f"  • {tool['name_zh']}"
                draw.text((panel_x + 30, y_pos), tool_text, font=font_item, fill=(80, 80, 80))
                
                # 置信度（如果有的话）
                if tool['confidence'] != 0:
                    conf_text = f"({tool['confidence']:+.3f})"
                    conf_color = (100, 100, 100)
                    draw.text((panel_x + 300, y_pos), conf_text, font=font_small, fill=conf_color)
                
                y_pos += 28
            
            y_pos += 15  # 分组间距
        
        # 底部时间戳
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        time_text = f"检测时间: {timestamp}"
        draw.text((panel_x + 20, panel_height - 30), time_text, font=font_small, fill=(120, 120, 120))
        
        # 保存结果
        base_name = os.path.splitext(image_path)[0]
        output_path = f"{base_name}_professional_status.jpg"
        new_image.save(output_path, 'JPEG', quality=95)
        
        return output_path

def test_professional_annotation():
    """测试专业标注功能"""
    from production_tool_detector import ProductionToolDetector
    from types import SimpleNamespace
    
    # 初始化检测器 - 使用正确的配置格式
    config = SimpleNamespace(
        clip_model='ViT-B-32',
        clip_pretrained='openai',
        device='cpu',
        confidence_threshold=0.0,
        log_level='ERROR'
    )
    
    detector = ProductionToolDetector(config)
    annotator = ProfessionalToolboxAnnotator()
    
    # 测试图片
    test_images = ['test.jpg', 'test2.jpg', 'test3.jpg']
    
    for image_path in test_images:
        if os.path.exists(image_path):
            print(f"\n🔍 处理图片: {image_path}")
            
            # 进行检测
            workspace_config = detector.load_workspace_configuration('instances_default.json')
            results = detector.run_full_detection(image_path, workspace_config)
            
            # 计算完整性
            analysis = detector.analyze_workspace_status(results)
            completeness_rate = analysis['completeness_rate']
            
            # 创建专业标注
            output_path = annotator.create_professional_status_report(
                image_path, results, completeness_rate
            )
            
            if output_path:
                print(f"✅ 生成专业报告: {output_path}")
            else:
                print(f"❌ 生成失败: {image_path}")

if __name__ == "__main__":
    test_professional_annotation()