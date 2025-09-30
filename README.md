# 工具检测系统# 🔧 智能工具检测系统



基于CLIP模型的工具检测系统，用于检测工具箱中缺失的工具。基于CLIP和ROI技术的生产级工具识别与监控系统。



## 核心文件## ✨ 核心特性



### 主要代码- 🤖 **AI驱动**: 基于OpenAI CLIP模型的零样本学习

- `simple_cli.py` - 命令行工具（主要使用接口）- 🎯 **精确检测**: ROI区域定位，支持9种工具类型

- `production_tool_detector.py` - 基于标注数据的精确检测器- 📡 **实时监控**: 定时检测、状态告警、历史记录

- `simple_image_detector.py` - 简单图片分类检测器- 🌐 **多接口**: Web API、命令行工具、Python SDK

- 📊 **智能分析**: 详细报告和统计分析

### 配置文件

- `instances_default.json` - 工具箱标注数据（9种工具的位置信息）## 🚀 快速开始

- `requirements.txt` - Python依赖包

### 系统要求

### 测试图片- Python 3.8+

- `test.jpg` - 完整工具箱图片（所有工具在位）- 4GB+ 内存

- `test2.jpg` - 测试图片2- macOS, Linux, Windows

- `test3.jpg` - 测试图片3

### 安装

## 使用方法```bash

# 自动安装 (推荐)

### 1. 简单工具分类chmod +x install.sh

```bash./install.sh

python simple_cli.py detect test.jpg

```# 手动安装

- 快速识别图片中的主要工具类型python3 -m venv venv

source venv/bin/activate  # Linux/macOS

### 2. 工具箱缺失检测（推荐）pip install -r requirements.txt

```bash```

python simple_cli.py check test.jpg

```### 基本使用

- 基于精确标注，检测具体缺失哪些工具```bash

- 显示每个工具的在位状态# 命令行检测

- 计算工具箱完整性百分比python simple_cli.py detect test.jpg



## 支持的工具类型# 完整检测系统

python production_tool_detector.py

1. hammer - 锤子

2. flat_screwdriver - 一字螺丝刀# Web服务 (需安装flask)

3. cross_screwdriver - 十字螺丝刀python web_api.py

4. cutter - 切割工具# 访问 http://localhost:5000

5. tape_measure - 卷尺```

6. hex_key_set - 六角扳手套装

7. screw_box - 螺丝盒## 🔧 支持的工具

8. pliers - 钳子

9. wrench - 扳手- hammer (锤子)

- flat_screwdriver (平头螺丝刀)  

## 输出示例- cross_screwdriver (十字螺丝刀)

- cutter (切割刀)

```- tape_measure (卷尺)

=== 工具检测结果 ===- hex_key_set (内六角扳手组)

hammer          ✅ present    (置信度: +0.0030)- screw_box (螺丝盒)

flat_screwdriver ✅ present    (置信度: +0.0024)- pliers (钳子)

...- wrench (扳手)



=== 工具箱状态摘要 ===## 📋 命令行工具

总工具数: 9

在位工具: 9 ✅```bash

缺失工具: 0 ❌# 查看系统状态

完整性: 100.0%python simple_cli.py status

整体状态: excellent

# 检测工具

🎉 所有工具都在工具箱中!python simple_cli.py detect image.jpg

```

# 工作空间信息

## 安装依赖python simple_cli.py workspace instances_default.json



```bash# 查看报告

pip install -r requirements.txtpython simple_cli.py reports

``````



## 技术说明## 🌐 Web API



- 使用OpenAI CLIP ViT-B-32模型进行视觉-语言理解启动Web服务后，可用端点：

- 基于COCO格式的标注数据进行精确区域检测

- 支持CPU运行，无需GPU- `GET /api/status` - 系统状态
- `POST /api/detect` - 检测工具
- `GET /api/reports` - 报告列表

## 📁 文件结构

```
observer/
├── production_tool_detector.py  # 核心检测引擎
├── simple_cli.py               # 简化CLI工具
├── web_api.py                  # Web API服务
├── realtime_monitor.py         # 实时监控系统
├── instances_default.json      # 工作空间配置
├── test.jpg                    # 测试图片
├── requirements.txt            # 依赖列表
└── install.sh                 # 安装脚本
```

## ⚙️ 配置说明

### 系统配置
```python
from production_tool_detector import SystemConfig

config = SystemConfig(
    confidence_threshold=0.005,   # 置信度阈值
    save_roi_images=False,        # 是否保存ROI图片
    log_level="INFO"             # 日志级别
)
```

### 工作空间配置
`instances_default.json` 使用标准COCO格式，包含工具位置和类别信息。

## 📊 检测结果

系统输出四种工具状态：
- ✅ `present` - 工具在位
- ❌ `missing` - 工具缺失  
- 🤔 `uncertain` - 状态不确定
- ⚠️ `error` - 检测错误

## 🛠️ 故障排除

### 常见问题
1. **依赖安装失败**: 确保Python版本3.8+，尝试更新pip
2. **检测准确率低**: 调整confidence_threshold参数
3. **内存不足**: 使用CPU模式，设置较小的图片分辨率

### 性能优化
```bash
# 检查GPU支持
python -c "import torch; print(torch.cuda.is_available())"

# 监控系统资源
top -p $(pgrep -f python)
```

## 📞 技术支持

如遇问题，请检查：
1. 系统日志: `logs/tool_detection.log`
2. 依赖版本: `pip list`
3. 系统状态: `python simple_cli.py status`

---

## 🎉 开始使用

```bash
# 立即体验
python simple_cli.py detect test.jpg
```

基于CLIP的智能工具检测，让工具管理更智能！