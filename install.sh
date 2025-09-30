#!/bin/bash

# 工具检测系统 - 简化安装脚本

set -e  # 遇到错误时退出

echo "🔧 工具检测系统安装程序"
echo "========================"

# 检查Python版本
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        PIP_CMD="pip3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
        PIP_CMD="pip"
    else
        echo "❌ 错误: 未找到Python。请先安装Python 3.8+"
        exit 1
    fi
    
    # 检查Python版本
    PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
    REQUIRED_VERSION="3.8"
    
    if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
        echo "✅ Python版本: $PYTHON_VERSION"
    else
        echo "❌ 错误: Python版本过低 ($PYTHON_VERSION)，需要 $REQUIRED_VERSION 或更高版本"
        exit 1
    fi
}

# 创建虚拟环境
create_virtual_env() {
    echo "🔄 创建Python虚拟环境..."
    
    if [ ! -d "venv" ]; then
        $PYTHON_CMD -m venv venv
        echo "✅ 虚拟环境创建成功"
    else
        echo "ℹ️  虚拟环境已存在"
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    echo "✅ 虚拟环境已激活"
}

# 安装核心依赖
install_dependencies() {
    echo "📦 安装核心依赖..."
    
    # 升级pip
    $PIP_CMD install --upgrade pip
    
    # 安装核心依赖
    $PIP_CMD install torch open-clip-torch "numpy<2.0.0" pillow
    
    echo "✅ 核心依赖安装完成"
}

# 创建目录结构
create_directories() {
    echo "📁 创建目录结构..."
    
    mkdir -p data/{images,production_rois}
    mkdir -p config
    mkdir -p reports
    mkdir -p logs
    
    echo "✅ 目录结构创建完成"
}

# 运行测试
run_tests() {
    echo "🧪 运行基础测试..."
    
    # 测试核心依赖
    $PYTHON_CMD -c "
try:
    import torch
    import open_clip
    from PIL import Image
    print('✅ 核心依赖测试通过')
except ImportError as e:
    print(f'❌ 依赖测试失败: {e}')
    exit(1)
"
    
    # 如果有测试文件，运行检测测试
    if [ -f "test.jpg" ] && [ -f "instances_default.json" ]; then
        echo "🔍 运行检测测试..."
        $PYTHON_CMD simple_cli.py status
        echo "✅ 系统测试通过"
    fi
}

# 显示使用说明
show_usage() {
    echo ""
    echo "🎉 安装完成！"
    echo "============"
    echo ""
    echo "📋 可用命令:"
    echo ""
    echo "1. 基本检测:"
    echo "   python simple_cli.py detect test.jpg"
    echo "   python simple_cli.py status"
    echo ""
    echo "2. 完整系统:"
    echo "   python production_tool_detector.py"
    echo ""
    echo "3. Web服务 (需要安装flask):"
    echo "   pip install flask flask-cors"
    echo "   python web_api.py"
    echo ""
    echo "📁 重要文件:"
    echo "   - instances_default.json: 工作空间配置"
    echo "   - test.jpg: 测试图片"
    echo "   - simple_cli.py: 命令行工具"
    echo ""
    echo "💡 提示:"
    echo "   激活虚拟环境: source venv/bin/activate"
    echo "   查看状态: python simple_cli.py status"
}

# 主安装流程
main() {
    echo "开始安装核心系统..."
    echo ""
    
    # 执行安装步骤
    check_python
    create_virtual_env
    install_dependencies
    create_directories
    run_tests
    show_usage
    
    echo ""
    echo "🎉 工具检测系统安装完成！"
}

# 运行主函数
main "$@"