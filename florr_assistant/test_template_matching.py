"""
模板匹配怪物检测 - 使用无背景图像作为模板
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import cv2
import numpy as np


class TemplateMobDetector:
    def __init__(self, template_dir: str):
        self.template_dir = Path(template_dir)
        self.templates = {}
        self._load_templates()
    
    def _load_templates(self):
        print(f"加载模板目录: {self.template_dir}")
        
        for template_path in self.template_dir.glob("*.png"):
            if template_path.name.endswith('.disable'):
                continue
            
            mob_name = template_path.stem
            template = cv2.imread(str(template_path), cv2.IMREAD_UNCHANGED)
            
            if template is not None:
                if template.shape[2] == 4:
                    template = template[:, :, :3]
                
                self.templates[mob_name] = template
                print(f"  加载: {mob_name} ({template.shape[1]}x{template.shape[0]})")
        
        print(f"共加载 {len(self.templates)} 个模板")
    
    def detect(self, image, target_mobs=None, scales=None, threshold=0.7):
        if scales is None:
            scales = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.5, 2.0]
        
        detections = {}
        
        templates_to_use = {}
        if target_mobs:
            for mob in target_mobs:
                if mob in self.templates:
                    templates_to_use[mob] = self.templates[mob]
        else:
            templates_to_use = self.templates
        
        for mob_name, template in templates_to_use.items():
            best_matches = []
            
            for scale in scales:
                scaled_template = cv2.resize(
                    template, 
                    None, 
                    fx=scale, 
                    fy=scale,
                    interpolation=cv2.INTER_CUBIC
                )
                
                if scaled_template.shape[0] > image.shape[0] or scaled_template.shape[1] > image.shape[1]:
                    continue
                
                result = cv2.matchTemplate(image, scaled_template, cv2.TM_CCOEFF_NORMED)
                
                locations = np.where(result >= threshold)
                
                for pt in zip(*locations[::-1]):
                    confidence = result[pt[1], pt[0]]
                    h, w = scaled_template.shape[:2]
                    
                    best_matches.append({
                        'confidence': float(confidence),
                        'bbox': (pt[0], pt[1], pt[0] + w, pt[1] + h),
                        'scale': scale
                    })
            
            if best_matches:
                best_matches = self._nms(best_matches, iou_threshold=0.3)
                detections[mob_name] = best_matches
        
        return detections
    
    def _nms(self, detections, iou_threshold=0.3):
        if not detections:
            return []
        
        sorted_dets = sorted(detections, key=lambda x: x['confidence'], reverse=True)
        
        keep = []
        for det in sorted_dets:
            should_keep = True
            for kept in keep:
                iou = self._calculate_iou(det['bbox'], kept['bbox'])
                if iou > iou_threshold:
                    should_keep = False
                    break
            if should_keep:
                keep.append(det)
        
        return keep
    
    def _calculate_iou(self, box1, box2):
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
    print("\n🔍 模板匹配怪物检测测试\n")
    print("=" * 60)
    
    template_dir = Path("/Users/panjiyang/Documents/trae_projects/florr_ai/image/0_no-background/mob/common")
    
    detector = TemplateMobDetector(str(template_dir))
    
    image_path = Path("/Users/panjiyang/Documents/trae_projects/florr_powerful_tools/florr-auto-framework-pytorch/mob检测测试图.png")
    print(f"\n测试图片: {image_path}")
    
    image = cv2.imread(str(image_path))
    print(f"图片尺寸: {image.shape}")
    
    target_mobs = ['ladybug', 'bee', 'ant_worker', 'ant_baby']
    
    print(f"\n目标怪物: {target_mobs}")
    print("运行模板匹配 (多尺度)...")
    
    detections = detector.detect(
        image, 
        target_mobs=target_mobs,
        scales=[0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.5],
        threshold=0.6
    )
    
    print("\n" + "=" * 60)
    print("检测结果汇总")
    print("=" * 60)
    
    target_counts = {
        'ladybug': 2,
        'bee': 4,
        'ant_worker': 2,
        'ant_baby': (2, 3)
    }
    
    all_mobs = {}
    for mob_name, dets in sorted(detections.items()):
        count = len(dets)
        if count > 0:
            avg_conf = sum(d['confidence'] for d in dets) / count
            all_mobs[mob_name] = count
            status = ""
            if mob_name in target_counts:
                status = f" (目标: {target_counts[mob_name]})"
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
    print("=" * 60)
    
    return all_passed


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
