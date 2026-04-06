import streamlit as st
import os
import pandas as pd
from pathlib import Path
from nd2_converter import batch_convert, get_nd2_files_count, ConversionResult

# Constants
DEFAULT_ROOT = "/Volumes/WJW/科研/神经退行性疾病检测/数据"


def get_subdirectories(path):
    """Return list of subdirectories in given path."""
    try:
        return [d for d in os.listdir(path)
                if os.path.isdir(os.path.join(path, d)) and not d.startswith('.')]
    except (PermissionError, FileNotFoundError):
        return []


def main():
    st.set_page_config(page_title="ND2 转换", layout="wide")

    st.title("ND2 文件转换")
    st.markdown("""
    将 Nikon ND2 显微镜文件转换为 OME-TIFF 格式。
    支持多 Position 文件自动分割。
    """)

    # Initialize current path
    if 'nd2_current_path' not in st.session_state:
        if os.path.exists(DEFAULT_ROOT):
            st.session_state.nd2_current_path = DEFAULT_ROOT
        else:
            st.session_state.nd2_current_path = os.path.expanduser("~")

    # File Browser UI
    st.subheader("文件夹浏览")

    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        st.code(st.session_state.nd2_current_path, language="bash")
    with col2:
        if st.button("⬆️ 返回上级", use_container_width=True):
            parent = os.path.dirname(st.session_state.nd2_current_path)
            if parent and os.path.exists(parent):
                st.session_state.nd2_current_path = parent
                st.rerun()

    # Subdirectory buttons
    subdirs = get_subdirectories(st.session_state.nd2_current_path)
    if subdirs:
        st.write(f"当前目录下的文件夹 ({len(subdirs)}个):")
        cols = st.columns(4)
        for i, subdir in enumerate(sorted(subdirs)):
            with cols[i % 4]:
                if st.button(f"📁 {subdir}", key=f"nd2_dir_{i}_{subdir}", use_container_width=True):
                    st.session_state.nd2_current_path = os.path.join(
                        st.session_state.nd2_current_path, subdir
                    )
                    st.rerun()
    else:
        st.info("此文件夹下没有子文件夹。")

    st.divider()

    # Action Section
    st.subheader("转换操作")
    input_folder = st.session_state.nd2_current_path

    # Show ND2 file count
    nd2_count = get_nd2_files_count(Path(input_folder))

    col_info, col_act = st.columns([0.7, 0.3])
    with col_info:
        st.write(f"将要转换的文件夹: **{os.path.basename(input_folder)}**")
        st.caption(f"完整路径: {input_folder}")
        if nd2_count > 0:
            st.info(f"发现 {nd2_count} 个 ND2 文件")
        else:
            st.warning("此文件夹中没有 ND2 文件")

    with col_act:
        run_convert = st.button("🚀 开始转换", type="primary", use_container_width=True)

    if run_convert:
        if nd2_count == 0:
            st.error("没有 ND2 文件可转换")
            return

        input_dir = Path(input_folder)
        output_dir = input_dir / "converted"

        st.info(f"正在转换... 输出目录: `{output_dir}`")

        progress_bar = st.progress(0)
        status_text = st.empty()

        def update_progress(current, total, filename):
            progress_bar.progress(int((current / total) * 100))
            status_text.text(f"正在处理 {current}/{total}: {filename}")

        try:
            results = batch_convert(input_dir, output_dir, progress_callback=update_progress)

            if results:
                success_count = sum(1 for r in results if r.success)
                fail_count = len(results) - success_count
                total_outputs = sum(len(r.output_files) if r.output_files else 0
                                    for r in results if r.success)

                progress_bar.progress(100)
                status_text.empty()

                st.success(f"转换完成！成功 {success_count} 个，失败 {fail_count} 个，输出 {total_outputs} 个文件")
                st.write(f"输出目录: `{output_dir}`")

                # Results table
                df_data = []
                for r in results:
                    if r.success:
                        for out_file in r.output_files:
                            df_data.append({
                                "输入文件": Path(r.input_file).name,
                                "输出文件": Path(out_file).name,
                                "状态": "成功"
                            })
                    else:
                        df_data.append({
                            "输入文件": Path(r.input_file).name,
                            "输出文件": "-",
                            "状态": f"失败: {r.error}"
                        })

                df = pd.DataFrame(df_data)
                st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error(f"转换过程中发生错误: {e}")


if __name__ == "__main__":
    main()