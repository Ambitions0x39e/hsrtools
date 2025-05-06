import sys, os
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QLabel, QWidget, QFileDialog, QDialog, QHBoxLayout, QRadioButton, QButtonGroup)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from PIL import Image

class BackgroundSelectDialog(QDialog):
    def __init__(self, image_path):
        super().__init__()
        self.setWindowTitle("选择背景星级")
        self.setMinimumSize(400, 500)  # 增加窗口高度以适应图片预览
        
        layout = QVBoxLayout()
        
        # 显示当前处理的图片名
        image_name = os.path.basename(image_path)
        self.image_label = QLabel(f"为图片 {image_name} 选择背景星级:")
        layout.addWidget(self.image_label)
        
        # 添加图片预览
        preview_label = QLabel()
        pixmap = QPixmap(image_path)
        # 将图片缩放到合适大小
        scaled_pixmap = pixmap.scaled(256, 256, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        preview_label.setPixmap(scaled_pixmap)
        preview_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(preview_label)
        
        # 创建单选按钮组
        self.button_group = QButtonGroup()
        self.buttons = []  # 存储按钮引用
        for i in range(1, 6):
            radio = QRadioButton(f"{i}星背景")
            self.button_group.addButton(radio, i)
            self.buttons.append(radio)  # 保存按钮引用
            layout.addWidget(radio)
        
        # 默认选中1星
        self.current_index = 0  # 当前选中的索引
        self.buttons[self.current_index].setChecked(True)
        
        # 确认按钮
        confirm_btn = QPushButton("确认")
        confirm_btn.clicked.connect(self.accept)
        layout.addWidget(confirm_btn)
        
        # 添加提示标签
        hint_label = QLabel("使用←→方向键切换星级，Enter确认")
        hint_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint_label)
        
        self.setLayout(layout)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            # 向左切换
            self.current_index = (self.current_index - 1) % 5
            self.buttons[self.current_index].setChecked(True)
        elif event.key() == Qt.Key_Down:
            # 向右切换
            self.current_index = (self.current_index + 1) % 5
            self.buttons[self.current_index].setChecked(True)
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # 回车键确认
            self.accept()
        else:
            super().keyPressEvent(event)
    
    def get_selected_star(self):
        return self.button_group.checkedId()

class ImageOverlayApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("图片叠加工具")
        self.setMinimumSize(400, 300)
        
        # 存储图片路径
        self.base_images = []
        self.selected_images = []
        
        # 创建主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # 创建按钮和标签
        self.base_btn = QPushButton("选择基准图片文件夹")
        self.base_btn.clicked.connect(self.load_base_images)
        
        self.base_label = QLabel("已加载基准图片: 0张")
        
        self.new_btn = QPushButton("选择要叠加的图片文件夹")
        self.new_btn.clicked.connect(self.load_new_images)
        
        self.new_label = QLabel("已选择新图片: 0张")
        
        self.process_btn = QPushButton("开始处理")
        self.process_btn.clicked.connect(self.process_images)
        
        # 添加部件到布局
        layout.addWidget(self.base_btn)
        layout.addWidget(self.base_label)
        layout.addWidget(self.new_btn)
        layout.addWidget(self.new_label)
        layout.addWidget(self.process_btn)
        
    def load_base_images(self):
        # 获取当前文件所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        folder = os.path.join(current_dir, "物品背景")
        
        # 检查文件夹是否存在
        if os.path.exists(folder):
            self.base_images = [os.path.join(folder, f) for f in os.listdir(folder) 
                            if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            self.base_label.setText(f"已加载基准图片: {len(self.base_images)}张")
        else:
            self.base_label.setText("错误: 未找到'物品背景'文件夹")
            
    
    def load_new_images(self):
        folder = QFileDialog.getExistingDirectory(self, "选择要叠加的图片文件夹")
        if folder:
            self.selected_images = [os.path.join(folder, f) for f in os.listdir(folder) 
                                  if f.lower().endswith('.png')]
            self.new_label.setText(f"已选择新图片: {len(self.selected_images)}张")
    
    def process_images(self):
        if not self.selected_images:
            return
                
        output_dir = "overlaid_images"
        os.makedirs(output_dir, exist_ok=True)
        
        # 获取当前文件所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backgrounds_dir = os.path.join(current_dir, "物品背景")
        
        for new_img_path in self.selected_images:
            try:
                # 打开选择背景的对话框
                dialog = BackgroundSelectDialog(new_img_path)
                if dialog.exec() == QDialog.Accepted:
                    selected_star = dialog.get_selected_star()
                    
                    # 查找对应星级的背景图片
                    background_pattern = f"{selected_star}星背景"
                    background_file = next((f for f in os.listdir(backgrounds_dir) 
                                        if background_pattern in f), None)
                    
                    if not background_file:
                        print(f"未找到{selected_star}星背景图片")
                        continue
                    
                    background_path = os.path.join(backgrounds_dir, background_file)
                    
                    # 处理图片叠加
                    new_img = Image.open(new_img_path).convert('RGBA')
                    if new_img.size != (256, 256):
                        new_img = new_img.resize((256, 256))
                    
                    base_img = Image.open(background_path).convert('RGBA')
                    result = Image.alpha_composite(base_img, new_img)
                    
                    # 保存结果
                    # output_name = f"overlay_{selected_star}star_{os.path.basename(new_img_path)}"
                    output_name = f"{os.path.basename(new_img_path)}"
                    output_path = os.path.join(output_dir, output_name)
                    result.save(output_path)
                    
            except Exception as e:
                print(f"处理图片 {new_img_path} 时出错: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageOverlayApp()
    window.show()
    sys.exit(app.exec())