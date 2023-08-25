"""Utility functions.

This module contains utility functions dedicated to frame range operations
"""
import clique

from openpype.lib import Logger
from openpype.client import get_asset_by_name

log = Logger.get_logger(__name__)


def get_frame_start_str(frame_start, frame_end):
    """Get frame start string.

    Args:
        frame_start (int): first frame
        frame_end (int): last frame

    Returns:
        str: frame start string
    """
    padding = len(str(frame_end))
    return str(frame_start).zfill(padding)


def get_asset_frame_range(project_name, asset_name, asset_doc=None):
    """Get the current assets frame range and handles.

    Args:
        project_name (str): Name of project.
        asset_name (str): Name of asset.
        asset_doc (Optional[dict]): Asset document.
    Returns:
        dict: with frame start, frame end, handle start, handle end.
    """

    # Set frame start/end
    if not asset_doc:
        asset_doc = get_asset_by_name(
            project_name,
            asset_name,
            fields=[
                "data.frameStart",
                "data.frameEnd",
                "data.handleStart",
                "data.handleEnd"
            ]
        )

    frame_start = asset_doc["data"].get("frameStart")
    frame_end = asset_doc["data"].get("frameEnd")

    if frame_start is None or frame_end is None:
        return

    handle_start = asset_doc["data"].get("handleStart", 0)
    handle_end = asset_doc["data"].get("handleEnd", 0)

    return {
        "frameStart": frame_start,
        "frameEnd": frame_end,
        "handleStart": handle_start,
        "handleEnd": handle_end
    }


def get_frame_range_from_list_of_files(collected_files):
    """Get frame range from sequence files.

    Args:
        collected_files (list[str]): list of files

    Returns:
        Any[tuple[int, int], tuple[None, None]]: frame range or None
            if not possible
    """

    collections, remainder = clique.assemble(collected_files)
    if not collections:
        # No sequences detected and we can't retrieve
        # frame range from single file
        return None, None

    assert len(collections) == 1, (
        "Multiple sequences detected in collected files"
    )

    collection = collections[0]
    repres_frames = list(collection.indexes)

    return repres_frames[0], repres_frames[-1]