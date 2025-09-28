"""
最基础的 CLIP 测试 - 理解 CLIP 如何工作
"""
import torch
import open_clip
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import os

def test_clip_basic():
    """测试 CLIP 的基本功能"""
    print("正在加载 CLIP 模型...")
    
    # 1. 加载模型（第一次会下载，需要网络）
    model, _, preprocess = open_clip.create_model_and_transforms(
        'ViT-B-32', 
        pretrained='openai'
    )
    tokenizer = open_clip.get_tokenizer('ViT-B-32')
    
    # 设置设备
    device = "cpu"  # Intel Mac 用 CPU
    model.to(device)
    model.eval()
    
    print("模型加载完成！")
    
    # 2. 准备测试文本
    test_texts = [
        "a screwdriver on a table",
        "an empty table with no tools", 
        "a hammer on a table",
        "a wrench on a table"
    ]
    
    print("\n文本描述列表:")
    for i, text in enumerate(test_texts):
        print(f"{i+1}. {text}")
    
    # 3. 编码文本
    text_tokens = tokenizer(test_texts).to(device)
    
    with torch.no_grad():
        text_features = model.encode_text(text_tokens)
        # 标准化
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)
    
    print(f"\n文本特征形状: {text_features.shape}")
    return model, preprocess, tokenizer, text_features, test_texts

def test_with_image(model, preprocess, text_features, test_texts, image_path):
    """测试图片与文本的相似度"""
    print(f"\n正在测试图片: {image_path}")
    
    try:
        # 1. 加载和预处理图片
        image = Image.open(image_path).convert('RGB')
        image_input = preprocess(image).unsqueeze(0)
        
        # 2. 编码图片
        with torch.no_grad():
            image_features = model.encode_image(image_input)
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        
        # 3. 计算相似度
        similarities = (image_features @ text_features.T).softmax(dim=-1)
        
        # 4. 显示结果
        print("\n相似度结果:")
        for i, (text, sim) in enumerate(zip(test_texts, similarities[0])):
            print(f"{text}: {sim.item():.4f}")
        
        # 找出最匹配的描述
        best_match_idx = similarities.argmax().item()
        print(f"\n最匹配的描述: {test_texts[best_match_idx]} ({similarities[0][best_match_idx]:.4f})")
        
        return similarities
        
    except Exception as e:
        print(f"处理图片时出错: {e}")
        return None

def create_sample_image():
    """创建一个简单的示例图片用于测试"""
    from PIL import Image, ImageDraw, ImageFont
    
    # 创建一个白色背景的图片
    img = Image.new('RGB', (400, 300), color='white')
    draw = ImageDraw.Draw(img)
    
    # 画一个桌子（矩形）
    draw.rectangle([50, 200, 350, 250], fill='brown', outline='black', width=2)
    
    # 画一个螺丝刀（简化的线条）
    draw.rectangle([150, 170, 250, 180], fill='yellow', outline='black', width=1)  # 手柄
    draw.rectangle([250, 175, 280, 178], fill='gray', outline='black', width=1)    # 螺丝刀头
    
    # 添加文字说明
    try:
        # 尝试使用默认字体
        draw.text((150, 260), "Test: Screwdriver on table", fill='black')
    except:
        # 如果默认字体不可用，跳过文字
        pass
    
    # 保存图片
    sample_path = "data/images/sample_screwdriver.png"
    img.save(sample_path)
    print(f"已创建示例图片: {sample_path}")
    return sample_path

if __name__ == "__main__":
    print("=== CLIP 基础测试 ===")
    
    # 确保图片目录存在
    os.makedirs("data/images", exist_ok=True)
    
    # 加载模型
    model, preprocess, tokenizer, text_features, test_texts = test_clip_basic()
    
    # 创建示例图片
    sample_image = create_sample_image()
    
    # 自动测试示例图片
    print("\n" + "="*50)
    print("自动测试示例图片...")
    print("="*50)
    test_with_image(model, preprocess, text_features, test_texts, sample_image)
    
    # 提示用户可以测试其他图片
    print("\n" + "="*50)
    print("您也可以测试自己的图片！")
    print("请准备一张测试图片，比如：")
    print("1. 桌上有螺丝刀的图片")
    print("2. 空桌子的图片") 
    print("3. 桌上有其他工具的图片")
    print("="*50)
    
    # 等待用户输入图片路径
    while True:
        image_path = input("\n请输入图片路径 (或按 q 退出): ").strip()
        if image_path.lower() == 'q':
            break
        
        if image_path and len(image_path) > 0:
            if os.path.exists(image_path):
                test_with_image(model, preprocess, text_features, test_texts, image_path)
            else:
                print("文件不存在，请检查路径是否正确")
        else:
            print("请输入有效的图片路径")
    
    print("\n测试结束，感谢使用！")