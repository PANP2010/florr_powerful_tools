#!/bin/bash
# Kaggle API 自动配置脚本

echo "=========================================="
echo "Kaggle API 配置工具"
echo "=========================================="
echo ""

# 检查 kaggle.json 是否已配置
if [ -f ~/.kaggle/kaggle.json ]; then
    echo "✓ kaggle.json 已配置"
    echo ""
    ls -la ~/.kaggle/kaggle.json
    echo ""
    
    # 验证权限
    PERMS=$(stat -f "%Lp" ~/.kaggle/kaggle.json 2>/dev/null || stat -c "%a" ~/.kaggle/kaggle.json 2>/dev/null)
    if [ "$PERMS" = "600" ]; then
        echo "✓ 权限正确 (600)"
    else
        echo "⚠ 权限不正确，正在修复..."
        chmod 600 ~/.kaggle/kaggle.json
        echo "✓ 权限已修复"
    fi
    
    echo ""
    echo "测试连接..."
    kaggle competitions list > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✓ API 连接成功"
        echo ""
        echo "配置信息:"
        kaggle config view
    else
        echo "✗ API 连接失败，请检查 Token 是否有效"
    fi
    
    exit 0
fi

# 查找下载的 kaggle.json
echo "查找 kaggle.json..."
KAGGLE_JSON=$(find ~/Downloads -name "kaggle.json" 2>/dev/null | head -1)

if [ -z "$KAGGLE_JSON" ]; then
    echo ""
    echo "❌ 未找到 kaggle.json 文件"
    echo ""
    echo "请先下载 API Token:"
    echo "  1. 访问 https://www.kaggle.com/settings"
    echo "  2. 滚动到 'API' 部分"
    echo "  3. 点击 'Create New API Token'"
    echo "  4. 下载 kaggle.json"
    echo "  5. 重新运行此脚本"
    echo ""
    echo "或手动配置:"
    echo "  mkdir -p ~/.kaggle"
    echo "  mv ~/Downloads/kaggle.json ~/.kaggle/"
    echo "  chmod 600 ~/.kaggle/kaggle.json"
    exit 1
fi

# 配置
echo "✓ 找到文件: $KAGGLE_JSON"
echo ""
echo "正在配置..."

# 创建目录
mkdir -p ~/.kaggle

# 移动文件
mv "$KAGGLE_JSON" ~/.kaggle/

# 设置权限
chmod 600 ~/.kaggle/kaggle.json

echo "✓ 配置完成!"
echo ""

# 验证
echo "验证配置:"
ls -la ~/.kaggle/kaggle.json
echo ""

echo "测试连接..."
kaggle competitions list > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ API 连接成功"
    echo ""
    echo "配置信息:"
    kaggle config view
else
    echo "⚠ API 连接测试失败，但配置已完成"
    echo "请检查 Token 是否有效"
fi

echo ""
echo "=========================================="
echo "✓ Kaggle API 配置完成!"
echo "=========================================="
echo ""
echo "下一步:"
echo "  ./upload_to_kaggle.sh  # 上传数据集"
