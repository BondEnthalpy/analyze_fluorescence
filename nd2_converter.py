#!/usr/bin/env python3
"""
ND2 to OME-TIFF Conversion Module

Converts Nikon ND2 microscope files to OME-TIFF format.
Supports splitting multi-position files into separate outputs.
"""

from dataclasses import dataclass
from typing import List, Optional, Callable
from pathlib import Path
import nd2
import numpy as np
import tifffile


@dataclass
class ConversionResult:
    """Result of a single file conversion."""
    success: bool
    input_file: str
    output_files: Optional[List[str]] = None
    error: Optional[str] = None


def convert_nd2_to_ometiff(input_path: Path, output_dir: Path) -> List[str]:
    """
    Convert a single ND2 file to OME-TIFF format.
    If the file contains multiple XY positions, splits into separate files.

    Args:
        input_path: Path to the ND2 file
        output_dir: Directory for output files

    Returns:
        List of output file paths

    Raises:
        Exception: Any error during conversion
    """
    output_files = []

    with nd2.ND2File(input_path) as nd2_file:
        sizes = nd2_file.sizes
        num_positions = sizes.get('P', 1)

        if num_positions <= 1:
            # Single position - direct output
            output_path = output_dir / f"{input_path.stem}.ome.tif"
            nd2_file.write_tiff(output_path, include_unstructured_metadata=True)
            output_files.append(str(output_path))
        else:
            # Multiple positions - split output
            dim_order = tuple(sizes.keys())
            data = nd2_file.asarray()
            p_axis = dim_order.index('P')
            dims_without_p = ''.join([d for d in dim_order if d != 'P'])

            for p_idx in range(num_positions):
                pos_data = np.take(data, p_idx, axis=p_axis)
                output_path = output_dir / f"{input_path.stem}_P{p_idx+1}.ome.tif"
                tifffile.imwrite(
                    output_path,
                    pos_data,
                    photometric='minisblack',
                    metadata={'axes': dims_without_p}
                )
                output_files.append(str(output_path))

    return output_files


def batch_convert(
    input_dir: Path,
    output_dir: Path,
    progress_callback: Optional[Callable[[int, int, str], None]] = None
) -> List[ConversionResult]:
    """
    Batch convert all ND2 files in a directory.

    Args:
        input_dir: Directory containing ND2 files
        output_dir: Directory for output files
        progress_callback: Optional callback(current, total, filename) for progress updates

    Returns:
        List of ConversionResult for each processed file
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    nd2_files = sorted(input_dir.glob('*.nd2'))

    if not nd2_files:
        return []

    results = []
    total = len(nd2_files)

    for i, nd2_file in enumerate(nd2_files, 1):
        try:
            output_files = convert_nd2_to_ometiff(nd2_file, output_dir)
            results.append(ConversionResult(
                success=True,
                input_file=str(nd2_file),
                output_files=output_files
            ))
        except Exception as e:
            results.append(ConversionResult(
                success=False,
                input_file=str(nd2_file),
                error=str(e)
            ))

        if progress_callback:
            progress_callback(i, total, nd2_file.name)

    return results


def get_nd2_files_count(input_dir: Path) -> int:
    """
    Count ND2 files in a directory.

    Args:
        input_dir: Directory to scan

    Returns:
        Number of .nd2 files found
    """
    return len(list(input_dir.glob('*.nd2')))