# Florr.io Knowledge Base

自动更新的 Florr.io 游戏知识库组件。

## 功能

- 自动从 Wiki 获取游戏数据
- 增量更新，避免重复下载
- 自动分类索引
- 搜索和查询接口
- 排除二创/同人内容

## 安装

```bash
pip install -r requirements.txt
```

## 使用方法

### 命令行

```bash
cd scripts

# 增量更新 (默认)
python knowledge_base.py update

# 全量更新
python knowledge_base.py update --full

# 搜索
python knowledge_base.py search --query "ant"

# 按分类搜索
python knowledge_base.py search --query "ant" --category mobs

# 获取单个条目
python knowledge_base.py get --query "Baby Ant"

# 查看统计
python knowledge_base.py stats
```

### Python API

```python
from knowledge_base import FlorrKnowledgeBase

# 初始化
kb = FlorrKnowledgeBase("./data")

# 更新知识库
kb.update()

# 搜索
results = kb.search("ant")
for entry in results:
    print(entry.title, entry.url)

# 按分类搜索
mobs = kb.search("", category="mobs")

# 获取单个条目
entry = kb.get_entry("Baby Ant")
print(entry.content)

# 获取统计信息
stats = kb.get_stats()
```

## 数据结构

```
data/
├── wiki.json      # 所有条目数据
├── index.json     # 分类索引
└── metadata.json  # 元数据 (更新时间、统计等)
```

## 分类

| 分类 | 说明 |
|------|------|
| mobs | 怪物 (Ant, Bee, Beetle 等) |
| petals | 花瓣 (Air, Ankh, Basic 等) |
| areas | 区域 (Garden, Desert, Ocean 等) |
| mechanics | 机制 (AFK, Armor, Crafting 等) |
| other | 其他 |

## 自动排除

以下内容会被自动排除：
- 模板页面
- 用户页面
- 二创/同人内容
- 概念/建议页面
- 愚人节/恶搞内容
