# 📖 SillyTavern World Info Editor (ST世界书本地编辑器)

一个专为 **SillyTavern (酒馆)** 用户打造的现代化、纯本地的“世界书 (World Info / Lorebooks)”独立编辑器。

## 💡 为什么需要这个工具？

当 SillyTavern 的世界书条目积累到几百甚至上千条时，基于浏览器前端 DOM 的渲染会遭遇严重的性能瓶颈，导致网页端在打字、滚动和保存时出现令人抓狂的卡顿。
本项目旨在提供一个**脱离网页端**的轻量级原生桌面化解决方案，用极其丝滑的响应速度和现代化的 UI，彻底解放你的创作生产力！

<img width="2560" height="1518" alt="image" src="https://github.com/user-attachments/assets/fa61945b-07c8-406a-a3a2-9b1c4587c327" />


## ✨ 核心特性

本项目完美对齐了 [SillyTavern 官方世界书文档](https://docs.sillytavern.app/usage/worldinfo/) 中的所有设定，不仅没有功能妥协，还加入了大量专为“世界书长篇创作者”设计的效率工具。

### 🌍 1. 100% 满血功能支持
完美映射并解析 ST 世界书底层的各项复杂逻辑（包括最新的特性），并严谨处理了继承全局设置的 `null` 空值状态：
- **高级策略**：支持常规触发、常驻 (Constant) 以及向量化匹配 (Vectorized)。
- **插入与过滤**：支持 8 种精确插入位置（含 @ 特定深度与 Outlet 出口）、4 种多级逻辑过滤器、全字匹配/区分大小写。
- **递归与时效**：完整支持递归扫描阻止、延迟递归、递归层级分组，以及冷却 (Cooldown)、粘性 (Sticky) 和延迟 (Delay) 等时效性规则。
- **高级群组**：支持互斥组 (Group)、组权重以及组评分 (Group Scoring) 判定。
- **拓展扫描**：涵盖角色备注 (Depth Prompt)、场景预设、创作者笔记等多维度附加匹配源。

### 🚀 2. 极致的性能与交互体验
- **现代蓝白主题 UI**：告别 Windows 原生生硬控件，采用全局自定义 QSS，提供充满呼吸感的排版与微动效。
- **全局极速检索**：支持同时针对标题、触发词、过滤器和具体**内容**进行毫秒级全局过滤。
- **丝滑排序**：支持列表条目**鼠标直接拖拽排序**，或输入数字精准“空降”移动。

### 🛠️ 3. 专为创作者打造的效率工具
- **高级查找与替换**：内置专属文本编辑器，支持查找词“黄字红底”全局高亮，替换词“白字蓝底”精准标识。
- **防丢/容灾机制**：每次打开文件时，自动在同目录下生成 `.backup` 备份文件；拥有完善的未保存退出拦截提示。
- **无损简繁转换**：内置自动化一键简繁转换功能（支持标题/触发词/内容自由勾选），转换后不覆盖原文件，而是自动生成带有后缀的新条目供对比。

---

## 📦 安装与使用

### 选项 A：直接运行 (推荐普通用户)
1. 前往仓库的 [Releases](https://github.com/MiyukiYe/SillyTavern-Worldinfo-Editor/releases) 页面下载最新打包好的 `.exe` 或 `.html` 文件。
2. 无需安装任何环境，双击即可运行！
3. 点击左上角 `文件 -> 打开`，选择你从 SillyTavern 导出的 `.json` 世界书文件即可开始流畅编辑。

### 选项 B：从源码运行 (推荐开发者)
确保你已安装 Python 3.10 或更高版本。
1. 克隆本仓库到本地：
   ```bash
   git clone [https://github.com/你的用户名/ST_WorldInfo_Editor.git](https://github.com/你的用户名/ST_WorldInfo_Editor.git)
   cd ST_WorldInfo_Editor
   ```

2. 安装必要的依赖库：
   ```bash
   pip install PySide6 zhconv
   ```

3. 运行主程序：
   ```bash
   python main.py
   ```

---

## 🛠️ 构建可执行文件

如果你想自己将源码打包为 `.exe` 文件：

```bash
pip install pyinstaller
pyinstaller -F -w -i icon.ico main.py
```

打包完成的文件将生成在 `dist` 目录下。

## 🤝 参与贡献

欢迎提交 Issue 和 Pull Request！如果你有关于界面布局、快捷键支持或是批量处理功能的绝妙想法，非常期待你的加入。

## 📄 开源协议

本项目基于 [MIT License](https://www.google.com/search?q=LICENSE) 开源，你可以自由地使用、修改和分发。

