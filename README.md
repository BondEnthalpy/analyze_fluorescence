# 荧光图像分析工具

用于神经退行性疾病研究的荧光显微镜图像批量分析工具，支持多页 TIFF/OME-TIFF 格式。

## 功能特性

- **批量处理**：自动处理文件夹内所有 `.tif` 或 `.tiff` 文件
- **多页支持**：读取 TIFF 文件的所有页，智能处理偶数页 (0, 2, 4, 6...)
- **自动分割**：使用 Otsu 阈值分割和轮廓检测寻找 ROI
- **形态学分析**：计算原始区域和腐蚀后区域（缩小30像素）的平均荧光强度
- **结果导出**：生成 Excel 表格和带标注的可视化图像
- **Web 界面**：基于 Streamlit 的图形界面，支持文件夹浏览和进度显示

## 安装依赖

```bash
pip install numpy opencv-python tifffile pandas openpyxl streamlit watchdog
```

或使用虚拟环境：

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## 使用方法

### 方法一：Web 界面（推荐）

```bash
streamlit run app.py
```

浏览器自动打开界面：
1. 使用文件夹浏览器导航到数据目录
2. 点击 **"🚀 在此文件夹运行分析"**
3. 查看结果表格和图像预览
4. 结果自动保存到 `analysis_results_YYYYMMDD_HHMMSS/` 目录（每次运行生成独立文件夹）

### 方法二：macOS 快捷启动

双击 `start_app.command` 文件（自动激活虚拟环境并启动 Streamlit）

### 方法三：命令行

```bash
python analyze_fluorescence.py
# 按提示输入文件夹路径
```

## 输入数据格式

支持的 TIFF 文件类型：
- 单页灰度图像
- 多页 TIFF（如时间序列、Z-stack）
- OME-TIFF 格式

**处理逻辑**：读取文件的所有页，仅处理偶数索引页（0, 2, 4, 6...）

## 输出结构

每次运行都会生成带有时间戳的独立输出目录，避免覆盖之前的结果：

```
输入文件夹/
├── image1.ome.tif
├── image2.ome.tif
├── analysis_results_20260406_143052/    # 第一次运行（时间戳格式：YYYYMMDD_HHMMSS）
│   ├── image1_page0_result.png           # 标注图像：绿色=原始轮廓，蓝色=腐蚀后轮廓
│   ├── image1_page2_result.png
│   ├── image1_page4_result.png
│   ├── image2_page0_result.png
│   ├── ...
│   └── analysis_results.xlsx             # 汇总数据（按文件名和页数排序）
├── analysis_results_20260407_091530/    # 第二次运行
│   └── ...
└── analysis_results_20260408_160200/    # 第三次运行
    └── ...
```

## Excel 输出字段

| 字段 | 说明 |
|------|------|
| File Name | 原始文件名 |
| Page | TIFF 页数索引 |
| Mean Intensity (Original) | 原始 ROI 平均荧光强度 |
| Mean Intensity (Eroded) | 腐蚀后 ROI 平均荧光强度（排除边缘） |
| Difference | 两者差值（边缘效应评估） |

## 分析流程

1. **读取**：使用 `tifffile` 读取所有 TIFF 页
2. **筛选**：仅处理偶数页 (0, 2, 4...)
3. **预处理**：归一化到 8-bit，高斯模糊
4. **分割**：Otsu 阈值 + 轮廓检测（取最大区域）
5. **腐蚀**：距离变换收缩 30 像素，生成内部掩膜
6. **计算**：分别计算原始区域和腐蚀区域的平均强度
7. **可视化**：生成带标注的结果图像

## 故障排除

| 问题 | 解决方法 |
|------|----------|
| 未找到轮廓 | 检查图像对比度，或调整阈值参数 |
| 缺少模块 | 运行 `pip install` 安装依赖 |
| OME-TIFF 读取错误 | 程序会自动读取所有页，忽略 OME 元数据声明 |
| 结果排序混乱 | 确保文件名包含数字时使用前导零（如 page01, page02） |

## 默认数据路径

程序默认数据目录：
```
/Volumes/WJW/科研/神经退行性疾病检测/数据
```

可在 `app.py` 中修改 `DEFAULT_ROOT` 变量。
