#!/usr/bin/env python3
"""
增强版工具检测器 - 支持检测工具放错位置
"""
from production_tool_detector import ProductionToolDetector, SystemConfig
from simple_image_detector import SimpleImageDetector
from PIL import Image
import json
from dataclasses import dataclass
from typing import List, Dict, Optional
import os

@dataclass
class EnhancedDetectionResult:
    """增强检测结果"""
    tool_name: str
    expected_position: str
    actual_status: str  # 'correct', 'misplaced', 'missing'
    confidence: float
    found_at: Optional[str] = None  # 如果misplaced，在哪里找到的
    bbox: List[int] = None

class EnhancedToolDetector:
    """增强版工具检测器"""
    
    def __init__(self):
        self.config = SystemConfig(
            confidence_threshold=0.0001,
            uncertainty_threshold=-0.0001,
            save_roi_images=False,
            log_level='ERROR'
        )
        
        self.production_detector = ProductionToolDetector(self.config)
        self.simple_detector = SimpleImageDetector()
        
        # 工具类型映射
        self.tool_mapping = {
            'hammer': 'hammer',
            'flat_screwdriver': 'screwdriver', 
            'cross_screwdriver': 'screwdriver',
            'cutter': 'cutter',
            'tape_measure': 'tape measure',
            'hex_key_set': 'hex key',
            'screw_box': 'screw box',
            'pliers': 'pliers',
            'wrench': 'wrench'
        }
    
    def detect_with_misplacement_check(self, image_path: str) -> List[EnhancedDetectionResult]:
        """检测工具位置，包括错位检测"""
        
        workspace_config = self.production_detector.load_workspace_configuration('instances_default.json')
        image = Image.open(image_path).convert('RGB')
        
        results = []
        roi_analysis = {}
        
        print("🔍 第一阶段：分析各个ROI区域内容")
        
        # 第一阶段：分析每个ROI区域实际包含什么工具
        for i, tool_config in enumerate(workspace_config):
            expected_tool = tool_config['name']
            bbox = tool_config['bbox']
            x, y, w, h = [int(v) for v in bbox]
            
            # 提取ROI区域
            roi = image.crop((x, y, x + w, y + h))
            roi_path = f"temp_roi_{expected_tool}.jpg"
            roi.save(roi_path)
            
            # 检测这个区域最像什么工具
            detection_result = self.simple_detector.detect_tools_in_image(roi_path)
            
            if detection_result:
                best_tool = detection_result['best_tool']
                detected_tool = best_tool['tool']
                confidence = best_tool['score']
                
                roi_analysis[expected_tool] = {
                    'detected': detected_tool,
                    'confidence': confidence,
                    'position': f"{expected_tool}_position",
                    'bbox': bbox
                }
                
                print(f"  {expected_tool:15} 位置 → 检测到: {detected_tool:12} (置信度: {confidence:.4f})")
            
            # 清理临时文件
            if os.path.exists(roi_path):
                os.remove(roi_path)
        
        print(f"\n🔎 第二阶段：分析工具位置状态")
        
        # 第二阶段：分析每个工具的状态
        for expected_tool in workspace_config:
            tool_name = expected_tool['name']
            expected_type = self.tool_mapping.get(tool_name, tool_name)
            
            # 检查该工具是否在正确位置
            roi_info = roi_analysis.get(tool_name, {})
            detected_type = roi_info.get('detected', '')
            confidence = roi_info.get('confidence', 0.0)
            
            # 判断状态
            if self._is_correct_tool(expected_type, detected_type):
                # 工具在正确位置
                status = 'correct'
                found_at = None
            else:
                # 工具不在预期位置，检查是否在其他位置
                found_at = self._find_tool_elsewhere(expected_type, roi_analysis, tool_name)
                if found_at:
                    status = 'misplaced'
                else:
                    status = 'missing'
            
            result = EnhancedDetectionResult(
                tool_name=tool_name,
                expected_position=f"{tool_name}_position",
                actual_status=status,
                confidence=confidence,
                found_at=found_at,
                bbox=roi_info.get('bbox', [])
            )
            
            results.append(result)
        
        return results
    
    def _is_correct_tool(self, expected: str, detected: str) -> bool:
        """判断检测到的工具是否与期望一致"""
        # 简单的匹配逻辑
        expected_lower = expected.lower()
        detected_lower = detected.lower()
        
        # 直接匹配
        if expected_lower == detected_lower:
            return True
        
        # 部分匹配
        if expected_lower in detected_lower or detected_lower in expected_lower:
            return True
        
        # 螺丝刀特殊处理
        if expected_lower == 'screwdriver' and 'screwdriver' in detected_lower:
            return True
            
        return False
    
    def _find_tool_elsewhere(self, expected_tool: str, roi_analysis: Dict, exclude_position: str) -> Optional[str]:
        """在其他位置寻找工具"""
        for position, info in roi_analysis.items():
            if position == exclude_position:
                continue
                
            detected = info['detected']
            if self._is_correct_tool(expected_tool, detected):
                return f"{position}_position"
        
        return None
    
    def print_enhanced_results(self, results: List[EnhancedDetectionResult]):
        """打印增强检测结果"""
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
                status_text = '缺失'
                missing_count += 1
            
            print(f"{result.tool_name:15} {icon} {status_text}")
        
        print(f"\n=== 状态统计 ===")
        print(f"正确位置: {correct_count} ✅")
        print(f"位置错误: {misplaced_count} 🔄")
        print(f"真正缺失: {missing_count} ❌")
        
        if misplaced_count > 0:
            print(f"\n💡 建议: 有 {misplaced_count} 个工具需要重新整理到正确位置")

def main():
    """主函数"""
    print("🔧 增强版工具位置检测")
    print("=" * 50)
    
    detector = EnhancedToolDetector()
    results = detector.detect_with_misplacement_check('test.jpg')
    detector.print_enhanced_results(results)

if __name__ == "__main__":
    main()