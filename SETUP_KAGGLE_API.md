# Kaggle API 配置步骤

## 📋 当前状态

✅ Kaggle API 已安装（版本 2.0.0）
❌ API Token 未配置

---

## 🔑 获取 API Token

### 步骤 1: 登录 Kaggle

访问 https://www.kaggle.com/ 并登录您的账号

### 步骤 2: 进入设置页面

1. 点击右上角头像
2. 选择 "Settings"
3. 或直接访问: https://www.kaggle.com/settings

### 步骤 3: 创建 API Token

1. 滚动到页面底部的 "API" 部分
2. 点击 "Create New API Token" 按钮
3. 浏览器会自动下载 `kaggle.json` 文件

**文件内容示例：**
```json
{
  "username": "your-username",
  "key": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

---

## ⚙️ 配置 API Token

### 方法 1: 自动配置（推荐）

下载完成后，运行以下命令：

```bash
# 创建目录
mkdir -p ~/.kaggle

# 移动文件
mv ~/Downloads/kaggle.json ~/.kaggle/

# 设置权限（重要！）
chmod 600 ~/.kaggle/kaggle.json
```

### 方法 2: 手动配置

如果文件不在 Downloads 目录：

```bash
# 查找文件
find ~ -name "kaggle.json" 2>/dev/null

# 或指定路径
mv /path/to/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

---

## ✅ 验证配置

运行以下命令验证：

```bash
# 检查文件权限
ls -la ~/.kaggle/kaggle.json

# 应该显示: -rw------- (600)

# 测试连接
kaggle competitions list

# 查看用户信息
kaggle config view
```

---

## 🚀 快速配置脚本

创建 `setup_kaggle.sh` 并运行：

```bash
#!/bin/bash

echo "Kaggle API 配置工具"
echo "=================="

# 检查 kaggle.json 是否存在
if [ -f ~/.kaggle/kaggle.json ]; then
    echo "✓ kaggle.json 已配置"
    ls -la ~/.kaggle/kaggle.json
    exit 0
fi

# 查找下载的文件
KAGGLE_JSON=$(find ~/Downloads -name "kaggle.json" 2>/dev/null | head -1)

if [ -z "$KAGGLE_JSON" ]; then
    echo "❌ 未找到 kaggle.json"
    echo ""
    echo "请先下载 API Token:"
    echo "1. 访问 https://www.kaggle.com/settings"
    echo "2. 点击 'Create New API Token'"
    echo "3. 下载 kaggle.json"
    echo "4. 重新运行此脚本"
    exit 1
fi

# 配置
echo "找到文件: $KAGGLE_JSON"
echo "正在配置..."

mkdir -p ~/.kaggle
mv "$KAGGLE_JSON" ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json

echo "✓ 配置完成!"
echo ""
echo "验证配置:"
ls -la ~/.kaggle/kaggle.json
```

---

## 📝 配置完成后

运行上传脚本：

```bash
# 上传数据集
./upload_to_kaggle.sh

# 或手动上传
cd upload_package
kaggle datasets create -p .
```

---

## ❓ 常见问题

### Q: 为什么需要 API Token？

A: API Token 用于身份验证，允许您通过命令行访问 Kaggle 资源。

### Q: Token 安全吗？

A: Token 包含敏感信息，请勿分享。设置 600 权限确保只有您能访问。

### Q: 如何重新生成 Token？

A: 访问 https://www.kaggle.com/settings，点击 "Expire API Token"，然后重新创建。

### Q: 忘记 Token 怎么办？

A: 重新下载即可，旧的 Token 会自动失效。

---

## 🔗 有用链接

- Kaggle 设置: https://www.kaggle.com/settings
- API 文档: https://github.com/Kaggle/kaggle-api
- 帮助中心: https://www.kaggle.com/docs/api

---

**下一步**: 下载 kaggle.json 后运行配置命令！
