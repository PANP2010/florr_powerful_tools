# CLAUDE.md — Florr Powerful Tools

> AI 协作开发规范，基于 Karpathy AI 编程四原则制定。
> 版本：v1.0 | 维护者：@PANP2010

---

## 四条核心原则

### 1. 不确定就问（Think Before Coding）

**行动准则：**
- 涉及游戏逻辑（花瓣生成、碰撞检测、伤害计算）的修改，先确认方向再编码
- 涉及多浏览器环境（Windows/macOS/Linux）的代码，先确认目标平台
- 涉及外网请求（Kaggle API、模型下载）的代码，确认网络可达性和凭证配置
- 不确定 API 版本或参数含义时，先查文档再实现

**必须先提问的场景：**
- "优化性能"——先确认是 CPU 型还是 GPU 型瓶颈
- "修复 bug"——先确认复现条件和复现路径
- "添加新功能"——先确认是否与现有功能重叠
- 改动涉及 3 个以上文件——先陈述改动计划

**示例提问：**
```
在改 AFK 保护之前，先确认：这个是浏览器验证类型变了，还是花瓣检测算法需要调整？
```

---

### 2. 极简优先（Simplicity First）

**行动准则：**
- 不添加需求描述中没有的功能
- 不为跨平台而添加抽象层（如果只在 Windows 运行，只写 Windows 代码）
- 不引入额外依赖（pip install 前先确认是否已有同类依赖）
- 不为"以后可能需要"而添加配置项

**自测问题：** 一个熟悉 Python 的开发者会觉得这过度复杂吗？如果是，简化。

**具体规则：**
- 脚本类工具（download_*.py、setup_*.sh）保持单文件，逻辑不超过 200 行
- 浏览器自动化（auto-*.py）不添加额外的 UI 框架
- 配置文件（config/）只包含实际被代码读取的键，不写空注释占位

---

### 3. 精准改动（Surgical Changes）

**行动准则：**
- 编辑现有代码时，**只改本次任务直接相关的行**
- 不重构相邻代码、不改注释、不调整格式（除非明确要求）
- 不删除别人写的死代码，只删除本次改动产生的无效代码
- 匹配项目现有代码风格：函数名用 snake_case、类名用 PascalCase

**改动追溯原则：** 每一行改动都应该能回答"这个改动的目的是什么"

**清理规则（仅限本次改动的附带产物）：**
- 因本次改动而变成 None 的 import → 删除
- 因本次改动而失去调用的函数 → 删除
- 因本次改动而永远不可能为 True 的 if 条件 → 简化或删除

---

### 4. 目标驱动执行（Goal-Driven Execution）

**行动准则：**
- 将"修复某个问题"转化为"先写一个能复现问题的测试，让它失败，再让测试通过"
- 多步骤任务先陈述计划，再执行，最后验证

**标准工作流：**
```
1. [收集数据] → 验证：输出目录有 .png 文件
2. [训练模型] → 验证：output/ 目录有 .pt 模型文件
3. [运行测试] → 验证：pytest 无 FAIL
```

**无测试场景：** 对于浏览器自动化类任务，用截图验证替代单元测试：
```
[修改 AFK 保护] → 验证：手动运行脚本，截图确认验证码被正确检测
```

---

## 项目特定规则

### 技术栈约束

| 组件 | 技术选择 | 原因 |
|------|---------|------|
| 训练框架 | PyTorch | 主流，Kaggle Notebook 原生支持 |
| 目标检测 | YOLO（ultralytics） | 成熟，mobs_images 数据集验证过 |
| 浏览器自动化 | Playwright | 跨平台，异步性能好 |
| 模型格式 | .pt（Pytorch） | 直接 torch.load()，无转换步骤 |
| 标注格式 | YOLO TXT | 工具链最简，Roboflow 直接支持 |

**禁止：**
- ❌ 引入 TensorFlow/Keras（与 PyTorch 重复）
- ❌ 引入 Detectron2/MMDetection（过度复杂）
- ❌ 引入 Selenium（同步，性能差）
- ❌ 使用 .h5 / .ckpt 格式（增加转换步骤）

### 文件组织

```
florr_powerful_tools/
├── florr-auto-*-pytorch/    # 主要自动化工具（各平台）
├── mob_wiki_monitor/         # Wiki 监控工具
├── mob_wiki/
├── mobs_images/             # 标注数据（.png + .txt）
├── config/                  # 配置文件（被代码读取）
├── scripts/                 # 工具脚本
└── tests/                   # 单元测试
```

- 资源类文件（.pt、数据集）放对应子目录，不放根目录
- 各平台版本（*-macos、*-windows）独立目录，共享代码优先提取到 scripts/

### 配置管理

- 所有敏感配置（API keys、Kaggle token）通过环境变量或 config/ 读取
- 不硬编码任何凭证
- config/ 目录下的 .example 文件记录必需的环境变量名

### 测试规范

```bash
# 运行所有测试
bash run_tests.sh

# 收集测试覆盖率
pytest --cov=. --cov-report=term-missing
```

- 每个独立模块（data_collector、mob_detector、path_finding）至少有一个测试文件
- 测试文件命名：`test_模块名.py`

### Git 提交规范

```
<类型>(<模块>): <简短描述>

类型：feat | fix | refactor | docs | test | chore
```

示例：
```
feat(afk): 添加花瓣识别阈值自动调整
fix(pathfinding): 修复边界处路径计算死循环
docs: 更新 README 安装步骤
```

---

## 项目上下文（AI 需要知道的事）

### 核心用户场景
- **AFK 玩家**：挂机时被验证码踢出，需要自动识别并解决验证码
- **竞速玩家**：需要自动寻路通过复杂地图
- **数据收集者**：需要批量采集花瓣/怪物图片用于训练
- **AI 训练者**：需要用自己采集的数据训练自定义检测模型

### 已知限制
- **浏览器版本敏感**：Playwright 版本需与 Chromium 版本匹配
- **Kaggle API 限速**：token 有速率限制，大批量下载需加 delay
- **Roboflow 配额**：免费账号有图片数量上限
- **游戏更新风险**：游戏 UI 变化会破坏计算机视觉检测（花瓣颜色、形状）

### 参考资料
- 项目架构文档：`PROJECT_ARCHITECTURE.md`
- 快速开始：`QUICK_SETUP.md`
- Kaggle API 配置：`SETUP_KAGGLE_API.md`
- 已有研究：`PROJECT_RESEARCH_REPORT.md`
- Kaggle 训练指南：`KAGGLE_TRAINING_QUICKSTART.md`

---

## 错误处理

### 当遇到报错时

1. **先读报错信息**——不要猜测原因
2. **搜索项目内已有解决方案**——`docs/`、`*.md` 中可能有记录
3. **如果是依赖问题**——先检查 `requirements.txt` / `pyproject.toml` 中版本
4. **如果是浏览器问题**——检查 `playwright install --check` 输出
5. **如果是 Kaggle 问题**——检查 `~/.kaggle/kaggle.json` 凭证格式

### 报告新问题

发现新的错误模式时，更新 `docs/` 中的 troubleshooting 章节，不要只在聊天中提及。

---

*本文件由 AI 协作规范生成，基于 Karpathy AI 编程原则。更新日期：2026-04-22*
