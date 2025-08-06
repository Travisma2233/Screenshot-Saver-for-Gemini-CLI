#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
无控制台窗口的截图保存器启动脚本
此脚本将隐藏控制台窗口，仅显示GUI界面，并提供系统托盘功能
"""
import sys
import os
import threading
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import time

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入主程序
from clipboard_screenshot_saver import ClipboardScreenshotSaver

class ScreenshotSaverGUI:
    def __init__(self):
        self.saver = None
        self.monitor_thread = None
        self.running = False
        
    def show_error(self, message):
        """显示错误消息"""
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        messagebox.showerror("错误", message)
        root.destroy()
    
    def show_exit_confirmation(self):
        """显示退出确认"""
        try:
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            
            result = messagebox.askyesno(
                "退出确认", 
                "截图保存器正在后台运行。\n\n确定要退出程序吗？",
                icon='question'
            )
            root.destroy()
            return result
        except:
            return True
    
    def monitor_wrapper(self):
        """监控包装器，用于在单独线程中运行"""
        try:
            self.saver.monitor_clipboard()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            self.show_error(f"监控过程出错:\n{str(e)}")
        finally:
            self.running = False
    
    def start(self):
        """启动程序"""
        try:
            # 创建截图保存器（会自动弹出文件夹选择对话框）
            self.saver = ClipboardScreenshotSaver()
            
            if self.saver.save_path:
                self.running = True
                # 在单独线程中启动监控
                self.monitor_thread = threading.Thread(target=self.monitor_wrapper, daemon=True)
                self.monitor_thread.start()
                
                # 主线程保持运行，等待退出信号
                try:
                    while self.running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    self.running = False
                    
        except Exception as e:
            self.show_error(f"程序启动失败:\n{str(e)}")

def main():
    """主函数 - 无控制台模式"""
    try:
        gui = ScreenshotSaverGUI()
        gui.start()
        
    except KeyboardInterrupt:
        print("\n程序已退出")
    except Exception as e:
        # 创建简单的错误显示
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        messagebox.showerror("错误", f"程序运行出错:\n{str(e)}")
        root.destroy()

if __name__ == "__main__":
    main()