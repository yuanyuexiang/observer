"""
简化的 CLIP 测试 - 避免权限问题
"""
import sys
import os

# 确保在正确的目录
print(f"当前工作目录: {os.getcwd()}")
print(f"Python解释器: {sys.executable}")

try:
    import torch
    print(f"PyTorch版本: {torch.__version__}")
    print("PyTorch导入成功！")
    
    import open_clip
    print("open_clip导入成功！")
    
    from PIL import Image
    print("PIL导入成功！")
    
    # 测试基础功能
    print("\n开始加载模型...")
    model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='openai')
    tokenizer = open_clip.get_tokenizer('ViT-B-32')
    
    # 设置为CPU模式
    device = "cpu"
    model.to(device)
    model.eval()
    print("模型加载成功！")
    
    # 准备测试文本
    test_texts = [
        "a screwdriver on a table",
        "an empty table with no tools"
    ]
    
    print(f"\n测试文本: {test_texts}")
    
    # 编码文本
    text_tokens = tokenizer(test_texts).to(device)
    with torch.no_grad():
        text_features = model.encode_text(text_tokens)
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)
    
    print(f"文本特征形状: {text_features.shape}")
    print("✅ CLIP 基础功能测试通过！")
    
    # 检查图片文件
    img_path = "data/images/sample_screwdriver.png"
    if os.path.exists(img_path):
        print(f"\n找到示例图片: {img_path}")
        
        # 加载图片
        image = Image.open(img_path).convert('RGB')
        image_input = preprocess(image).unsqueeze(0)
        
        # 编码图片
        with torch.no_grad():
            image_features = model.encode_image(image_input)
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        
        # 计算相似度
        similarities = (image_features @ text_features.T).softmax(dim=-1)
        
        print("\n相似度结果:")
        for text, sim in zip(test_texts, similarities[0]):
            print(f"  {text}: {sim.item():.4f}")
        
        best_match_idx = similarities.argmax().item()
        print(f"\n最匹配: {test_texts[best_match_idx]} (置信度: {similarities[0][best_match_idx]:.4f})")
    else:
        print(f"\n未找到示例图片: {img_path}")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()

print("\n测试完成！")