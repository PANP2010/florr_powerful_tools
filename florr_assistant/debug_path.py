from pathlib import Path
import os

print("当前工作目录:", os.getcwd())
print("__file__:", __file__)

base_dir = Path(__file__).parent.parent
print("base_dir:", base_dir)
print("base_dir.resolve():", base_dir.resolve())

model_path = base_dir / 'models' / 'mob_detector.pt'
print("model_path:", model_path)
print("model_path.exists():", model_path.exists())

resolved = model_path.resolve()
print("resolved:", resolved)
print("resolved.exists():", resolved.exists())

print("\n列出models目录:")
models_dir = base_dir / 'models'
if models_dir.exists():
    for f in models_dir.iterdir():
        print(f"  {f.name}: exists={f.exists()}, is_symlink={f.is_symlink()}")
        if f.is_symlink():
            print(f"    -> {f.resolve()}")
