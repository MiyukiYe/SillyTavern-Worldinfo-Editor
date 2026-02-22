# 📖 SillyTavern Worldinfo Editor (酒馆世界书本地编辑器)

一款专为 SillyTavern（酒馆）跑团/聊天玩家打造的**轻量级、现代化、防丢护航**的本地世界书编辑器。

当你编写了数十上百条、动辄几万字的庞大世界设定（如大型剧本杀、长篇企划）时，SillyTavern 网页端自带的编辑器往往会出现严重的输入卡顿和内存溢出。本项目正是为了彻底解决这一痛点而生——**告别浏览器卡顿，丝滑管理你的大部头设定集！**

## ✨ 核心特性 (Key Features)

* 🚀 **极致流畅的本地编辑**：纯本地原生 GUI 程序，彻底摆脱网页端渲染长文本时的卡顿噩梦。
* 🎨 **现代高颜值 UI**：采用 `customtkinter` 打造的纯正 Dark Mode（深色模式），自动唤醒 Windows 底层高 DPI 缩放，文字渲染如矢量般锐利，护眼且优雅。
<img width="863" height="584" alt="Snipaste_2026-02-22_20-59-28" src="https://github.com/user-attachments/assets/419774d1-9312-4c02-9ec1-cb185e1aa0fc" />

* 🔍 **全局搜索 & 高亮替换**：
* 左侧列表支持对**标题、触发词、正文**进行深层全局检索。
<img width="182" height="519" alt="Snipaste_2026-02-22_21-01-11" src="https://github.com/user-attachments/assets/f7822873-e2e5-466e-991a-60ac6aaadfb5" />

* 右侧编辑器自带“查找与替换”功能，目标内容**红底白字**醒目高亮，替换成功**蓝底白字**即时反馈。
<img width="668" height="519" alt="Snipaste_2026-02-22_21-01-55" src="https://github.com/user-attachments/assets/e678b773-0054-4de6-a0a8-b4fab1292165" />



* 🖱️ **丝滑的条目排序**：
* 支持**鼠标按住直接拖拽**左侧列表进行排序。
* 提供【📌 移至】功能，输入序号即可让条目一键跨越百行“瞬移”。（所有位置调整将完美同步至底层 JSON 键值）。
<img width="442" height="184" alt="Snipaste_2026-02-22_21-02-50" src="https://github.com/user-attachments/assets/59658a26-7a63-44da-83fa-af947c5afde5" />


* 🀄 **一键简繁转换**：内置 `zhconv` 引擎，一键将上万字的正文在“简体中文”和“繁体中文”间无缝切换，再也不用复制到外部网页处理了。
<img width="668" height="519" alt="Snipaste_2026-02-22_21-03-29" src="https://github.com/user-attachments/assets/02ceadd3-0a03-4d28-9184-3667f4ab765e" />

* 🛡️ **数据护航**：
* **自动备份**：每次打开世界书时，会在同目录下自动生成一份带有时间戳的 `_backup` 备份文件，误删也能随时回档。
* **防丢拦截**：实时追踪修改状态（标题栏 `🔴 *` 提示）。意外点击右上角“X”关闭时，会强制拦截并弹出“保存/另存为”确认框，保护你的灵感心血。
<img width="338" height="127" alt="Snipaste_2026-02-22_21-03-48" src="https://github.com/user-attachments/assets/43435169-49ca-43da-9018-aeffa646101b" />


* 📁 **全生命周期管理**：支持从零**新建**空白世界书结构，也支持将不同分支结局的设定**另存为**新文件。
<img width="1725" height="1159" alt="image" src="https://github.com/user-attachments/assets/041bce08-2d56-4a67-8c01-6bede8b8b955" />

## 📥 下载与使用 (How to Use)

**普通用户（推荐）：**

1. 前往本仓库的 [Releases 页面](https://github.com/MiyukiYe/SillyTavern-Worldbook-Editor/releases) 下载最新版本的 `.exe` 可执行文件。
2. 无需安装任何环境，双击直接运行。
3. 点击顶部导航栏的 `📂 打开`，选择你的 SillyTavern 世界书文件（`.json` 格式）即可开始丝滑编辑。
4. 编辑完成后点击 `💾 保存`，即可直接在酒馆中生效。

> **⚠️ 杀毒软件误报说明：**
> 本程序使用 PyInstaller 打包为单文件独立运行版。由于个人开发者没有购买昂贵的微软数字签名证书，Windows Defender 或其他杀毒软件可能会弹出“已保护你的电脑”的未知发布者拦截，或产生误报。
> **解决办法：** 点击弹窗上的 `更多信息` -> `仍要运行` 即可。本工具完全开源，所有代码均在 `st_worldinfo_editor.py` 中，绝无恶意行为，请放心使用。

## 🛠️ 开发者指南 (For Developers)

如果你熟悉 Python，并希望自己运行源码或进行二次开发，请按照以下步骤配置环境：

**1. 克隆仓库**

```bash
git clone https://github.com/你的用户名/你的仓库名.git
cd 你的仓库名

```

**2. 安装依赖库**
本工具依赖 `customtkinter` (用于现代 UI) 和 `zhconv` (用于简繁转换)：

```bash
pip install customtkinter zhconv

```

**3. 运行脚本**

```bash
python st_worldinfo_editor.py

```

**4. 自行打包为 .exe**

```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --hidden-import zhconv --collect-all customtkinter st_worldinfo_editor.py

```

编译成功后，可执行文件将生成在 `dist` 文件夹中。

## 📝 更新日志 (Changelog)

**v9.0 (当前版本)**

* 彻底重构 UI，引入 CustomTkinter 现代深色主题。
* 增加 Windows 高 DPI 适配，解决文本模糊问题。
* 完善了退出时的未保存拦截机制（防丢护航）。
* 增加了新建和另存为功能。

*(早期迭代版本更新略...)*

## 🤝 贡献与反馈

欢迎在 Issues 中提出你在编辑设定集时遇到的痛点，或者提交 Pull Request 共同完善这个小工具。如果你觉得这个工具拯救了你的酒馆体验，请点击右上角的 ⭐ **Star** 支持一下！

---

*Created with ❤️ for the SillyTavern community.*

---
