"""
快速验证当前训练模型
"""

import sys
from pathlib import Path
import cv2
from ultralytics import YOLO


def main():
    print("\n🔍 快速验证当前模型\n")
    
    model_path = Path("/Users/panjiyang/Documents/trae_projects/florr_powerful_tools/data/runs/mob_detector_v3_mps3/weights/best.pt")
    
    if not model_path.exists():
        print(f"模型不存在: {model_path}")
        return False
    
    print(f"模型: {model_path}")
    
    model = YOLO(str(model_path))
    
    image_path = Path("/Users/panjiyang/Documents/trae_projects/florr_powerful_tools/florr-auto-framework-pytorch/mob检测测试图.png")
    image = cv2.imread(str(image_path))
    
    results = model(image, verbose=False, imgsz=640, conf=0.25)
    
    colors = {
        'ladybug': (0, 255, 0),
        'bee': (0, 255, 255),
        'ant_worker': (255, 0, 0),
        'ant_baby': (255, 0, 255),
        'centipede': (255, 255, 0),
        'default': (128, 128, 128)
    }
    
    detections = {}
    for result in results:
        boxes = result.boxes
        if boxes is not None and len(boxes) > 0:
            for box in boxes:
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = result.names.get(class_id, 'unknown')
                
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                
                detections[class_name] = detections.get(class_name, 0) + 1
                
                color = colors.get(class_name, colors['default'])
                cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
                
                label = f"{class_name} {confidence:.2f}"
                cv2.putText(image, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    output_path = Path("/Users/panjiyang/Documents/trae_projects/florr_powerful_tools/florr-auto-framework-pytorch/mob检测测试图_结果_v2.png")
    cv2.imwrite(str(output_path), image)
    
    print("\n检测结果:")
    for mob_name, count in sorted(detections.items()):
        print(f"  {mob_name}: {count}个")
    
    print(f"\n共检测到 {sum(detections.values())} 个对象")
    print(f"结果已保存: {output_path}")
    
    target = {'ladybug': 2, 'bee': 4, 'ant_worker': 2, 'ant_baby': (2, 3)}
    print("\n目标验证:")
    for name, tgt in target.items():
        actual = detections.get(name, 0)
        if isinstance(tgt, tuple):
            ok = tgt[0] <= actual <= tgt[1]
        else:
            ok = actual == tgt
        status = "✓" if ok else "✗"
        print(f"  {status} {name}: 目标={tgt}, 检测={actual}")
    
    return True


if __name__ == '__main__':
    main()
