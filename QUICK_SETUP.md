# Kaggle API 配置 - 快速指南

## ✅ kaggle.json 已找到

文件位置: `/Users/panjiyang/trae_projects/florr_powerful_tools/kaggle.json`

用户名: `panp2010`

---

## 🔧 配置步骤

请在终端中运行以下命令：

```bash
# 1. 创建目录
mkdir -p ~/.kaggle

# 2. 复制文件
cp /Users/panjiyang/trae_projects/florr_powerful_tools/kaggle.json ~/.kaggle/

# 3. 设置权限（重要！）
chmod 600 ~/.kaggle/kaggle.json

# 4. 验证配置
ls -la ~/.kaggle/kaggle.json
```

---

## ✅ 验证配置

```bash
# 测试连接
kaggle competitions list

# 查看配置
kaggle config view
```

---

## 🚀 配置完成后

运行上传脚本：

```bash
./upload_to_kaggle.sh
```

---

## 📝 一键配置命令

复制并运行这一行命令：

```bash
mkdir -p ~/.kaggle && cp /Users/panjiyang/trae_projects/florr_powerful_tools/kaggle.json ~/.kaggle/ && chmod 600 ~/.kaggle/kaggle.json && echo "✓ 配置完成" && kaggle config view
```

---

## ❓ 常见问题

**Q: 为什么需要设置权限？**
A: 保护 API Token 安全，防止其他用户访问。

**Q: 配置后可以删除原文件吗？**
A: 可以，但建议保留备份。

**Q: 如何验证配置成功？**
A: 运行 `kaggle competitions list`，如果显示比赛列表则成功。

---

**下一步**: 运行上面的配置命令，然后执行 `./upload_to_kaggle.sh` 上传数据集！
