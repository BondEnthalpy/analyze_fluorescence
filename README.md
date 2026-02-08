# 荧光分析脚本 - 使用文档

## 概述
`analyze_fluorescence.py` 是一个用于批量处理荧光显微镜图像（TIFF格式）的Python脚本。
它可以自动检测荧光区域，执行形态学分析（背景扣除/腐蚀），计算平均强度，并将结果导出到Excel电子表格中。

## 功能特性
- **批量处理**：自动处理指定目录下的所有 `.tif` 或 `.tiff` 文件。
- **多通道支持**：处理多通道图像（例如 OME-TIFF），根据配置处理交替通道。
- **自动分割**：使用 Otsu 阈值分割和轮廓检测来寻找感兴趣区域 (ROI)。
- **强度分析**：计算原始区域和腐蚀后的内部区域（模拟细胞质/细胞核分离或背景排除）的平均强度。
- **Excel 导出**：将所有数据汇总到一个 Excel 文件中。
- **可视化验证**：生成带有检测轮廓的注释图像以供验证。

## 先决条件
确保已安装 Python。需要安装以下库：

```bash
pip install numpy opencv-python-headless tifffile pandas openpyxl
```

## 使用方法

### 方法一：图形界面 (推荐)
1.  **准备数据**：将所有 TIFF 图像放在同一个文件夹中。
2.  **启动程序**：
    - 双击运行 `start_app.command` 文件。
    - 或者在终端中运行：
      ```bash
      ./start_app.command
      ```
3.  **操作步骤**：
    - 网页会自动在浏览器中打开。
    - 点击 **“选择文件夹”** 按钮，选择包含图像的文件夹。
    - 或者直接粘贴文件夹的完整路径。
    - 点击 **“运行分析”**。

4.  **查看结果**：
    - 页面下方会显示分析结果表格和处理后的图像预览。
    - 结果文件（Excel 和 图像）会自动保存在您选择的文件夹下的 `analysis_results` 目录中。

### 方法二：命令行脚本 (高级)
1.  **运行脚本**：
    ```bash
    python analyze_fluorescence.py
    ```
2.  **输入路径**：按提示输入文件夹路径。

## 输出结构

```
输入文件夹/
├── image1.tif
├── image2.tif
└── analysis_results/          <-- 脚本创建
    ├── image1_ch0_result.png
    ├── image1_ch2_result.png
    ├── ...
    └── analysis_results.xlsx  <-- 汇总数据
```

## 故障排除
- **未找到轮廓 (No contours found)**：尝试在脚本中调整阈值参数，或确保图像具有足够的对比度。
- **缺少模块 (Missing modules)**：运行上面的 `pip install` 命令来安装依赖项。
