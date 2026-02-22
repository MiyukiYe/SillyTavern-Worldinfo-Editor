import json
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import shutil
from datetime import datetime
import ctypes

# 尝试唤醒 Windows 高 DPI 模式，解决模糊像素感问题！
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

import customtkinter as ctk

# 尝试导入简繁转换库
try:
    import zhconv
    HAS_ZHCONV = True
except ImportError:
    HAS_ZHCONV = False

# 设置全局主题和外观
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class WorldbookEditor:
    def __init__(self, root):
        self.root = root
        self.app_title = "SillyTavern 世界书编辑器"
        self.root.title(f"{self.app_title} - [未打开文件]")
        self.root.geometry("1150x750")
        
        # 现代 UI 窗口圆角等优化(根据系统支持)
        self.data = None
        self.filepath = None
        
        self.entries = [] 
        self.filtered_mapping = []
        self.current_real_index = None
        self.drag_start_index = None
        self.is_modified = False

        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        # 基础网格布局
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)

        # ================= 顶部现代导航栏 =================
        top_bar = ctk.CTkFrame(self.root, height=45, corner_radius=0, fg_color="#1a1a1a")
        top_bar.grid(row=0, column=0, sticky="ew")
        top_bar.pack_propagate(False)

        btn_style = {"fg_color": "transparent", "text_color": "#cce4ff", "hover_color": "#1f538d", "width": 80}
        
        ctk.CTkButton(top_bar, text="📄 新建", command=self.new_file, **btn_style).pack(side="left", padx=5, pady=8)
        ctk.CTkButton(top_bar, text="📂 打开", command=self.load_file, **btn_style).pack(side="left", padx=5)
        ctk.CTkButton(top_bar, text="💾 保存", command=self.save_file, **btn_style).pack(side="left", padx=5)
        ctk.CTkButton(top_bar, text="💾 另存为...", command=self.save_as_file, **btn_style).pack(side="left", padx=5)
        
        ctk.CTkButton(top_bar, text="❌ 退出", command=self.on_closing, fg_color="transparent", text_color="#ff6b6b", hover_color="#8b0000", width=80).pack(side="right", padx=10)

        # ================= 主体分栏 (保留可拖动特性，但样式暗黑化) =================
        self.paned_window = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg="#111111", bd=0, sashwidth=6, sashrelief="flat")
        self.paned_window.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # ================= 左侧：列表与搜索区 =================
        left_frame = ctk.CTkFrame(self.paned_window, fg_color="#212121", corner_radius=8)
        self.paned_window.add(left_frame, minsize=250)

        # 搜索框
        search_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=10, pady=(10, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var, placeholder_text="🔍 全局搜索...", border_width=1, corner_radius=6)
        self.search_entry.pack(fill="x", expand=True)
        self.search_entry.bind('<KeyRelease>', self.refresh_listbox)

        # 列表框 (包裹在容器中以配合现代滚动条)
        list_container = ctk.CTkFrame(left_frame, fg_color="#1e1e1e", corner_radius=6)
        list_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.listbox = tk.Listbox(list_container, exportselection=False, font=("Microsoft YaHei UI", 10),
                                  bg="#1e1e1e", fg="#e0e0e0", selectbackground="#1f538d", selectforeground="white",
                                  bd=0, highlightthickness=0, activestyle="none")
        self.listbox.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)
        self.listbox.bind('<Button-1>', self.on_drag_start)
        self.listbox.bind('<ButtonRelease-1>', self.on_drag_release)

        list_scroll = ctk.CTkScrollbar(list_container, command=self.listbox.yview)
        list_scroll.pack(side="right", fill="y", padx=2, pady=2)
        self.listbox.config(yscrollcommand=list_scroll.set)

        # 增删调序栏
        manage_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        manage_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        s_btn = {"width": 35, "height": 28, "corner_radius": 4}
        ctk.CTkButton(manage_frame, text="➕", command=self.add_entry, **s_btn, fg_color="#2b7a0b", hover_color="#1e5408").pack(side="left", padx=2)
        ctk.CTkButton(manage_frame, text="➖", command=self.delete_entry, **s_btn, fg_color="#b22222", hover_color="#7b1111").pack(side="left", padx=2)
        
        ctk.CTkLabel(manage_frame, text=" ").pack(side="left", padx=2) # 占位
        
        self.btn_up = ctk.CTkButton(manage_frame, text="▲", command=lambda: self.move_entry(-1), **s_btn)
        self.btn_up.pack(side="left", padx=2)
        self.btn_down = ctk.CTkButton(manage_frame, text="▼", command=lambda: self.move_entry(1), **s_btn)
        self.btn_down.pack(side="left", padx=2)
        self.btn_jump = ctk.CTkButton(manage_frame, text="📌 移至", command=self.jump_to_index, width=50, height=28, corner_radius=4)
        self.btn_jump.pack(side="right", padx=2)

        ctk.CTkLabel(left_frame, text="💡 提示: 支持直接鼠标拖拽排序", text_color="#666666", font=("Microsoft YaHei UI", 11)).pack(anchor="w", padx=10, pady=(0, 10))

        # ================= 右侧：编辑与转换区 =================
        right_frame = ctk.CTkFrame(self.paned_window, fg_color="#212121", corner_radius=8)
        self.paned_window.add(right_frame, minsize=600)

        content_inner = ctk.CTkFrame(right_frame, fg_color="transparent")
        content_inner.pack(fill="both", expand=True, padx=20, pady=20)

        # 备注与触发词
        ctk.CTkLabel(content_inner, text="备注/标题 (Comment):", font=("Microsoft YaHei UI", 12, "bold")).pack(anchor="w", pady=(0, 2))
        self.comment_var = tk.StringVar()
        self.comment_entry = ctk.CTkEntry(content_inner, textvariable=self.comment_var, font=("Microsoft YaHei UI", 12), border_width=1)
        self.comment_entry.pack(fill="x", pady=(0, 10))
        self.comment_entry.bind('<KeyRelease>', self.auto_save_current)

        ctk.CTkLabel(content_inner, text="触发词 (Keys - 英文逗号分隔):", font=("Microsoft YaHei UI", 12, "bold")).pack(anchor="w", pady=(0, 2))
        self.keys_var = tk.StringVar()
        self.keys_entry = ctk.CTkEntry(content_inner, textvariable=self.keys_var, font=("Microsoft YaHei UI", 12), border_width=1)
        self.keys_entry.pack(fill="x", pady=(0, 10))
        self.keys_entry.bind('<KeyRelease>', self.auto_save_current)

        # 选项行
        options_frame = ctk.CTkFrame(content_inner, fg_color="transparent")
        options_frame.pack(fill="x", pady=(0, 10))
        self.constant_var = ctk.BooleanVar()
        self.constant_check = ctk.CTkCheckBox(options_frame, text="始终激活 (Constant)", variable=self.constant_var, command=self.auto_save_current, checkbox_height=20, checkbox_width=20)
        self.constant_check.pack(side="left", padx=(0, 20))
        
        ctk.CTkLabel(options_frame, text="插入顺序/权重 (Order):").pack(side="left")
        self.order_var = tk.StringVar(value="100")
        self.order_entry = ctk.CTkEntry(options_frame, textvariable=self.order_var, width=80, height=24)
        self.order_entry.pack(side="left", padx=(10, 0))
        self.order_entry.bind('<KeyRelease>', self.auto_save_current)

        # 查找替换 & 简繁转换
        fr_frame = ctk.CTkFrame(content_inner, fg_color="#2a2a2a", corner_radius=6)
        fr_frame.pack(fill="x", pady=(5, 15), ipadx=10, ipady=5)
        
        ctk.CTkLabel(fr_frame, text="查找:").pack(side="left", padx=(10, 5))
        self.find_var = tk.StringVar()
        ctk.CTkEntry(fr_frame, textvariable=self.find_var, width=120, height=24).pack(side="left", padx=5)
        ctk.CTkButton(fr_frame, text="下一个", command=self.find_text, width=60, height=24).pack(side="left", padx=5)
        
        ctk.CTkLabel(fr_frame, text="替换为:").pack(side="left", padx=(15, 5))
        self.replace_var = tk.StringVar()
        ctk.CTkEntry(fr_frame, textvariable=self.replace_var, width=120, height=24).pack(side="left", padx=5)
        ctk.CTkButton(fr_frame, text="替换", command=self.replace_text, width=50, height=24).pack(side="left", padx=5)
        ctk.CTkButton(fr_frame, text="全部替换", command=self.replace_all_text, width=70, height=24).pack(side="left", padx=5)

        if HAS_ZHCONV:
            ctk.CTkLabel(fr_frame, text=" | ", text_color="#555555").pack(side="left", padx=5)
            ctk.CTkButton(fr_frame, text="转简体", command=lambda: self.convert_text('zh-hans'), width=60, height=24, fg_color="#8e44ad", hover_color="#732d91").pack(side="left", padx=5)
            ctk.CTkButton(fr_frame, text="转繁体", command=lambda: self.convert_text('zh-hant'), width=60, height=24, fg_color="#8e44ad", hover_color="#732d91").pack(side="left", padx=5)

        # 正文内容
        ctk.CTkLabel(content_inner, text="世界书正文 (Content):", font=("Microsoft YaHei UI", 12, "bold")).pack(anchor="w", pady=(0, 2))
        
        text_container = ctk.CTkFrame(content_inner, fg_color="#181818", corner_radius=6)
        text_container.pack(fill="both", expand=True)
        
        # 保持原生 Text 控件以完美支持颜色 Tag，但大幅美化样式
        self.content_text = tk.Text(text_container, wrap="word", undo=True, font=("Consolas", 12),
                                    bg="#181818", fg="#dcdcdc", insertbackground="white",
                                    bd=0, highlightthickness=0, selectbackground="#1f538d")
        self.content_text.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        text_scroll = ctk.CTkScrollbar(text_container, command=self.content_text.yview)
        text_scroll.pack(side="right", fill="y", padx=2, pady=2)
        self.content_text.config(yscrollcommand=text_scroll.set)
        
        # 【美化的高亮标签】红底白字(查找)、蓝底白字(替换)
        self.content_text.tag_config('found', background='#E74C3C', foreground='white', font=("Consolas", 12, "bold"))
        self.content_text.tag_config('replaced', background='#2980B9', foreground='white', font=("Consolas", 12, "bold"))
        
        self.content_text.bind('<KeyRelease>', self.auto_save_current)

    def mark_modified(self):
        if not self.is_modified:
            self.is_modified = True
            self.update_title()

    def update_title(self):
        prefix = "🔴 *" if self.is_modified else "🟢 "
        filename = os.path.basename(self.filepath) if self.filepath else "未命名新文件"
        self.root.title(f"{self.app_title} - {prefix}[{filename}]")

    def on_closing(self):
        if not self.is_modified:
            self.root.destroy()
            return
            
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("未保存的更改")
        dialog.geometry("450x150")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - 450) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 150) // 2
        dialog.geometry(f"+{x}+{y}")
        
        ctk.CTkLabel(dialog, text="⚠️ 灵感尚未落笔，您有未保存的修改！\n直接退出将丢失这些进度，请选择您的操作：", font=("Microsoft YaHei UI", 13)).pack(pady=20)
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10)
        
        ctk.CTkButton(btn_frame, text="💾 保存并退出", command=lambda: (self.save_file() and dialog.destroy() or self.root.destroy()), width=100).pack(side="left", padx=4, expand=True)
        ctk.CTkButton(btn_frame, text="📁 另存为退出", command=lambda: (self.save_as_file() and dialog.destroy() or self.root.destroy()), width=100).pack(side="left", padx=4, expand=True)
        ctk.CTkButton(btn_frame, text="🗑️ 直接退出", command=lambda: (dialog.destroy(), self.root.destroy()), fg_color="#b22222", hover_color="#7b1111", width=100).pack(side="left", padx=4, expand=True)
        ctk.CTkButton(btn_frame, text="取消", command=dialog.destroy, fg_color="transparent", border_width=1, width=70).pack(side="left", padx=4, expand=True)

    # ================= 核心读写 =================

    def new_file(self):
        if self.is_modified:
            if not messagebox.askyesno("确认新建", "当前修改未保存，是否强制丢弃并新建？"): return
        self.data = {"entries": {}}
        self.entries = []
        self.filepath = None
        self.is_modified = False
        self.search_var.set("")
        self.current_real_index = None
        self.clear_editor()
        self.refresh_listbox()
        self.update_title()

    def load_file(self):
        if self.is_modified:
            if not messagebox.askyesno("确认加载", "当前修改未保存，是否强制丢弃并打开新文件？"): return
            
        filepath = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if not filepath: return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name, ext = os.path.splitext(filepath)
            shutil.copy2(filepath, f"{base_name}_backup_{timestamp}{ext}")
        except Exception: pass

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            self.filepath = filepath
            self.entries = [self.data['entries'][k] for k in sorted(self.data['entries'].keys(), key=lambda x: int(x))] if 'entries' in self.data else []
            self.is_modified = False
            self.search_var.set("")
            self.current_real_index = None
            self.clear_editor()
            self.refresh_listbox()
            self.update_title()
        except Exception as e:
            messagebox.showerror("错误", f"无法加载文件: {e}")

    def save_file(self):
        if not self.data: 
            messagebox.showwarning("警告", "没有可保存的内容！")
            return False
        if not self.filepath: 
            return self.save_as_file()
            
        self.data['entries'] = {str(i): entry for i, entry in enumerate(self.entries)}
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            self.is_modified = False
            self.update_title()
            messagebox.showinfo("成功", "世界书修改已保存！")
            return True
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")
            return False

    def save_as_file(self):
        if not self.data: 
            messagebox.showwarning("警告", "没有可保存的内容！")
            return False
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")], title="另存为 世界书")
        if filepath:
            self.filepath = filepath
            return self.save_file()
        return False

    # ================= 列表管理与增删调序 =================

    def refresh_listbox(self, event=None):
        search_term = self.search_var.get().lower()
        self.listbox.delete(0, tk.END)
        self.filtered_mapping = []
        
        # 搜索状态下禁用调序按钮
        state = "disabled" if search_term else "normal"
        self.btn_up.configure(state=state)
        self.btn_down.configure(state=state)
        self.btn_jump.configure(state=state)

        for i, entry in enumerate(self.entries):
            display_name = entry.get('comment', f"条目 {i}") or "未命名条目"
            if search_term in display_name.lower() or search_term in ",".join(entry.get('key', [])).lower() or search_term in entry.get('content', '').lower():
                self.filtered_mapping.append(i)
                self.listbox.insert(tk.END, f"  [{i}] {display_name}")

    def on_select(self, event):
        selection = self.listbox.curselection()
        if not selection: return
        self.current_real_index = self.filtered_mapping[selection[0]]
        entry = self.entries[self.current_real_index]

        self.comment_var.set(entry.get('comment', ''))
        self.keys_var.set(",".join(entry.get('key', [])))
        self.constant_var.set(entry.get('constant', False))
        self.order_var.set(str(entry.get('order', 100)))
        
        self.content_text.tag_remove('found', '1.0', tk.END)
        self.content_text.tag_remove('replaced', '1.0', tk.END)
        self.content_text.delete('1.0', tk.END)
        self.content_text.insert('1.0', entry.get('content', ''))

    def auto_save_current(self, event=None):
        if self.current_real_index is None: return
        entry = self.entries[self.current_real_index]
        
        new_content = self.content_text.get('1.0', tk.END)
        if new_content.endswith('\n'): new_content = new_content[:-1]
        
        entry['comment'] = self.comment_var.get()
        entry['key'] = [k.strip() for k in self.keys_var.get().split(',') if k.strip()]
        entry['constant'] = self.constant_var.get()
        try: entry['order'] = int(self.order_var.get())
        except ValueError: pass 
        entry['content'] = new_content
        
        self.mark_modified()
        
        selection = self.listbox.curselection()
        if selection:
            idx = selection[0]
            new_list_text = f"  [{self.current_real_index}] {entry['comment'] or '未命名条目'}"
            if new_list_text != self.listbox.get(idx):
                self.listbox.delete(idx)
                self.listbox.insert(idx, new_list_text)
                self.listbox.selection_set(idx)

    def clear_editor(self):
        self.comment_var.set("")
        self.keys_var.set("")
        self.content_text.tag_remove('found', '1.0', tk.END)
        self.content_text.tag_remove('replaced', '1.0', tk.END)
        self.content_text.delete('1.0', tk.END)
        self.current_real_index = None

    def add_entry(self):
        if not self.data: return messagebox.showwarning("警告", "请先新建或打开一个世界书！")
        self.entries.append({
            "key": [], "keysecondary": [], "comment": "新建条目", "content": "",
            "constant": False, "vectorized": False, "selective": True,
            "selectiveLogic": 0, "addMemo": True, "order": 100,
            "position": 0, "disable": False, "excludeRecursion": True,
            "preventRecursion": True, "probability": 100, "useProbability": True,
            "depth": 4, "group": "", "groupWeight": 100
        })
        self.mark_modified()
        self.search_var.set("") 
        self.refresh_listbox()
        self.listbox.selection_set(self.listbox.size() - 1)
        self.listbox.see(self.listbox.size() - 1)
        self.on_select(None)

    def delete_entry(self):
        if self.current_real_index is None: return
        if messagebox.askyesno("确认删除", f"确定要删除条目 [{self.current_real_index}] 吗？"):
            del self.entries[self.current_real_index]
            self.mark_modified()
            self.clear_editor()
            self.refresh_listbox()

    def move_entry(self, direction):
        if self.current_real_index is None or self.search_var.get(): return 
        idx = self.current_real_index
        new_idx = idx + direction
        if 0 <= new_idx < len(self.entries):
            self.entries[idx], self.entries[new_idx] = self.entries[new_idx], self.entries[idx]
            self.mark_modified()
            self.refresh_listbox()
            self.listbox.selection_set(new_idx)
            self.listbox.see(new_idx)
            self.on_select(None)

    def jump_to_index(self):
        if self.current_real_index is None or self.search_var.get(): return
        max_idx = len(self.entries) - 1
        # 使用现代弹窗
        dialog = ctk.CTkInputDialog(text=f"当前操作条目: [{self.current_real_index}]\n\n请输入目标序号 (0 - {max_idx}):", title="移动到指定位置")
        try:
            target = int(dialog.get_input())
            if 0 <= target <= max_idx and target != self.current_real_index:
                item = self.entries.pop(self.current_real_index)
                self.entries.insert(target, item)
                self.mark_modified()
                self.refresh_listbox()
                self.listbox.selection_set(target)
                self.listbox.see(target)
                self.on_select(None)
        except (ValueError, TypeError):
            pass

    def on_drag_start(self, event):
        if self.search_var.get(): return 
        self.drag_start_index = self.listbox.nearest(event.y)

    def on_drag_release(self, event):
        if self.search_var.get() or self.drag_start_index is None: return
        drag_end_index = self.listbox.nearest(event.y)
        if self.drag_start_index != drag_end_index and 0 <= drag_end_index < len(self.entries):
            item = self.entries.pop(self.drag_start_index)
            self.entries.insert(drag_end_index, item)
            self.mark_modified()
            self.refresh_listbox()
            self.listbox.selection_set(drag_end_index)
            self.listbox.see(drag_end_index)
            self.on_select(None)
        self.drag_start_index = None

    # ================= 查找替换与转换 =================
    
    def find_text(self):
        self.content_text.tag_remove('found', '1.0', tk.END)
        self.content_text.tag_remove('sel', '1.0', tk.END)
        target = self.find_var.get()
        if target:
            start_pos = self.content_text.index(tk.INSERT)
            pos = self.content_text.search(target, start_pos, stopindex=tk.END)
            if not pos: pos = self.content_text.search(target, '1.0', stopindex=start_pos)
            if pos:
                end_pos = f"{pos}+{len(target)}c"
                self.content_text.tag_add('sel', pos, end_pos)
                self.content_text.tag_add('found', pos, end_pos)
                self.content_text.mark_set(tk.INSERT, end_pos)
                self.content_text.see(pos)
            else:
                messagebox.showinfo("提示", "未找到指定内容。")

    def replace_text(self):
        self.content_text.tag_remove('replaced', '1.0', tk.END)
        if self.content_text.tag_ranges('sel'):
            pos = self.content_text.index('sel.first')
            self.content_text.delete('sel.first', 'sel.last')
            replacement = self.replace_var.get()
            self.content_text.insert(pos, replacement)
            end_pos = f"{pos}+{len(replacement)}c"
            self.content_text.tag_add('replaced', pos, end_pos)
            self.content_text.mark_set(tk.INSERT, end_pos)
            self.auto_save_current()
            self.find_text() 
        else:
            self.find_text() 

    def replace_all_text(self):
        target = self.find_var.get()
        replacement = self.replace_var.get()
        if not target: return
        self.content_text.tag_remove('found', '1.0', tk.END)
        self.content_text.tag_remove('replaced', '1.0', tk.END)
        count, idx = 0, '1.0'
        while True:
            idx = self.content_text.search(target, idx, stopindex=tk.END)
            if not idx: break
            end_pos = f"{idx}+{len(target)}c"
            self.content_text.delete(idx, end_pos)
            self.content_text.insert(idx, replacement)
            new_end_pos = f"{idx}+{len(replacement)}c"
            self.content_text.tag_add('replaced', idx, new_end_pos)
            idx = new_end_pos
            count += 1
        if count > 0:
            self.auto_save_current()
            messagebox.showinfo("替换完成", f"已成功替换 {count} 处内容。")
        else:
            messagebox.showinfo("提示", "未找到可替换的内容。")

    def convert_text(self, mode):
        if self.current_real_index is None: return
        content = self.content_text.get('1.0', tk.END)
        if content.endswith('\n'): content = content[:-1]
        converted = zhconv.convert(content, mode)
        self.content_text.delete('1.0', tk.END)
        self.content_text.insert('1.0', converted)
        self.auto_save_current()
        messagebox.showinfo("转换成功", f"当前条目正文已转换为{'简体' if mode == 'zh-hans' else '繁体'}。")

if __name__ == "__main__":
    app = ctk.CTk()
    editor = WorldbookEditor(app)
    app.mainloop()