<<<<<<< HEAD
# A-PDF-translator
A totally free translator which can help you translate the english articles to Chinese.
=======
# PDF 文献翻译助手 (PDF Layout Translator)

这是一个基于 Python 的桌面应用程序，旨在帮助用户将英文 PDF 文献翻译成中文，同时保持原始排版布局。

## 功能特点

- **保持排版**：利用 `pdf2zh` (PDFMathTranslate) 技术，精准识别并替换 PDF 中的文本，保留公式、图表和段落结构。
- **多引擎支持**：
  - **Google Translate** (默认)：免费，无需 API Key，但需要稳定的网络连接。
  - **DeepL**：翻译质量高，需要 API Key。
  - **OpenAI (GPT)**：支持上下文理解，适合学术文献，需要 API Key。
- **简单易用**：拖拽文件即可添加，一键翻译。
- **批量处理**：支持一次性添加多个 PDF 文件进行翻译。

## 快速开始

### 1. 安装依赖

确保你的系统已安装 Python 3.8 或更高版本。在终端中运行以下命令安装所需依赖：

```bash
pip install -r pdf_translator_app/requirements.txt
```

或者直接运行启动脚本（macOS/Linux）：

```bash
sh run.sh
```

### 2. 运行应用

```bash
python pdf_translator_app/main.py
```

### 3. 使用说明

1.  **添加文件**：将 PDF 文件拖入窗口中央的虚线区域，或点击 "Add Files" 按钮选择文件。
2.  **选择服务**：
    -   默认使用 `google`。如果网络受限，请确保配置了系统代理。
    -   如果拥有 DeepL 或 OpenAI 的 API Key，建议选择对应服务以获得更好的翻译质量。
3.  **配置 API Key** (可选)：
    -   如果选择了 `deepl` 或 `openai`，请在 "API Key" 输入框中填入你的密钥。
    -   对于 OpenAI，如果你使用第三方代理接口，可以在 "Base URL" 中填入代理地址。
4.  **开始翻译**：点击 "Start Translation" 按钮。翻译完成后，应用会自动打开输出文件夹。

## 常见问题

**Q: 翻译后的 PDF 打开是乱码？**
A: `pdf2zh` 会尝试嵌入中文字体。如果仍然乱码，请检查你的系统是否安装了常见的中文字体（如 SimHei, SimSun）。

**Q: 翻译速度很慢？**
A: 翻译速度取决于网络状况和所选服务。Google 翻译通常较快，OpenAI GPT-4 可能较慢但质量最好。

**Q: 扫描版 PDF 能翻译吗？**
A: 本应用主要针对文字版 PDF（可选中文字）。对于扫描版（图片型）PDF，目前暂不支持直接翻译，建议先使用 OCR 工具转为文字版 PDF。

## 技术栈

- **GUI**: PyQt6
- **核心引擎**: pdf2zh (基于 PyMuPDF)
- **语言**: Python

## 开发者

- 本项目开源，欢迎修改和分发。
>>>>>>> 20a28c8 (feat: complete PDF translator app with multi-language support and UI improvements)
