#!/bin/bash

echo "🚀 开始安装打包工具..."
pip install pyinstaller

echo "🧹 清理旧的构建文件..."
rm -rf build dist *.spec

echo "📦 开始打包应用程序..."
# --noconfirm: 不询问确认
# --onedir: 生成一个文件夹（包含可执行文件和依赖），比单文件模式启动更快，兼容性更好
# --windowed:以此模式运行，不显示命令行窗口（macOS下生成.app）
# --name: 指定程序名称
# --clean: 清理缓存
# --paths: 将当前目录加入搜索路径，确保能找到 pdf_translator_app 模块
# --collect-all: 强制收集 pdf2zh 及其所有依赖，防止缺少隐式导入的库
# --icon: (可选) 如果有图标文件，可以用 --icon=icon.icns 指定

pyinstaller --noconfirm --onedir --windowed --clean \
    --name "PDFTranslator" \
    --paths "." \
    --collect-all "pdf2zh" \
    --collect-all "doclayout_yolo" \
    --hidden-import "PyQt6" \
    pdf_translator_app/main.py

echo "✅ 打包完成！"
echo "📂 您的应用位于: dist/PDFTranslator/"
echo "   (macOS 用户请运行 dist/PDFTranslator/PDFTranslator.app)"
