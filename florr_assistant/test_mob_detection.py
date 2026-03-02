"""
测试怪物检测 - 切片检测 + 低置信度
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import cv2
import numpy as np
from ultralytics import YOLO


def slice_detect(model, image, slice_size=320, overlap=0.3, conf=0.15):
    h, w = image.shape[:2]
    detections = {}
    
    step = int(slice_size * (1 - overlap))
    
    for y in range(0, h - slice_size + 1, step):
        for x in range(0, w - slice_size + 1, step):
            slice_img = image[y:y+slice_size, x:x+slice_size]
            
            results = model(slice_img, verbose=False, imgsz=320, conf=conf)
            
            for result in results:
                boxes = result.boxes
                if boxes is not None and len(boxes) > 0:
                    for box in boxes:
                        confidence = float(box.conf[0])
                        class_id = int(box.cls[0])
                        class_name = result.names.get(class_id, 'unknown')
                        
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        
                        global_x1 = x + x1
                        global_y1 = y + y1
                        global_x2 = x + x2
                        global_y2 = y + y2
                        
                        if class_name not in detections:
                            detections[class_name] = []
                        detections[class_name].append({
                            'confidence': confidence,
                            'bbox': (global_x1, global_y1, global_x2, global_y2)
                        })
    
    return detections


def merge_detections(detections, iou_threshold=0.3):
    merged = {}
    
    for mob_name, dets in detections.items():
        if len(dets) == 0:
            continue
        
        dets_sorted = sorted(dets, key=lambda x: x['confidence'], reverse=True)
        
        keep = []
        for det in dets_sorted:
            should_keep = True
            for kept in keep:
                iou = calculate_iou(det['bbox'], kept['bbox'])
                if iou > iou_threshold:
                    should_keep = False
                    break
            if should_keep:
                keep.append(det)
        
        merged[mob_name] = keep
    
    return merged


def calculate_iou(box1, box2):
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    
    union = area1 + area2 - inter
    
    return inter / union if union > 0 else 0


def main():
    print("\n🔍 怪物检测测试 - 切片检测 + 低置信度\n")
    print("=" * 60)
    
    base_dir = Path(__file__).parent
    model_path = base_dir / 'models' / 'mob_detector.pt'
    
    print(f"模型路径: {model_path}")
    
    model = YOLO(str(model_path))
    print(f"✓ 模型加载成功! 类别数: {len(model.names)}")
    
    image_path = base_dir.parent / 'florr-auto-framework-pytorch' / 'mob检测测试图.png'
    print(f"\n测试图片: {image_path}")
    
    image = cv2.imread(str(image_path))
    print(f"图片尺寸: {image.shape}")
    
    print("\n运行切片检测 (切片=320, 重叠=30%, 置信度=0.15)...")
    
    detections = slice_detect(model, image, slice_size=320, overlap=0.3, conf=0.15)
    
    merged = merge_detections(detections, iou_threshold=0.3)
    
    print("\n" + "=" * 60)
    print("检测结果汇总 (合并后)")
    print("=" * 60)
    
    target_mobs = {
        'ladybug': 2,
        'bee': 4,
        'ant_worker': 2,
        'ant_baby': (2, 3)
    }
    
    all_mobs = {}
    for mob_name, dets in sorted(merged.items()):
        count = len(dets)
        if count > 0:
            avg_conf = sum(d['confidence'] for d in dets) / count
            all_mobs[mob_name] = count
            status = ""
            if mob_name in target_mobs:
                status = f" (目标: {target_mobs[mob_name]})"
            print(f"  {mob_name}: {count}个, 平均置信度: {avg_conf:.2f}{status}")
    
    if not all_mobs:
        print("  (未检测到任何对象)")
    
    print("\n" + "=" * 60)
    print("目标检测验证")
    print("=" * 60)
    
    results_check = []
    
    ladybug_count = all_mobs.get('ladybug', 0)
    ladybug_ok = ladybug_count == 2
    results_check.append(('ladybug', 2, ladybug_count, ladybug_ok))
    
    bee_count = all_mobs.get('bee', 0)
    bee_ok = bee_count == 4
    results_check.append(('bee', 4, bee_count, bee_ok))
    
    ant_worker_count = all_mobs.get('ant_worker', 0)
    ant_worker_ok = ant_worker_count == 2
    results_check.append(('ant_worker', 2, ant_worker_count, ant_worker_ok))
    
    ant_baby_count = all_mobs.get('ant_baby', 0)
    ant_baby_ok = 2 <= ant_baby_count <= 3
    results_check.append(('ant_baby', '2-3', ant_baby_count, ant_baby_ok))
    
    all_passed = True
    for name, target, actual, passed in results_check:
        status = "✓" if passed else "✗"
        print(f"  {status} {name}: 目标={target}, 检测={actual}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有目标检测成功!")
    else:
        print("⚠️ 部分目标检测不符合预期")
        print("\n注意: 当前模型使用单独怪物图片训练，无法很好地从完整游戏截图中检测怪物")
        print("建议: 使用完整游戏截图重新训练模型")
    print("=" * 60)
    
    return all_passed


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
