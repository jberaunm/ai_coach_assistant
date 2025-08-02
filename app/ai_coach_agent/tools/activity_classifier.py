import statistics
import copy
from typing import Dict, List, Any

def segment_activity_by_pace(activity_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Segments a running activity's laps into 'Warm up', 'Main', and 'Cool down' 
    based on a statistical analysis of lap pace.

    This function uses a more robust approach to identify the core "Main" 
    segment. It first finds the average pace of the middle 50% of laps and then 
    classifies any lap within a small percentage deviation of this average as 
    part of the main segment. The longest contiguous block of these laps is 
    then designated as the "Main" segment, with the preceding and succeeding 
    laps classified as "Warm up" and "Cool down" respectively.

    Args:
        activity_data: A dictionary containing activity details, including a list 
                       of laps with 'pace' values.

    Returns:
        A new dictionary with the same structure as the input, but with a new 
        'segment' key added to each lap, classified as "Warm up", "Main", or 
        "Cool down".
    """
    print(f"[ActivityClassifier_tool] Segmenting activity by pace")
    
    # Create a deep copy of the input data to avoid modifying the original object.
    segmented_data = copy.deepcopy(activity_data)
    laps = segmented_data.get("laps", [])

    if not laps:
        return segmented_data

    # --- Step 1: Identify a dynamic threshold based on the middle of the activity ---
    # We assume the main effort is typically in the middle of the run.
    num_laps = len(laps)
    mid_start_index = num_laps // 4
    mid_end_index = num_laps - mid_start_index
    
    # Get the paces of the middle 50% of the laps.
    middle_paces = [laps[i]["pace"] for i in range(mid_start_index, mid_end_index)]

    if not middle_paces:
        # If there are too few laps, just classify all as Main.
        main_paces_start_index = 0
        main_paces_end_index = num_laps - 1
    else:
        # Calculate the average pace of the middle segment as a baseline for the Main segment.
        main_pace_avg = statistics.mean(middle_paces)
        
        # We use a small percentage deviation from the average as our threshold.
        # This makes the algorithm more adaptive than a static multiplier.
        # 0.10 (10%) is a reasonable starting value, can be tuned.
        threshold_percentage = 0.10
        min_pace = main_pace_avg * (1 - threshold_percentage)
        max_pace = main_pace_avg * (1 + threshold_percentage)

        # --- Step 2: Identify all laps that meet the "Main" pace criteria ---
        main_lap_indices = [
            i for i, lap in enumerate(laps)
            if min_pace <= lap["pace"] <= max_pace
        ]
        
        # --- Step 3: Find the longest contiguous block of "Main" laps ---
        longest_segment_start = -1
        longest_segment_end = -1
        
        if main_lap_indices:
            longest_segment_start = main_lap_indices[0]
            longest_segment_end = main_lap_indices[0]
            current_segment_start = main_lap_indices[0]
            max_length = 1
            current_length = 1

            for i in range(1, len(main_lap_indices)):
                if main_lap_indices[i] == main_lap_indices[i-1] + 1:
                    current_length += 1
                else:
                    if current_length > max_length:
                        max_length = current_length
                        longest_segment_start = current_segment_start
                        longest_segment_end = main_lap_indices[i-1]
                    
                    current_segment_start = main_lap_indices[i]
                    current_length = 1
            
            # Check the final segment after the loop
            if current_length > max_length:
                longest_segment_start = current_segment_start
                longest_segment_end = main_lap_indices[-1]

            main_paces_start_index = longest_segment_start
            main_paces_end_index = longest_segment_end
        else:
            # If no main segment is found, classify all laps as Main by default
            main_paces_start_index = 0
            main_paces_end_index = num_laps - 1

    # --- Step 4: Classify all laps based on the identified main segment ---
    for i, lap in enumerate(segmented_data["laps"]):
        if i < main_paces_start_index:
            lap["segment"] = "Warm up"
        elif main_paces_start_index <= i <= main_paces_end_index:
            lap["segment"] = "Main"
        else: # i > main_paces_end_index
            lap["segment"] = "Cool down"

    return segmented_data

# --- Example Usage ---

# Example 1: Activity with clear segments
activity_data_1 = {
    "activity_id": 15194488126,
    "laps": [
        {"lap_index": 1, "pace": 3.06},
        {"lap_index": 2, "pace": 3.15},
        {"lap_index": 3, "pace": 3.61},
        {"lap_index": 4, "pace": 3.53},
        {"lap_index": 5, "pace": 3.61},
        {"lap_index": 6, "pace": 3.72},
        {"lap_index": 7, "pace": 2.94},
        {"lap_index": 8, "pace": 2.68}
    ]
}

# Example 2: Activity with consistent pace (all Main)
activity_data_2 = {
    "activity_id": 15233791332,
    "laps": [
        {"lap_index": 1, "pace": 3.46},
        {"lap_index": 2, "pace": 3.48},
        {"lap_index": 3, "pace": 3.47},
        {"lap_index": 4, "pace": 3.5},
        {"lap_index": 5, "pace": 3.45},
        {"lap_index": 6, "pace": 3.55},
        {"lap_index": 7, "pace": 3.47},
        {"lap_index": 8, "pace": 3.56}
    ]
}
