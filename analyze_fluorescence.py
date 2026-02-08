import cv2
import numpy as np
import tifffile
import os
import pandas as pd

def analyze_fluorescence(image_path, output_dir):
    """
    Analyzes fluorescence in a given image and returns the results.
    """
    print(f"Processing: {image_path}")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Read image
    try:
        img = tifffile.imread(image_path)
    except Exception as e:
        print(f"Error reading file {image_path}: {e}")
        return []

    print(f"Image shape: {img.shape}")

    # Determine channels to process based on dimensions
    image_list = []
    if img.ndim == 2:
        image_list = [(0, img)]
    elif img.ndim == 3:
        # Assume (C, H, W) or (Z, H, W). Process alternate channels.
        for i in range(img.shape[0]):
            if i % 2 == 0: 
                image_list.append((i, img[i]))
    elif img.ndim == 4:
        # Assume (Z, C, H, W) or similar. 
        # For simplicity, if 4D, let's try to iterate the second dimension if it looks like channels, 
        # or the first if it looks like Z and channels are inside.
        # Given the previous context, let's stick to a simple heuristic or just process 
        # the first available dimension that makes sense, or flatten.
        # For now, let's try to treat axis 0 as C/Z and process alternate.
         for i in range(img.shape[0]):
            if i % 2 == 0: 
                image_list.append((i, img[i]))
    
    if not image_list:
        print(f"No suitable channels found in {image_path}")
        return []

    results = []
    base_name = os.path.basename(image_path)

    for idx, channel_img in image_list:
        # Preprocessing (normalize to 8-bit)
        if channel_img.dtype != np.uint8:
            min_val = np.min(channel_img)
            max_val = np.max(channel_img)
            if max_val > min_val:
                img_8bit = ((channel_img - min_val) / (max_val - min_val) * 255).astype(np.uint8)
            else:
                img_8bit = np.zeros_like(channel_img, dtype=np.uint8)
        else:
            img_8bit = channel_img.copy()

        # Blur and Threshold
        blurred = cv2.GaussianBlur(img_8bit, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            print(f"No contours found in {base_name} channel {idx}")
            continue

        # Largest contour
        c = max(contours, key=cv2.contourArea)

        # Masks
        mask_original = np.zeros_like(img_8bit, dtype=np.uint8)
        cv2.drawContours(mask_original, [c], -1, 255, thickness=cv2.FILLED)

        # Distance Transform & Erosion (Shrink by 30 pixels)
        dist_transform = cv2.distanceTransform(mask_original, cv2.DIST_L2, 5)
        mask_eroded = (dist_transform > 30).astype(np.uint8) * 255

        # Calculate Means
        mean_original = np.mean(channel_img[mask_original > 0]) if np.any(mask_original) else 0
        mean_eroded = np.mean(channel_img[mask_eroded > 0]) if np.any(mask_eroded) else 0
        diff = mean_original - mean_eroded

        # Save result image
        vis_img = cv2.cvtColor(img_8bit, cv2.COLOR_GRAY2BGR)
        cv2.drawContours(vis_img, [c], -1, (0, 255, 0), 2)
        contours_eroded, _ = cv2.findContours(mask_eroded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(vis_img, contours_eroded, -1, (255, 0, 0), 2)
        
        cv2.putText(vis_img, f"Mean(Org)={mean_original:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(vis_img, f"Mean(Ero)={mean_eroded:.1f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        cv2.putText(vis_img, f"Diff={diff:.1f}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        save_name = os.path.join(output_dir, f"{os.path.splitext(base_name)[0]}_ch{idx}_result.png")
        cv2.imwrite(save_name, vis_img)

        # Collect data
        results.append({
            "File Name": base_name,
            "Channel": idx,
            "Mean Intensity (Original)": mean_original,
            "Mean Intensity (Eroded)": mean_eroded,
            "Difference": diff
        })
        
    return results

def batch_process_folder(folder_path, progress_callback=None):
    """
    Processes all TIFF files in a folder and saves results.
    """
    output_dir = os.path.join(folder_path, "analysis_results")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    all_results = []
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.tif', '.tiff'))]
    # Sort files naturally or alphabetically
    files.sort()
    
    total_files = len(files)
    print(f"Found {total_files} TIFF files.")

    for i, f in enumerate(files):
        full_path = os.path.join(folder_path, f)
        results = analyze_fluorescence(full_path, output_dir)
        if isinstance(results, list):
            all_results.extend(results)
        
        if progress_callback:
            progress_callback(i + 1, total_files, f)

    if all_results:
        # Sort results by File Name
        all_results.sort(key=lambda x: x.get("File Name", ""))
        
        df = pd.DataFrame(all_results)
        excel_path = os.path.join(output_dir, "analysis_results.xlsx")
        
        try:
            df.to_excel(excel_path, index=False)
            print(f"Successfully saved results to {excel_path}")
        except Exception as e:
            print(f"Error saving Excel file: {e}")
            csv_path = os.path.join(output_dir, "analysis_results.csv")
            df.to_csv(csv_path, index=False)
            print(f"Saved as CSV instead: {csv_path}")
            
    return all_results, output_dir

def main():
    folder_path = input("请输入包含TIFF图片的文件夹路径: ").strip()
    
    # Remove quotes if user added them
    if (folder_path.startswith('"') and folder_path.endswith('"')) or \
       (folder_path.startswith("'") and folder_path.endswith("'")):
        folder_path = folder_path[1:-1]
        
    if not os.path.isdir(folder_path):
        print("Provided path is not a valid directory.")
        return

    batch_process_folder(folder_path)

if __name__ == "__main__":
    main()
