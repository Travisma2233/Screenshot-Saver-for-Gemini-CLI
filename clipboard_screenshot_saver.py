import os
import sys
import time
import json
import keyboard
import pyperclip
from datetime import datetime
from pathlib import Path
import threading
from PIL import Image
import io
import win32clipboard
import win32con
import hashlib
from pynput.keyboard import Key, Controller
import tkinter as tk
from tkinter import filedialog, messagebox

class ClipboardScreenshotSaver:
    def __init__(self, save_path=None):
        """
        初始化剪贴板截图保存器
        
        Args:
            save_path (str): 截图保存路径，如果为None则会提示用户选择
        """
        self.config_file = Path("screenshot_config.json")
        self.last_clipboard_content = None
        self.last_image_hash = None
        self.latest_saved_file = None  # 存储最新保存的文件路径
        self.hotkey = 'ctrl+alt+p'  # 默认快捷键
        self.keyboard_controller = Controller()  # 用于模拟键盘输入
        self.hotkey_check_counter = 0  # 用于定期检查快捷键状态
        self.is_monitoring = False  # 添加监控状态标志
        
        # 加载配置
        self.load_config()
        
        # 如果没有指定保存路径，则让用户选择
        if save_path is None:
            save_path = self.select_save_folder()
            if save_path is None:
                # 用户取消了选择，使用默认路径
                save_path = "screenshots"
        
        self.save_path = Path(save_path)
        self.save_path.mkdir(exist_ok=True)
        
        # 保存更新后的配置
        self.save_config()
    
    def hide_console_window(self):
        """隐藏控制台窗口"""
        try:
            import ctypes
            from ctypes import wintypes
            
            # 使用 ctypes 直接调用 Windows API
            kernel32 = ctypes.windll.kernel32
            user32 = ctypes.windll.user32
            
            # 获取当前控制台窗口句柄
            console_window = kernel32.GetConsoleWindow()
            if console_window != 0:
                # 隐藏控制台窗口 (SW_HIDE = 0)
                user32.ShowWindow(console_window, 0)
                print("✅ 控制台窗口已隐藏")
                return True
            else:
                print("ℹ️ 未找到控制台窗口")
                return False
        except Exception as e:
            print(f"⚠️ 隐藏控制台窗口失败: {e}")
            print("💡 提示: 您可以手动最小化控制台窗口")
        return False
    
    def show_console_window(self):
        """显示控制台窗口"""
        try:
            import ctypes
            
            # 使用 ctypes 直接调用 Windows API
            kernel32 = ctypes.windll.kernel32
            user32 = ctypes.windll.user32
            
            # 获取当前控制台窗口句柄
            console_window = kernel32.GetConsoleWindow()
            if console_window != 0:
                # 显示控制台窗口 (SW_SHOW = 5)
                user32.ShowWindow(console_window, 5)
                return True
        except Exception as e:
            print(f"显示控制台窗口失败: {e}")
        return False
    
    def select_save_folder(self):
        """弹出文件夹选择对话框"""
        try:
            # 创建一个隐藏的根窗口
            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口
            root.attributes("-topmost", True)  # 确保对话框在最前面
            
            # 尝试从配置文件中获取上次的保存路径作为初始目录
            initial_dir = None
            if self.config_file.exists():
                try:
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        last_path = config.get('save_path', None)
                        if last_path and Path(last_path).exists():
                            initial_dir = last_path
                except:
                    pass
            
            if initial_dir is None:
                initial_dir = str(Path.home() / "Pictures")  # 默认使用图片文件夹
            
            # 显示文件夹选择对话框
            selected_folder = filedialog.askdirectory(
                title="选择截图保存文件夹",
                initialdir=initial_dir
            )
            
            # 清理tkinter
            root.destroy()
            
            return selected_folder if selected_folder else None
            
        except Exception as e:
            print(f"文件夹选择对话框出错: {e}")
            return None
    
    def show_startup_notification(self):
        """显示启动通知"""
        try:
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            
            message = f"""截图保存器已启动！

保存路径: {self.save_path.resolve()}
快捷键: {self.hotkey.upper()} - 粘贴最新截图路径
备用键: Ctrl+Shift+C - 复制路径到剪贴板

程序将在后台运行，请使用您的截图软件截图并复制到剪贴板。
图片将自动保存到指定文件夹。

点击"确定"继续运行程序。"""
            
            messagebox.showinfo("截图保存器", message)
            root.destroy()
            
        except Exception as e:
            print(f"显示启动通知失败: {e}")
        
    def load_config(self):
        """加载配置文件"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.save_path = Path(config.get('save_path', 'screenshots'))
                    self.save_path.mkdir(exist_ok=True)
                    self.hotkey = config.get('hotkey', 'ctrl+alt+p')
            except Exception as e:
                print(f"加载配置文件失败: {e}")
                self.set_default_config()
        else:
            self.set_default_config()
    
    def set_default_config(self):
        """设置默认配置"""
        self.save_config()
    
    def save_config(self):
        """保存配置文件"""
        config = {
            'save_path': str(self.save_path),
            'hotkey': self.hotkey
        }
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置文件失败: {e}")

    def set_save_path(self, new_path):
        """设置新的保存路径"""
        try:
            old_path = self.save_path
            new_path = Path(new_path)
            new_path.mkdir(exist_ok=True)
            self.save_path = new_path
            self.save_config()
            
            print(f"📂 截图保存路径已更新:")
            print(f"   原路径: {old_path.resolve()}")
            print(f"   新路径: {self.save_path.resolve()}")

            # 提示用户路径变更的影响
            if hasattr(self, 'is_monitoring') and self.is_monitoring:
                print("⚠️ 注意: 路径修改后正在运行的监控将使用新路径")
                print("   如需确保生效，建议重启监控")
            
            return True
        except Exception as e:
            print(f"❌ 设置保存路径失败: {e}")
            return False
    
    def get_clipboard_text(self):
        """获取剪贴板中的文本内容"""
        try:
            return pyperclip.paste()
        except Exception as e:
            print(f"获取剪贴板文本失败: {e}")
            return None
    
    def paste_latest_file_path(self):
        """粘贴最新保存的文件路径到当前光标位置"""
        try:
            if self.latest_saved_file:
                # 检查文件是否仍然存在
                if Path(self.latest_saved_file).exists():
                    # 获取完整的绝对路径
                    file_path = str(Path(self.latest_saved_file).resolve())
                    
                    # 首先尝试使用剪贴板方式粘贴（更可靠）
                    try:
                        # 备份当前剪贴板内容
                        original_clipboard = self.get_clipboard_text()
                        
                        # 将文件路径复制到剪贴板
                        pyperclip.copy(file_path)
                        
                        # 短暂延迟确保快捷键释放
                        time.sleep(0.1)
                        
                        # 模拟Ctrl+V粘贴
                        self.keyboard_controller.press(Key.ctrl)
                        self.keyboard_controller.press('v')
                        self.keyboard_controller.release('v')
                        self.keyboard_controller.release(Key.ctrl)
                        
                        # 稍等一下让粘贴操作完成
                        time.sleep(0.1)
                        
                        # 恢复原来的剪贴板内容
                        if original_clipboard:
                            threading.Timer(0.5, lambda: pyperclip.copy(original_clipboard)).start()
                        
                        print(f"✅ 已通过剪贴板粘贴文件路径: {Path(self.latest_saved_file).name}")
                        return True
                        
                    except Exception as clipboard_error:
                        print(f"⚠️ 剪贴板粘贴失败，尝试直接输入: {clipboard_error}")
                        # 备用方案：直接键盘输入
                        time.sleep(0.1)
                        self.keyboard_controller.type(file_path)
                        print(f"✅ 已通过键盘输入文件路径: {Path(self.latest_saved_file).name}")
                        return True
                else:
                    print(f"⚠️ 文件不存在: {self.latest_saved_file}")
                    return False
            else:
                print("📝 还没有保存任何截图文件")
                return False
        except Exception as e:
            print(f"❌ 粘贴文件路径失败: {e}")
            print(f"🔧 错误详情: {type(e).__name__}: {str(e)}")
            # 尝试重新设置快捷键
            try:
                print("🔄 尝试重新注册快捷键...")
                keyboard.remove_hotkey(self.hotkey)
                time.sleep(0.1)
                keyboard.add_hotkey(self.hotkey, self.paste_latest_file_path)
                print(f"✅ 快捷键已重新注册: {self.hotkey.upper()}")
            except Exception as hotkey_error:
                print(f"❌ 重新注册快捷键失败: {hotkey_error}")
            return False
    
    def setup_hotkey(self):
        """设置全局快捷键"""
        try:
            # 先尝试移除可能存在的旧快捷键
            try:
                keyboard.remove_hotkey(self.hotkey)
                print(f"🔄 已移除旧的快捷键: {self.hotkey.upper()}")
            except:
                # 如果快捷键不存在，忽略错误
                pass
            
            # 短暂延迟
            time.sleep(0.1)
            
            # 使用配置文件中的快捷键
            keyboard.add_hotkey(self.hotkey, self.paste_latest_file_path)
            print(f"⌨️  快捷键设置成功: {self.hotkey.upper()} - 粘贴最新截图路径")
            print(f"🔧 调试信息: 快捷键已注册到全局热键系统")
            
            # 测试快捷键是否正常工作
            print(f"💡 使用提示:")
            print(f"   1. 确保程序以管理员身份运行（某些应用可能需要）")
            print(f"   2. 在任意文本框中按 {self.hotkey.upper()} 来粘贴路径")
            print(f"   3. 如果不工作，请检查快捷键是否与其他软件冲突")
            
            return True
        except Exception as e:
            print(f"❌ 设置快捷键失败: {e}")
            print(f"🔧 错误详情: {type(e).__name__}: {str(e)}")
            # 尝试使用备用快捷键
            backup_hotkeys = ['ctrl+alt+v', 'ctrl+shift+p', 'alt+shift+p']
            for backup_hotkey in backup_hotkeys:
                try:
                    print(f"🔄 尝试使用备用快捷键: {backup_hotkey.upper()}")
                    keyboard.add_hotkey(backup_hotkey, self.paste_latest_file_path)
                    self.hotkey = backup_hotkey
                    self.save_config()  # 保存新的快捷键到配置文件
                    print(f"✅ 备用快捷键设置成功: {backup_hotkey.upper()}")
                    return True
                except Exception as backup_error:
                    print(f"❌ 备用快捷键 {backup_hotkey.upper()} 也失败: {backup_error}")
                    continue
            
            print("❌ 所有快捷键设置都失败了")
            print("💡 请尝试:")
            print("   1. 以管理员身份运行程序")
            print("   2. 检查是否有其他软件占用了快捷键")
            print("   3. 手动修改 screenshot_config.json 中的 hotkey 设置")
            return False
    
    def check_and_refresh_hotkey(self):
        """检查快捷键状态并在必要时重新注册"""
        try:
            # 这是一个简单的健康检查
            # 如果有更好的方法检测快捷键状态，可以在这里实现
            pass
        except Exception as e:
            print(f"⚠️ 快捷键状态检查时出现问题，尝试重新注册: {e}")
            self.setup_hotkey()
    
    def get_image_hash(self, image):
        """计算图片的哈希值用于比较"""
        try:
            img_bytes = io.BytesIO()
            image.save(img_bytes, format='PNG')
            img_data = img_bytes.getvalue()
            return hashlib.md5(img_data).hexdigest()
        except Exception as e:
            print(f"计算图片哈希值失败: {e}")
            return None
    
    def get_clipboard_image(self):
        """获取剪贴板中的图片"""
        try:
            # 使用win32clipboard来获取剪贴板中的图片
            win32clipboard.OpenClipboard()
            
            # 检查是否有CF_DIB格式的图片
            if win32clipboard.IsClipboardFormatAvailable(win32con.CF_DIB):
                try:
                    # 获取DIB格式的图片数据
                    dib_data = win32clipboard.GetClipboardData(win32con.CF_DIB)
                    win32clipboard.CloseClipboard()
                    
                    # 将DIB数据转换为PIL Image
                    image = Image.open(io.BytesIO(dib_data))
                    return image
                except Exception as e:
                    print(f"处理DIB格式图片失败: {e}")
            
            # 检查是否有CF_BITMAP格式的图片
            elif win32clipboard.IsClipboardFormatAvailable(win32con.CF_BITMAP):
                try:
                    # 获取BITMAP格式的图片数据
                    bitmap_data = win32clipboard.GetClipboardData(win32con.CF_BITMAP)
                    win32clipboard.CloseClipboard()
                    
                    # 将BITMAP数据转换为PIL Image
                    image = Image.open(io.BytesIO(bitmap_data))
                    return image
                except Exception as e:
                    print(f"处理BITMAP格式图片失败: {e}")
            
            else:
                win32clipboard.CloseClipboard()
                
        except Exception as e:
            print(f"获取剪贴板图片失败: {e}")
            try:
                win32clipboard.CloseClipboard()
            except:
                pass
        
        return None
    
    def save_clipboard_image(self):
        """保存剪贴板中的图片"""
        try:
            image = self.get_clipboard_image()
            if image:
                # 生成文件名
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
                filepath = self.save_path / filename
                
                # 保存图片
                image.save(filepath, 'PNG')
                
                # 更新最新保存的文件路径（存储绝对路径）
                self.latest_saved_file = str(filepath.resolve())
                
                print(f"截图已保存: {filepath.resolve()}")
                return str(filepath.resolve())
            else:
                print("剪贴板中没有检测到图片")
                return None
                
        except Exception as e:
            print(f"保存截图失败: {e}")
            return None
    
    def copy_latest_file_path_to_clipboard(self):
        """将最新保存的文件路径复制到剪贴板"""
        try:
            if self.latest_saved_file:
                if Path(self.latest_saved_file).exists():
                    file_path = str(Path(self.latest_saved_file).resolve())
                    pyperclip.copy(file_path)
                    print(f"✅ 文件路径已复制到剪贴板: {Path(self.latest_saved_file).name}")
                    print(f"📋 您现在可以使用 Ctrl+V 粘贴路径: {file_path}")
                    return True
                else:
                    print(f"⚠️ 文件不存在: {self.latest_saved_file}")
                    return False
            else:
                print("📝 还没有保存任何截图文件")
                return False
        except Exception as e:
            print(f"❌ 复制文件路径到剪贴板失败: {e}")
            return False
    
    def test_hotkey_functionality(self):
        """测试快捷键功能是否正常"""
        print("\n🧪 开始测试快捷键功能...")
        
        # 创建一个测试文件路径
        test_path = "C:\\Test\\Path\\test_screenshot.png"
        original_file = self.latest_saved_file
        self.latest_saved_file = test_path
        
        # 测试剪贴板复制功能
        try:
            original_clipboard = self.get_clipboard_text()
            pyperclip.copy("测试路径复制功能")
            current_clipboard = pyperclip.paste()
            if current_clipboard == "测试路径复制功能":
                print("✅ 剪贴板操作正常")
                
                # 恢复原剪贴板内容
                if original_clipboard:
                    pyperclip.copy(original_clipboard)
            else:
                print("❌ 剪贴板操作异常")
        except Exception as e:
            print(f"❌ 剪贴板测试失败: {e}")
        
        # 测试键盘控制器
        try:
            # 这里只是测试键盘控制器是否能正常创建
            test_controller = Controller()
            print("✅ 键盘控制器正常")
        except Exception as e:
            print(f"❌ 键盘控制器测试失败: {e}")
        
        # 恢复原始文件路径
        self.latest_saved_file = original_file
        
        print("🧪 测试完成。如果上面显示正常，快捷键应该能工作。")
        print("💡 如果快捷键仍然不工作，可能是:")
        print("   1. 需要管理员权限运行程序")
        print("   2. 快捷键被其他软件占用")
        print("   3. 目标应用程序阻止外部输入")
        print("")
        return True

    def monitor_clipboard(self):
        """监控剪贴板变化"""
        self.is_monitoring = True
        
        print(f"📁 开始监控剪贴板，保存路径: {self.save_path.resolve()}")
        print("📸 使用您的截图软件截图并复制到剪贴板，图片将自动保存")
        print(f"⌨️  使用 {self.hotkey.upper()} 快捷键直接粘贴最新截图的完整路径（包含盘符）")
        print("📋 备用方案: 按 Ctrl+Shift+C 将最新截图路径复制到剪贴板")
        print("🚪 按 Ctrl+C 退出程序")
        print("-" * 50)
        
        # 设置快捷键
        self.setup_hotkey()
        
        # 设置备用快捷键（复制到剪贴板）
        try:
            keyboard.add_hotkey('ctrl+shift+c', self.copy_latest_file_path_to_clipboard)
            print(f"⌨️  备用快捷键设置成功: CTRL+SHIFT+C - 复制最新截图路径到剪贴板")
        except Exception as e:
            print(f"⚠️ 备用快捷键设置失败: {e}")
        
        # 运行初始测试
        self.test_hotkey_functionality()
        
        # 显示启动通知
        self.show_startup_notification()
        
        # 隐藏控制台窗口
        self.hide_console_window()
        
        while True:
            try:
                # 检查剪贴板是否有图片
                image = self.get_clipboard_image()
                
                if image:
                    # 计算当前图片的哈希值
                    current_hash = self.get_image_hash(image)
                    
                    # 只有当图片哈希值与上次不同时才保存
                    if current_hash and current_hash != self.last_image_hash:
                        # 保存图片
                        saved_path = self.save_clipboard_image()
                        if saved_path:
                            self.last_image_hash = current_hash
                            print(f"检测到新图片，已保存: {saved_path}")
                    elif current_hash == self.last_image_hash:
                        # 这是相同的图片，不需要保存
                        pass
                
                # 短暂休眠避免过度占用CPU
                time.sleep(0.5)
                
                # 每100次循环检查一次快捷键状态
                self.hotkey_check_counter += 1
                if self.hotkey_check_counter >= 100:
                    self.hotkey_check_counter = 0
                    self.check_and_refresh_hotkey()
                
            except KeyboardInterrupt:
                print("\n正在退出...")
                break
            except Exception as e:
                print(f"监控过程中出现错误: {e}")
                time.sleep(1)

def main():
    """主函数"""
    print("=== 剪贴板截图保存器 ===")
    
    # 创建截图保存器
    saver = ClipboardScreenshotSaver()
    
    # 启动剪贴板监控
    saver.monitor_clipboard()

if __name__ == "__main__":
    main() 