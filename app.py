import streamlit as st

st.set_page_config(page_title="神经退行性疾病检测工具", layout="wide")

st.title("神经退行性疾病检测工具")
st.markdown("""
本工具提供以下功能：

- **ND2 转换** - 将 Nikon ND2 显微镜文件转换为 OME-TIFF 格式
- **荧光分析** - 分析 TIFF 图像荧光强度，计算 ROI 平均强度

请在左侧导航栏选择对应功能页面。
""")

st.info("👈 点击左侧导航栏开始使用")