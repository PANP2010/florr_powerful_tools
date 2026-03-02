"""
验证训练好的模型 - 测试图3
"""

import sys
from pathlib import Path
import cv2
from ultralytics import YOLO


def main():
    print("\n🔍 验证模型 - 测试图3\n")
    print("=" * 60)
    
    model_path = Path("/Users/panjiyang/Documents/trae_projects/florr_powerful_tools/data/runs/mob_detector_v3_mps/weights/best.pt")
    
    print(f"模型路径: {model_path}")
    
    model = YOLO(str(model_path))
    print(f"✓ 模型加载成功! 类别数: {len(model.names)}")
    
    image_path = Path("/Users/panjiyang/Documents/trae_projects/florr_powerful_tools/florr-auto-framework-pytorch/测试图3.png")
    print(f"\n测试图片: {image_path}")
    
    image = cv2.imread(str(image_path))
    if image is None:
        print("无法读取图片!")
        return False
    print(f"图片尺寸: {image.shape}")
    
    print("\n运行检测...")
    results = model(image, verbose=True, imgsz=640, conf=0.25)
    
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
    
    output_path = Path("/Users/panjiyang/Documents/trae_projects/florr_powerful_tools/florr-auto-framework-pytorch/测试图3_结果.png")
    cv2.imwrite(str(output_path), image)
    
    print("\n" + "=" * 60)
    print("检测结果汇总")
    print("=" * 60)
    
    mob_counts = {}
    for det in detections:
        name = det['class_name']
        mob_counts[name] = mob_counts.get(name, 0) + 1
    
    for mob_name, count in sorted(mob_counts.items()):
        print(f"  {mob_name}: {count}个")
    
    print(f"\n共检测到 {len(detections)} 个对象")
    print(f"\n结果已保存: {output_path}")
    
    return True


if __name__ == '__main__':
    main()
