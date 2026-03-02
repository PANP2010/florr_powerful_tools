"""
验证V4模型 - 所有测试图
"""

import sys
from pathlib import Path
import cv2
from ultralytics import YOLO


def test_image(model, image_path, output_path, target_mobs=None):
    print(f"\n测试: {image_path.name}")
    print("-" * 40)
    
    image = cv2.imread(str(image_path))
    if image is None:
        print(f"无法读取图片!")
        return None
    
    print(f"图片尺寸: {image.shape}")
    
    results = model(image, verbose=False, imgsz=640, conf=0.25)
    
    colors = {
        'ladybug': (0, 255, 0),
        'bee': (0, 255, 255),
        'ant_worker': (255, 0, 0),
        'ant_baby': (255, 0, 255),
        'hornet': (255, 100, 0),
        'spider': (100, 100, 255),
        'centipede': (255, 255, 0),
        'beetle': (255, 100, 0),
        'jellyfish': (255, 0, 100),
        'starfish': (0, 255, 100),
        'bubble': (100, 255, 255),
        'crab': (255, 100, 100),
        'fly': (200, 200, 0),
        'wasp': (0, 165, 255),
        'bumble_bee': (255, 200, 0),
        'ant_soldier': (0, 165, 255),
        'default': (128, 128, 128)
    }
    
    detections = []
    
    for result in results:
        boxes = result.boxes
        if boxes is not None and len(boxes) > 0:
            for box in boxes:
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = result.names.get(class_id, 'unknown')
                
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                
                detections.append({
                    'class_name': class_name,
                    'confidence': confidence,
                    'bbox': (x1, y1, x2, y2)
                })
                
                color = colors.get(class_name, colors['default'])
                
                line_thickness = max(2, int(image.shape[1] / 500))
                cv2.rectangle(image, (x1, y1), (x2, y2), color, line_thickness)
                
                label = f"{class_name} {confidence:.2f}"
                
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = max(1.0, image.shape[1] / 1000)
                thickness = max(2, int(image.shape[1] / 600))
                
                (text_width, text_height), baseline = cv2.getTextSize(label, font, font_scale, thickness)
                
                cv2.rectangle(image, (x1, y1 - text_height - 15), (x1 + text_width + 15, y1), color, -1)
                
                cv2.putText(image, label, (x1 + 8, y1 - 8), font, font_scale, (255, 255, 255), thickness)
    
    cv2.imwrite(str(output_path), image)
    
    mob_counts = {}
    for det in detections:
        name = det['class_name']
        mob_counts[name] = mob_counts.get(name, 0) + 1
    
    print(f"检测到 {len(detections)} 个对象:")
    for mob_name, count in sorted(mob_counts.items()):
        print(f"  {mob_name}: {count}个")
    
    if target_mobs:
        print("\n目标验证:")
        all_passed = True
        for name, target in target_mobs.items():
            actual = mob_counts.get(name, 0)
            if isinstance(target, tuple):
                passed = target[0] <= actual <= target[1]
            else:
                passed = actual == target
            status = "✓" if passed else "✗"
            print(f"  {status} {name}: 目标={target}, 检测={actual}")
            if not passed:
                all_passed = False
        return all_passed
    
    return True


def main():
    print("\n" + "=" * 60)
    print("验证V4模型 - 所有测试图")
    print("=" * 60)
    
    model_path = Path("/Users/panjiyang/Documents/trae_projects/florr_powerful_tools/data/runs/mob_detector_v4/weights/best.pt")
    
    print(f"\n模型: {model_path}")
    
    model = YOLO(str(model_path))
    print(f"类别数: {len(model.names)}")
    
    base_dir = Path("/Users/panjiyang/Documents/trae_projects/florr_powerful_tools/florr-auto-framework-pytorch")
    
    test_cases = [
        {
            'image': 'mob检测测试图.png',
            'output': 'mob检测测试图_结果_v4.png',
            'target': {'ladybug': 2, 'bee': 4, 'ant_worker': 2, 'ant_baby': (2, 3)}
        },
        {
            'image': '测试图2.png',
            'output': '测试图2_结果_v4.png',
            'target': {'hornet': 3, 'spider': 1}
        },
        {
            'image': '测试图3.png',
            'output': '测试图3_结果_v4.png',
            'target': None
        }
    ]
    
    results_summary = []
    
    for test_case in test_cases:
        image_path = base_dir / test_case['image']
        output_path = base_dir / test_case['output']
        
        if not image_path.exists():
            print(f"\n跳过: {test_case['image']} 不存在")
            continue
        
        passed = test_image(model, image_path, output_path, test_case['target'])
        results_summary.append({
            'image': test_case['image'],
            'passed': passed
        })
    
    print("\n" + "=" * 60)
    print("测试汇总")
    print("=" * 60)
    
    for result in results_summary:
        if result['passed'] is not None:
            status = "✓ 通过" if result['passed'] else "✗ 未通过"
            print(f"  {status}: {result['image']}")
        else:
            print(f"  - {result['image']}")
    
    print("=" * 60)


if __name__ == '__main__':
    main()
