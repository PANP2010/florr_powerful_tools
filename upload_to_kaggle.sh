#!/bin/bash
# Kaggle 数据集快速上传脚本

set -e

# 配置
USERNAME="PANP2010"  # 修改为您的 Kaggle 用户名
DATASET_NAME="florr-mob-training-package"
DATASET_TITLE="Florr Mob Training Package - YOLO26s"

echo "=========================================="
echo "Kaggle 数据集上传工具"
echo "=========================================="
echo ""

# 检查 kaggle.json
if [ ! -f ~/.kaggle/kaggle.json ]; then
    echo "❌ 错误: 未找到 kaggle.json"
    echo ""
    echo "请先配置 Kaggle API:"
    echo "1. 访问 https://www.kaggle.com/settings"
    echo "2. 点击 'Create New API Token'"
    echo "3. 下载 kaggle.json"
    echo "4. 运行: mkdir -p ~/.kaggle && mv ~/Downloads/kaggle.json ~/.kaggle/"
    echo "5. 运行: chmod 600 ~/.kaggle/kaggle.json"
    exit 1
fi

echo "✓ 找到 kaggle.json"

# 检查数据集目录
if [ ! -d "upload_package" ]; then
    echo "❌ 错误: 未找到 upload_package 目录"
    echo ""
    echo "请先解压训练包:"
    echo "  tar -xzf florr_mob_detector_training_package.tar.gz"
    exit 1
fi

echo "✓ 找到 upload_package 目录"

# 进入目录
cd upload_package

# 创建元数据
if [ ! -f "dataset-metadata.json" ]; then
    echo ""
    echo "创建数据集元数据..."
    cat > dataset-metadata.json << EOF
{
  "title": "${DATASET_TITLE}",
  "id": "${USERNAME}/${DATASET_NAME}",
  "licenses": [
    {
      "name": "CC0-1.0"
    }
  ],
  "keywords": [
    "computer-vision",
    "object-detection",
    "yolo",
    "game",
    "florr"
  ],
  "collaborators": [],
  "data": []
}
EOF
    echo "✓ 创建 dataset-metadata.json"
else
    echo "✓ dataset-metadata.json 已存在"
fi

# 检查数据集是否已存在
echo ""
echo "检查数据集是否已存在..."
if kaggle datasets view "${USERNAME}/${DATASET_NAME}" 2>/dev/null; then
    echo "✓ 数据集已存在，将更新版本"
    
    echo ""
    echo "更新数据集..."
    kaggle datasets version -p . -m "Updated: $(date '+%Y-%m-%d %H:%M:%S')"
    
    echo ""
    echo "=========================================="
    echo "✓ 数据集更新成功!"
    echo "=========================================="
else
    echo "✗ 数据集不存在，将创建新数据集"
    
    echo ""
    echo "创建数据集..."
    kaggle datasets create -p . --public
    
    echo ""
    echo "=========================================="
    echo "✓ 数据集创建成功!"
    echo "=========================================="
fi

echo ""
echo "📦 数据集信息:"
echo "  名称: ${DATASET_TITLE}"
echo "  ID: ${USERNAME}/${DATASET_NAME}"
echo "  链接: https://www.kaggle.com/datasets/${USERNAME}/${DATASET_NAME}"
echo ""
echo "🎯 下一步:"
echo "  1. 访问 https://www.kaggle.com/code"
echo "  2. 点击 'New Notebook'"
echo "  3. 设置 Accelerator: GPU P100"
echo "  4. 添加数据集: ${DATASET_NAME}"
echo "  5. 上传 kaggle_notebook_template.ipynb"
echo "  6. 运行训练"
echo ""
