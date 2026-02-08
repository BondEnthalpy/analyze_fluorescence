import streamlit as st
import os
import pandas as pd
from analyze_fluorescence import batch_process_folder
import glob

# Constants
DEFAULT_ROOT = "/Volumes/WJW/科研/神经退行性疾病检测/数据"

def get_subdirectories(path):
    """Returns a list of subdirectories in the given path."""
    try:
        # Filter out hidden files/directories starting with '.'
        return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d)) and not d.startswith('.')]
    except (PermissionError, FileNotFoundError):
        return []

def main():
    st.set_page_config(page_title="荧光图像分析工具", layout="wide")
    
    st.title("荧光图像分析工具")
    st.markdown("""
    该工具用于分析选定文件夹中的 TIFF 图像，自动划定荧光区域并计算荧光强度。
    请在下方浏览并选择包含图像的文件夹进行分析。
    """)

    # Initialize current path in session state
    if 'current_path' not in st.session_state:
        # Default to the specified path if it exists, otherwise expand user home
        if os.path.exists(DEFAULT_ROOT):
             st.session_state.current_path = DEFAULT_ROOT
        else:
             # Fallback if the default path doesn't exist
             st.session_state.current_path = os.path.expanduser("~")

    # File Browser UI
    st.subheader("文件夹浏览")

    # Current path display and "Up" button
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        st.code(st.session_state.current_path, language="bash")
    with col2:
        if st.button("⬆️ 返回上一级", use_container_width=True):
            parent_dir = os.path.dirname(st.session_state.current_path)
            if parent_dir and os.path.exists(parent_dir):
                st.session_state.current_path = parent_dir
                st.rerun()

    # List subdirectories
    subdirs = get_subdirectories(st.session_state.current_path)
    
    if subdirs:
        st.write(f"当前目录下的文件夹 ({len(subdirs)}个):")
        # Display as clickable buttons in a grid
        cols = st.columns(4)
        for i, subdir in enumerate(sorted(subdirs)):
            with cols[i % 4]:
                if st.button(f"📁 {subdir}", key=f"dir_{i}_{subdir}", use_container_width=True):
                    st.session_state.current_path = os.path.join(st.session_state.current_path, subdir)
                    st.rerun()
    else:
        st.info("此文件夹下没有子文件夹。")

    st.divider()

    # Action Section
    st.subheader("分析操作")
    folder_path = st.session_state.current_path
    
    col_act1, col_act2 = st.columns([0.7, 0.3])
    with col_act1:
        st.write(f"将要分析的文件夹: **{os.path.basename(folder_path) if folder_path != '/' else 'Root'}**")
        st.caption(f"完整路径: {folder_path}")
    
    with col_act2:
        run_analysis = st.button("🚀 在此文件夹运行分析", type="primary", use_container_width=True)

    if run_analysis:
        if not folder_path or not os.path.exists(folder_path):
             st.error("无效的文件夹路径。")
             return

        st.info(f"正在处理文件夹: {folder_path}...")
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def update_progress(current, total, filename):
            progress = int((current / total) * 100)
            progress_bar.progress(progress)
            status_text.text(f"正在处理 {current}/{total}: {filename}")

        try:
            results, output_dir = batch_process_folder(folder_path, progress_callback=update_progress)
            
            if results:
                st.success("分析完成！")
                st.write(f"结果已保存至: `{output_dir}`")
                
                # Display Data
                df = pd.DataFrame(results)
                # Sort by filename if it exists
                if "File Name" in df.columns:
                     df = df.sort_values(by="File Name")

                # Rename columns for display
                df_display = df.rename(columns={
                    "File Name": "文件名",
                    "Channel": "通道",
                    "Mean Intensity (Original)": "平均强度(原始)",
                    "Mean Intensity (Eroded)": "平均强度(腐蚀后)",
                    "Difference": "差值"
                })
                
                st.dataframe(df_display, use_container_width=True)
                
                # Visualization
                st.subheader("处理后的图像预览")
                result_images = glob.glob(os.path.join(output_dir, "*_result.png"))
                result_images.sort() # Ensure images are sorted by name
                
                if result_images:
                    cols = st.columns(3)
                    for i, img_path in enumerate(result_images):
                        with cols[i % 3]:
                            st.image(img_path, caption=os.path.basename(img_path), use_container_width=True)
                else:
                    st.warning("未找到可显示的结果图像。")
                    
            else:
                st.warning("未处理任何图像。请检查文件夹是否包含 .tif/.tiff 文件。")
                
        except Exception as e:
            st.error(f"分析过程中发生错误: {e}")

if __name__ == "__main__":
    main()
