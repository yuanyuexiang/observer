#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进的图片标注功能 - 支持中文显示和更好的布局
"""
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

class ImprovedAnnotator:
    """改进的图片标注器"""
    
    def __init__(self):
        self.font_path = self._find_chinese_font()
        self.tool_names_zh = {
            'hammer': '锤子',
            'screwdriver': '螺丝刀', 
            'pliers': '钳子',
            'wrench': '扳手',
            'tape measure': '卷尺',
            'cutter': '切割工具',
            'hex key': '六角扳手',
            'screw box': '螺丝盒'
        }
        
    def _find_chinese_font(self):
        """查找中文字体"""
        # macOS常见中文字体路径
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
    
    def annotate_detection(self, image_path, tool_name, confidence):
        """为基础检测创建简单标注"""
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        
        # 字体设置
        font_main = self.get_chinese_font(size=40)
        font_small = self.get_chinese_font(size=24)
        
        # 工具名称翻译
        tool_zh = self.tool_names_zh.get(tool_name, tool_name)
        
        # 标题
        title = f"检测结果: {tool_zh}"
        bbox = draw.textbbox((0, 0), title, font=font_main)
        text_width = bbox[2] - bbox[0]
        
        # 绿色背景
        draw.rectangle([(20, 20), (40 + text_width, 80)], 
                      fill=(0, 200, 0), outline=(0, 150, 0), width=2)
        
        # 文字
        draw.text((30, 30), title, font=font_main, fill=(255, 255, 255))
        draw.text((30, 55), f"置信度: {confidence:.4f}", font=font_small, fill=(255, 255, 255))
        
        # 保存
        base_name = os.path.splitext(image_path)[0]
        output_path = f"{base_name}_detected.jpg"
        image.save(output_path, 'JPEG', quality=95)
        
        return output_path
    
    def annotate_toolbox_status(self, image_path, present_tools, missing_tools, completeness_rate):
        """创建工具箱状态标注图片"""
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        
        # 字体设置
        font_main = self.get_chinese_font(size=40)
        font_small = self.get_chinese_font(size=24)
        
        # 半透明背景
        overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle([0, 0, image.width, 200], fill=(40, 40, 40, 180))
        image = Image.alpha_composite(image.convert('RGBA'), overlay).convert('RGB')
        draw = ImageDraw.Draw(image)
        
        # 标题
        title = f"工具箱状态检查 - 完整性: {completeness_rate:.1f}%"
        bbox = draw.textbbox((0, 0), title, font=font_main)
        text_width = bbox[2] - bbox[0]
        title_x = (image.width - text_width) // 2
        draw.text((title_x, 20), title, font=font_main, fill=(255, 255, 255))
        
        # 状态信息
        y_pos = 80
        if present_tools:
            # 翻译工具名称
            present_zh = [self.tool_names_zh.get(tool, tool) for tool in present_tools]
            text = f"✅ 在位工具 ({len(present_tools)}): " + ", ".join(present_zh)
            draw.text((20, y_pos), text, font=font_small, fill=(0, 255, 0))
            y_pos += 35
        
        if missing_tools:
            # 翻译工具名称
            missing_zh = [self.tool_names_zh.get(tool, tool) for tool in missing_tools]
            text = f"❌ 缺失工具 ({len(missing_tools)}): " + ", ".join(missing_zh)
            draw.text((20, y_pos), text, font=font_small, fill=(255, 0, 0))
        else:
            text = "🎉 所有工具都在工具箱中！"
            draw.text((20, y_pos), text, font=font_small, fill=(0, 255, 0))
        
        # 保存
        base_name = os.path.splitext(image_path)[0]
        output_path = f"{base_name}_status.jpg"
        image.save(output_path, 'JPEG', quality=95)
        
        return output_path
    
    def create_annotated_image(self, image_path, detection_result):
        """创建带标注的图片"""
        try:
            # 使用PIL处理图片以支持中文
            image = Image.open(image_path)
            width, height = image.size
            
            # 创建绘图对象
            draw = ImageDraw.Draw(image)
            
            # 设置字体
            title_font_size = max(int(width / 25), 20)
            detail_font_size = max(int(width / 35), 16)
            
            if self.font_path:
                title_font = ImageFont.truetype(self.font_path, title_font_size)
                detail_font = ImageFont.truetype(self.font_path, detail_font_size)
            else:
                title_font = ImageFont.load_default()
                detail_font = ImageFont.load_default()
            
            # 获取检测结果
            best_tool = detection_result['best_tool']
            all_results = detection_result['all_results']
            
            # 工具名称中英文对照
            tool_names_zh = {
                'hammer': '锤子',
                'screwdriver': '螺丝刀', 
                'pliers': '钳子',
                'wrench': '扳手',
                'tape measure': '卷尺',
                'cutter': '切割工具',
                'hex key': '六角扳手',
                'screw box': '螺丝盒'
            }
            
            tool_zh = tool_names_zh.get(best_tool['tool'], best_tool['tool'])
            
            # 1. 主标题背景
            title_text = f"检测结果: {tool_zh}"
            title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_height = title_bbox[3] - title_bbox[1]
            
            # 绿色背景
            draw.rectangle([(20, 20), (40 + title_width, 40 + title_height)], 
                          fill=(0, 200, 0), outline=(0, 150, 0), width=2)
            
            # 标题文字
            draw.text((30, 30), title_text, font=title_font, fill=(255, 255, 255))
            
            # 2. 置信度信息
            conf_text = f"置信度: {best_tool['score']:.4f}"
            draw.text((30, 50 + title_height), conf_text, font=detail_font, fill=(255, 255, 255))
            
            # 3. 右侧详细结果面板
            panel_width = min(width // 3, 300)
            panel_height = min(height // 2, 250)
            panel_x = width - panel_width - 20
            panel_y = 20
            
            # 半透明黑色背景
            overlay = Image.new('RGBA', (panel_width, panel_height), (0, 0, 0, 180))
            image.paste(overlay, (panel_x, panel_y), overlay)
            
            # 面板标题
            panel_title = "检测详情"
            draw.text((panel_x + 15, panel_y + 15), panel_title, 
                     font=title_font, fill=(255, 255, 255))
            
            # 前5名结果
            y_offset = panel_y + 50
            for i, result in enumerate(all_results[:5]):
                tool_zh_name = tool_names_zh.get(result['tool'], result['tool'])
                rank_text = f"{i+1}. {tool_zh_name}"
                score_text = f"{result['score']:.4f}"
                
                # 排名颜色
                if i == 0:
                    color = (255, 215, 0)  # 金色
                elif i == 1:
                    color = (192, 192, 192)  # 银色
                elif i == 2:
                    color = (205, 127, 50)  # 铜色
                else:
                    color = (255, 255, 255)  # 白色
                
                draw.text((panel_x + 15, y_offset + i * 25), rank_text, 
                         font=detail_font, fill=color)
                draw.text((panel_x + panel_width - 80, y_offset + i * 25), score_text, 
                         font=detail_font, fill=color)
            
            # 4. 底部状态栏
            status_text = f"图片: {os.path.basename(image_path)} | 检测时间: {detection_result.get('timestamp', 'N/A')[:19]}"
            status_y = height - 30
            
            # 状态栏背景
            status_bbox = draw.textbbox((0, 0), status_text, font=detail_font)
            status_width = status_bbox[2] - status_bbox[0]
            draw.rectangle([(10, status_y - 5), (20 + status_width, status_y + 25)], 
                          fill=(40, 40, 40), outline=(80, 80, 80))
            
            draw.text((15, status_y), status_text, font=detail_font, fill=(200, 200, 200))
            
            # 保存图片
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            output_path = f"{base_name}_detected.jpg"
            image.save(output_path, 'JPEG', quality=95)
            
            print(f"💾 已保存改进标注图片: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ 创建标注图片失败: {e}")
            return None

def test_improved_annotation():
    """测试改进的标注功能"""
    from simple_image_detector import SimpleImageDetector
    
    detector = SimpleImageDetector()
    annotator = ImprovedAnnotator()
    
    # 测试图片
    test_images = ['test.jpg', 'test2.jpg', 'test3.jpg']
    
    for image_path in test_images:
        if os.path.exists(image_path):
            print(f"\n🔍 处理图片: {image_path}")
            
            # 检测
            result = detector.detect_tools_in_image(image_path, save_result=False)
            
            if result:
                # 创建改进的标注
                output_path = annotator.create_annotated_image(image_path, result)
                if output_path:
                    print(f"✅ 成功创建: {output_path}")
            else:
                print(f"❌ 检测失败: {image_path}")

if __name__ == "__main__":
    test_improved_annotation()