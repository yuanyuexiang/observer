"""
生产级工具检测系统
基于高质量标注数据的完整解决方案
"""
import torch
import open_clip
from PIL import Image, ImageDraw, ImageFont
import json
import os
import time
from datetime import datetime
import logging
from typing import Dict, List, Tuple, Optional
import numpy as np
from dataclasses import dataclass
from pathlib import Path

@dataclass
class DetectionResult:
    """检测结果数据类"""
    tool_id: str
    tool_name: str
    status: str  # "present", "missing", "uncertain"
    confidence: float
    bbox: List[int]
    detection_time: float
    details: Dict

@dataclass
class SystemConfig:
    """系统配置数据类"""
    model_name: str = "ViT-B-32"
    confidence_threshold: float = 0.0001  # 接近零的阈值
    uncertainty_threshold: float = -0.0003  # 更严格的缺失判断，负值就是缺失
    detection_timeout: float = 30.0
    log_level: str = "INFO"
    save_roi_images: bool = True
    enable_alerts: bool = True

class ProductionToolDetector:
    """生产级工具检测器"""
    
    def __init__(self, config: SystemConfig = None):
        self.config = config or SystemConfig()
        self.logger = self._setup_logging()
        
        # 性能统计
        self.stats = {
            "total_detections": 0,
            "successful_detections": 0,
            "failed_detections": 0,
            "average_detection_time": 0,
            "startup_time": time.time()
        }
        
        self.logger.info("🚀 启动生产级工具检测系统")
        self._initialize_clip_model()
        self._load_tool_templates()
        
    def _setup_logging(self):
        """设置日志系统"""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/tool_detection.log'),
                logging.StreamHandler()
            ]
        )
        
        # 确保日志目录存在
        os.makedirs('logs', exist_ok=True)
        
        return logging.getLogger('ToolDetector')
    
    def _initialize_clip_model(self):
        """初始化CLIP模型"""
        try:
            start_time = time.time()
            self.logger.info(f"加载CLIP模型: {self.config.model_name}")
            
            self.model, _, self.preprocess = open_clip.create_model_and_transforms(
                self.config.model_name, pretrained='openai'
            )
            self.tokenizer = open_clip.get_tokenizer(self.config.model_name)
            
            self.device = "cpu"  # 可以配置为 "cuda" 如果有GPU
            self.model.to(self.device)
            self.model.eval()
            
            init_time = time.time() - start_time
            self.logger.info(f"✅ CLIP模型初始化完成 ({init_time:.2f}秒)")
            
        except Exception as e:
            self.logger.error(f"❌ CLIP模型初始化失败: {e}")
            raise
    
    def _load_tool_templates(self):
        """加载工具文本模板"""
        self.tool_templates = {
            "hammer": {
                "positive": [
                    "hammer",
                    "hammer tool",
                    "claw hammer",
                    "construction hammer"
                ],
                "negative": [
                    "no hammer", 
                    "empty space",
                    "missing tool",
                    "no tool"
                ]
            },
            "pliers": {
                "positive": [
                    "pliers",
                    "pliers tool", 
                    "yellow pliers",
                    "needle nose pliers"
                ],
                "negative": [
                    "no pliers",
                    "empty space", 
                    "missing tool",
                    "no tool"
                ]
            },
            "wrench": {
                "positive": [
                    "wrench",
                    "adjustable wrench",
                    "spanner",
                    "wrench tool"
                ],
                "negative": [
                    "no wrench",
                    "empty space",
                    "missing tool", 
                    "no tool"
                ]
            },
            "flat_screwdriver": {
                "positive": [
                    "screwdriver",
                    "flat screwdriver",
                    "flathead screwdriver",
                    "screwdriver tool"
                ],
                "negative": [
                    "no screwdriver",
                    "empty space",
                    "missing tool",
                    "no tool"
                ]
            },
            "cross_screwdriver": {
                "positive": [
                    "screwdriver",
                    "phillips screwdriver", 
                    "cross screwdriver",
                    "screwdriver tool"
                ],
                "negative": [
                    "no screwdriver",
                    "empty space",
                    "missing tool",
                    "no tool"
                ]
            },
            "cutter": {
                "positive": [
                    "cutter",
                    "utility knife",
                    "box cutter",
                    "cutting tool"
                ],
                "negative": [
                    "no cutter",
                    "empty space",
                    "missing tool",
                    "no tool"
                ]
            },
            "tape_measure": {
                "positive": [
                    "tape measure",
                    "measuring tape",
                    "ruler",
                    "measuring tool"
                ],
                "negative": [
                    "no tape measure",
                    "empty space",
                    "missing tool",
                    "no tool"
                ]
            },
            "hex_key_set": {
                "positive": [
                    "hex keys",
                    "allen keys", 
                    "hex key set",
                    "allen wrench set"
                ],
                "negative": [
                    "no hex keys",
                    "empty space",
                    "missing tool",
                    "no tool"
                ]
            },
            "screw_box": {
                "positive": [
                    "screws",
                    "screw box",
                    "hardware",
                    "screw storage"
                ],
                "negative": [
                    "no screws",
                    "empty compartment",
                    "missing tool",
                    "no tool"
                ]
            }
        }
        
        self.logger.info(f"✅ 加载了 {len(self.tool_templates)} 种工具模板")
    
    def load_workspace_configuration(self, annotation_file: str) -> List[Dict]:
        """加载工作空间配置"""
        try:
            with open(annotation_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 解析标注数据
            categories = {cat['id']: cat['name'] for cat in data['categories']}
            
            workspace_config = []
            for ann in data['annotations']:
                tool_config = {
                    "id": f"tool_{ann['id']}",
                    "name": categories[ann['category_id']],
                    "category_id": ann['category_id'],
                    "bbox": ann['bbox'],  # [x, y, w, h]
                    "expected_status": "present",  # 默认应该存在
                    "priority": "normal",  # normal, high, critical
                    "alert_enabled": True
                }
                workspace_config.append(tool_config)
            
            self.logger.info(f"✅ 加载工作空间配置: {len(workspace_config)} 个工具位置")
            return workspace_config
            
        except Exception as e:
            self.logger.error(f"❌ 加载工作空间配置失败: {e}")
            raise
    
    def detect_single_tool(self, image: Image.Image, tool_config: Dict) -> DetectionResult:
        """检测单个工具"""
        start_time = time.time()
        
        try:
            # 解析ROI坐标
            bbox = tool_config["bbox"]
            x, y, w, h = bbox
            
            # 转换为PIL crop格式并裁剪
            roi_bbox = [int(x), int(y), int(x+w), int(y+h)]
            roi_crop = image.crop(roi_bbox)
            
            # 保存ROI图片（如果启用）
            roi_image_path = None
            if self.config.save_roi_images:
                roi_dir = Path("data/production_rois")
                roi_dir.mkdir(parents=True, exist_ok=True)
                roi_image_path = roi_dir / f"{tool_config['id']}.png"
                roi_crop.save(roi_image_path)
            
            # 获取工具模板
            tool_name = tool_config["name"]
            templates = self.tool_templates.get(tool_name, self.tool_templates["hammer"])
            
            # 准备文本
            all_texts = templates["positive"] + templates["negative"]
            
            # CLIP推理
            roi_input = self.preprocess(roi_crop).unsqueeze(0)
            text_tokens = self.tokenizer(all_texts).to(self.device)
            
            with torch.no_grad():
                image_features = self.model.encode_image(roi_input)
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
                
                text_features = self.model.encode_text(text_tokens)
                text_features = text_features / text_features.norm(dim=-1, keepdim=True)
                
                similarities = (image_features @ text_features.T).softmax(dim=-1)
            
            # 分析结果
            pos_count = len(templates["positive"])
            positive_scores = similarities[0][:pos_count]
            negative_scores = similarities[0][pos_count:]
            
            avg_positive = positive_scores.mean().item()
            avg_negative = negative_scores.mean().item()
            confidence_gap = avg_positive - avg_negative
            
            best_pos_idx = positive_scores.argmax().item()
            best_match = templates["positive"][best_pos_idx]
            best_score = positive_scores[best_pos_idx].item()
            
            # 智能状态判断 - 调整后的阈值
            if confidence_gap > self.config.confidence_threshold:
                status = "present"
            elif confidence_gap > self.config.uncertainty_threshold:
                status = "uncertain"
            else:
                status = "missing"
            
            detection_time = time.time() - start_time
            
            # 创建结果对象
            result = DetectionResult(
                tool_id=tool_config["id"],
                tool_name=tool_name,
                status=status,
                confidence=confidence_gap,
                bbox=roi_bbox,
                detection_time=detection_time,
                details={
                    "avg_positive": avg_positive,
                    "avg_negative": avg_negative,
                    "best_match": best_match,
                    "best_score": best_score,
                    "roi_image": str(roi_image_path) if roi_image_path else None,
                    "templates_used": len(all_texts)
                }
            )
            
            self.logger.debug(f"工具检测完成: {tool_name} - {status} ({detection_time:.3f}s)")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ 检测工具失败 {tool_config['name']}: {e}")
            # 返回错误结果
            return DetectionResult(
                tool_id=tool_config["id"],
                tool_name=tool_config.get("name", "unknown"),
                status="error",
                confidence=0.0,
                bbox=[0, 0, 0, 0],
                detection_time=time.time() - start_time,
                details={"error": str(e)}
            )
    
    def run_full_detection(self, image_path: str, workspace_config: List[Dict]) -> List[DetectionResult]:
        """运行完整检测"""
        self.logger.info(f"🔍 开始完整工具检测")
        self.logger.info(f"📷 图片: {image_path}")
        self.logger.info(f"🔧 工具数量: {len(workspace_config)}")
        
        start_time = time.time()
        
        try:
            # 加载图片
            image = Image.open(image_path).convert('RGB')
            self.logger.info(f"✅ 图片加载成功: {image.size}")
            
            results = []
            
            # 检测每个工具
            for i, tool_config in enumerate(workspace_config, 1):
                self.logger.info(f"检测进度: {i}/{len(workspace_config)} - {tool_config['name']}")
                
                result = self.detect_single_tool(image, tool_config)
                results.append(result)
                
                # 更新统计
                self.stats["total_detections"] += 1
                if result.status != "error":
                    self.stats["successful_detections"] += 1
                else:
                    self.stats["failed_detections"] += 1
            
            total_time = time.time() - start_time
            avg_time = total_time / len(workspace_config)
            
            self.stats["average_detection_time"] = avg_time
            
            self.logger.info(f"✅ 检测完成: {total_time:.2f}秒 (平均 {avg_time:.3f}秒/工具)")
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ 完整检测失败: {e}")
            raise
    
    def analyze_workspace_status(self, results: List[DetectionResult]) -> Dict:
        """分析工作空间状态"""
        analysis = {
            "total_tools": len(results),
            "present_tools": sum(1 for r in results if r.status == "present"),
            "missing_tools": sum(1 for r in results if r.status == "missing"), 
            "uncertain_tools": sum(1 for r in results if r.status == "uncertain"),
            "error_tools": sum(1 for r in results if r.status == "error"),
            "overall_status": "unknown",
            "completeness_rate": 0.0,
            "confidence_score": 0.0,
            "alerts": []
        }
        
        # 计算完整性率
        valid_results = [r for r in results if r.status != "error"]
        if valid_results:
            analysis["completeness_rate"] = analysis["present_tools"] / len(valid_results) * 100
            analysis["confidence_score"] = np.mean([abs(r.confidence) for r in valid_results])
        
        # 整体状态判断
        if analysis["completeness_rate"] >= 90:
            analysis["overall_status"] = "excellent"
        elif analysis["completeness_rate"] >= 75:
            analysis["overall_status"] = "good"
        elif analysis["completeness_rate"] >= 50:
            analysis["overall_status"] = "fair"
        else:
            analysis["overall_status"] = "poor"
        
        # 生成警报
        for result in results:
            if result.status == "missing":
                analysis["alerts"].append({
                    "type": "missing_tool",
                    "tool_name": result.tool_name,
                    "tool_id": result.tool_id,
                    "message": f"⚠️ 缺失工具: {result.tool_name}",
                    "severity": "medium"
                })
            elif result.status == "error":
                analysis["alerts"].append({
                    "type": "detection_error", 
                    "tool_name": result.tool_name,
                    "tool_id": result.tool_id,
                    "message": f"❌ 检测错误: {result.tool_name}",
                    "severity": "high"
                })
        
        return analysis
    
    def generate_report(self, results: List[DetectionResult], analysis: Dict, output_dir: str = "reports") -> str:
        """生成检测报告"""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = Path(output_dir) / f"detection_report_{timestamp}.json"
        
        report_data = {
            "report_info": {
                "timestamp": timestamp,
                "version": "1.0",
                "detector_config": {
                    "model": self.config.model_name,
                    "confidence_threshold": self.config.confidence_threshold,
                    "uncertainty_threshold": self.config.uncertainty_threshold
                }
            },
            "detection_results": [
                {
                    "tool_id": r.tool_id,
                    "tool_name": r.tool_name, 
                    "status": r.status,
                    "confidence": round(r.confidence, 4),
                    "bbox": r.bbox,
                    "detection_time": round(r.detection_time, 3),
                    "details": r.details
                }
                for r in results
            ],
            "workspace_analysis": analysis,
            "system_stats": self.stats,
            "recommendations": self._generate_recommendations(analysis, results)
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"📊 检测报告已生成: {report_file}")
        return str(report_file)
    
    def _generate_recommendations(self, analysis: Dict, results: List[DetectionResult]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if analysis["completeness_rate"] < 75:
            recommendations.append("建议检查工具箱组织，确保所有工具都在指定位置")
        
        if analysis["missing_tools"] > 0:
            missing_tools = [r.tool_name for r in results if r.status == "missing"]
            recommendations.append(f"缺失工具需要归位: {', '.join(missing_tools)}")
        
        if analysis["uncertain_tools"] > 2:
            recommendations.append("检测不确定的工具较多，建议改善光照条件或调整工具摆放")
        
        if analysis["confidence_score"] < 0.01:
            recommendations.append("整体检测置信度较低，建议优化图片质量或更新ROI配置")
        
        if analysis["error_tools"] > 0:
            recommendations.append("存在检测错误，建议检查系统配置和图片质量")
        
        return recommendations

def main():
    """主函数 - 生产级工具检测系统示例"""
    print("🏭 生产级工具检测系统")
    print("=" * 60)
    
    # 系统配置
    config = SystemConfig(
        model_name="ViT-B-32",
        confidence_threshold=0.0001,  # 接近零的阈值，确保所有工具都被识别
        uncertainty_threshold=-0.0003,  # 更严格的缺失判断
        save_roi_images=True,
        enable_alerts=True,
        log_level="INFO"
    )
    
    # 初始化检测器
    detector = ProductionToolDetector(config)
    
    try:
        # 加载工作空间配置
        workspace_config = detector.load_workspace_configuration("instances_default.json")
        
        # 运行检测
        results = detector.run_full_detection("test.jpg", workspace_config)
        
        # 分析结果
        analysis = detector.analyze_workspace_status(results)
        
        # 生成报告
        report_file = detector.generate_report(results, analysis)
        
        # 显示结果摘要
        print(f"\n🎯 检测结果摘要:")
        print(f"  总工具数: {analysis['total_tools']}")
        print(f"  在位工具: {analysis['present_tools']} ✅")
        print(f"  缺失工具: {analysis['missing_tools']} ❌")
        print(f"  不确定: {analysis['uncertain_tools']} 🤔")
        print(f"  错误: {analysis['error_tools']} ⚠️")
        print(f"  完整性: {analysis['completeness_rate']:.1f}%")
        print(f"  整体状态: {analysis['overall_status']}")
        print(f"  报告文件: {report_file}")
        
        # 显示警报
        if analysis["alerts"]:
            print(f"\n🚨 系统警报:")
            for alert in analysis["alerts"]:
                print(f"  {alert['message']}")
        
        return results, analysis
        
    except Exception as e:
        detector.logger.error(f"❌ 系统运行失败: {e}")
        raise

if __name__ == "__main__":
    results, analysis = main()