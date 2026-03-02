#!/bin/bash
# 打包训练所需文件用于上传到服务器

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="$PROJECT_DIR/train_package"

echo "=== 打包训练文件 ==="

rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

echo "复制训练脚本..."
cp "$SCRIPT_DIR/train_mob_detector_v4_server.py" "$OUTPUT_DIR/train.py"

echo "复制数据集..."
cp -r "$PROJECT_DIR/data/synthetic_mobs_v4" "$OUTPUT_DIR/data"

echo "复制预训练权重..."
cp "$PROJECT_DIR/yolov8n.pt" "$OUTPUT_DIR/"

echo "创建 README..."
cat > "$OUTPUT_DIR/README.txt" << 'EOF'
=== 训练环境要求 ===
- Python 3.8+
- PyTorch 2.0+ with CUDA
- ultralytics

=== 安装依赖 ===
pip install torch torchvision ultralytics

=== 运行训练 ===
python train.py --data ./data/data.yaml --epochs 80 --batch 64

=== 参数说明 ===
--data    数据集配置文件路径
--epochs  训练轮数 (默认 80)
--batch   单卡 batch size (默认 64，双卡总 batch=128)
--imgsz   图像尺寸 (默认 640)

=== 输出 ===
模型保存在 ./runs/mob_detector_v4/weights/
- best.pt  最佳模型
- last.pt  最后一轮模型
EOF

echo "压缩打包..."
cd "$PROJECT_DIR"
tar -czvf train_package.tar.gz -C "$OUTPUT_DIR" .

echo ""
echo "=== 打包完成 ==="
echo "输出文件: $PROJECT_DIR/train_package.tar.gz"
echo "大小: $(du -h "$PROJECT_DIR/train_package.tar.gz" | cut -f1)"
