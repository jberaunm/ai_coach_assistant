import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.ticker as ticker
from typing import Dict, Any, Optional
import os
from .chromaDB_tools import get_activity_by_id

def plot_running_chart(activity_id: int, save_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a running chart from activity data stored in ChromaDB.
    
    Args:
        activity_id: The Strava activity ID to retrieve and plot
        save_path: Optional path to save the chart image (e.g., "running_chart.png")
                  If not provided, saves to app/uploads/ directory with default name
        
    Returns:
        Dict containing:
            - status: "success" or "error"
            - message: Description of the result
            - chart_path: Path to the saved chart image
            - activity_info: Summary of the activity
    """
    try:
        print(f"[PlotRunningChart tool] START: Creating running chart for activity {activity_id}")
        
        # Get activity data from ChromaDB
        result = get_activity_by_id(activity_id)
        
        if result["status"] != "success":
            return {
                "status": "error",
                "message": f"Failed to retrieve activity data: {result['message']}",
                "chart_path": None,
                "activity_info": None
            }
        
        activity_data = result["activity_data"]
        data_points_streams = activity_data["data_points"]['streams']
        data_points_laps = activity_data["data_points"]['laps']
        
        if not data_points_streams:
            return {
                "status": "error",
                "message": "No data points available for this activity",
                "chart_path": None,
                "activity_info": None
            }
        
        # Convert data points to DataFrame
        df = pd.DataFrame(data_points_streams)

        ####################### Creating 1st chart

        # Convert distance from meters to kilometers
        df['distance_km'] = df['distance_meters'] / 1000

        fig, ax1 = plt.subplots(figsize=(12, 7))

        ### HEARTRATE
        # Create a second y-axis for Heart Rate
        sns.lineplot(x='distance_km', y='heartrate_bpm', data=df, ax=ax1, label='Heart rate', color='red', legend=False)
        ax1.set_ylabel('Heart Rate (bpm)', color='red')
        ax1.tick_params(axis='y', labelcolor='red')
        ax1.grid(False)

        # Set y-limit for Heart Rate axis
        max_heartrate = df['heartrate_bpm'].max()
        ax1.set_ylim(-25, max_heartrate * 1.1)

        # Calculate and plot min, avg, max lines for Heart Rate
        min_heartrate = df['heartrate_bpm'].min()
        avg_heartrate = df['heartrate_bpm'].mean()
        max_heartrate = df['heartrate_bpm'].max()
        ax1.axhline(min_heartrate, color='red', linestyle=':', linewidth=2, label='Min')
        ax1.axhline(avg_heartrate, color='red', linestyle=':', linewidth=2, label='Avg')
        ax1.axhline(max_heartrate, color='red', linestyle=':', linewidth=2, label='Max')

        # Add text labels for min, avg, max Heart Rate
        ax1.text(-0.15, min_heartrate, 'MIN', va='bottom', ha='right', color='red')
        ax1.text(-0.15, avg_heartrate, 'AVG', va='bottom', ha='right', color='red')
        ax1.text(-0.15, max_heartrate, 'MAX', va='bottom', ha='right', color='red')

        # Set only min, avg, and max as tick labels for Altitude
        ax1.set_yticks([min_heartrate, avg_heartrate, max_heartrate])
        ax1.set_yticklabels([f'{min_heartrate:.1f}', f'{avg_heartrate:.1f}', f'{max_heartrate:.1f}'])

        ax1.xaxis.set_major_locator(ticker.MultipleLocator(1))

        ### ALTITUDE
        # Plot Altitude on the first y-axis and fill the area below it
        # Removed the line plot for Altitude
        ax2 = ax1.twinx()
        # Offset the third y-axis to avoid overlapping with the second
        ax2.spines['right'].set_position(('outward', 60))
        ax2.fill_between(df['distance_km'], df['altitude_meters'], color='gray', alpha=0.8, label='Altitude') # Add label here for legend
        ax2.set_ylabel('Altitude (meters)', color='gray')
        ax2.tick_params(axis='y', labelcolor='gray')

        ax2.set_ylabel('')  # Remove the y-axis label
        ax2.set_yticklabels([]) # Remove the tick labels
        ax2.tick_params(axis='y', length=0) # Remove the tick marks
        ax2.grid(False)

        # Set y-limit for Altitude axis
        max_altitude = df['altitude_meters'].max()
        ax2.set_ylim(0, max_altitude * 6)

        ### PACE
        # Create a third y-axis for Pace
        ax3 = ax2.twinx()

        sns.lineplot(x='distance_km', y='velocity_ms', data=df, ax=ax3, label='Pace', color='blue', marker='o', legend=False)
        ax3.set_ylabel('Pace (min/km)', color='blue')
        ax3.tick_params(axis='y', labelcolor='blue')
        ax3.grid(False)

        # Calculate and plot min, avg, max lines for Heart Rate
        min_velocity = df['velocity_ms'][1:].min()
        avg_velocity = df['velocity_ms'][1:].mean()
        max_velocity = df['velocity_ms'].max()
        ax3.axhline(min_velocity, color='blue', linestyle=':', linewidth=2, label='MIN')
        ax3.axhline(avg_velocity, color='blue', linestyle=':', linewidth=2, label='AVG')
        ax3.axhline(max_velocity, color='blue', linestyle=':', linewidth=2, label='MAX')

        # Add text labels for min, avg, max Heart Rate
        ax3.text(df['distance_km'].iloc[-1]+0.1, min_velocity-0.4, 'MIN', va='bottom', ha='left', color='blue')
        ax3.text(df['distance_km'].iloc[-1]+0.1, avg_velocity-0.4, 'AVG', va='bottom', ha='left', color='blue')
        ax3.text(df['distance_km'].iloc[-1]+0.1, max_velocity-0.4, 'MAX', va='bottom', ha='left', color='blue')

        # Set only min, avg, and max as tick labels for Altitude
        ax3.set_yticks([min_velocity, avg_velocity, max_velocity])
        ax3.set_yticklabels([f'{min_velocity:.1f}', f'{avg_velocity:.1f}', f'{max_velocity:.1f}'])

        # Set y-limit for Velocity axis to avoid overlapping Heart Rate
        max_heartrate = df['heartrate_bpm'].max()
        max_velocity = df['velocity_ms'].max()
        ax3.set_ylim(0, max_velocity * 2) # Setting y-limit for Velocity from 0 to 1.5 times the max velocity

        # Function to convert m/s to min/km (pace) and format as MM:SS
        def ms_to_minkm_mmss(velocity_ms):
            if velocity_ms == 0:
                return 'inf'  # Or some other indicator for 0 velocity
            pace_minutes_decimal = (1000 / velocity_ms) / 60
            minutes = int(pace_minutes_decimal)
            seconds = int((pace_minutes_decimal - minutes) * 60)
            return f'{minutes:02d}:{seconds:02d}'

        # Apply the conversion and formatting to the y-axis tick labels for Velocity
        velocity_ticks = ax3.get_yticks()
        ax3.set_yticks(velocity_ticks) # Set the tick locations
        ax3.set_yticklabels([ms_to_minkm_mmss(y) if ms_to_minkm_mmss(y) != 'inf' else 'inf' for y in velocity_ticks])

        # Title and common x-label
        #plt.title('Altitude, Heart Rate, and Velocity vs. Distance')
        ax1.set_xlabel('Distance (km)')

        # Add a combined legend. This requires a bit more manual handling
        lines, labels = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        lines3, labels3 = ax3.get_legend_handles_labels()

        # Combine handles and labels, wrapping single elements in lists
        combined_lines = [lines[0]] + [lines2[0]] + [lines3[0]]
        combined_labels = [labels[0]] + [labels2[0]] + [labels3[0]]

        # using bbox_to_anchor and loc for placement
        ax1.legend(combined_lines, combined_labels,
                loc='lower center',
                bbox_to_anchor=(0.5, 1),
                ncol=3,
                fontsize='medium'
                )

        plt.tight_layout()
        
        # Determine save path - always save the chart
        if save_path:
            chart_path = save_path
        else:
            # Get the uploads directory path
            current_dir = os.path.dirname(os.path.abspath(__file__))
            app_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            uploads_dir = os.path.join(app_dir, "app", "uploads")
            
            # Create uploads directory if it doesn't exist
            os.makedirs(uploads_dir, exist_ok=True)
            
            # Generate default filename
            chart_path = os.path.join(uploads_dir, f"running_chart_activity_{activity_id}_2.png")
        
        # Save the chart
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        print(f"Chart saved to: {chart_path}")
        
        ####################### Creating 2nd chart

        laps_df = pd.DataFrame(data_points_laps)

        # Each lap distance is individual, so we need to accumulate them
        laps_df['cumulative_distance_meters'] = laps_df['distance_meters'].cumsum()
        # Convert distance from meters to kilometers
        laps_df['distance_km'] = laps_df['cumulative_distance_meters'] / 1000

        fig, ax5 = plt.subplots(figsize=(10, 6))

        sns.barplot(x=laps_df['lap_index'], y=laps_df['velocity_ms'], ax=ax5, label='Pace', color='blue', width=0.7)
        ax5.set_ylabel('Pace (min/km)', color='blue')
        ax5.tick_params(axis='y', labelcolor='blue')
        ax5.grid(True,  # Enable grid
                color='gray',  # Set color (e.g., 'gray', 'red', '#CCCCCC')
                linestyle='-.',  # Set line style (e.g., '-', '--', ':', '-.')
                linewidth=0.8,  # Set line width
                alpha=0.9,  # Set transparency
                which='major',  # Apply to 'major', 'minor', or 'both' ticks
                )

        max_velocity = laps_df['velocity_ms'].max()
        min_velocity = laps_df['velocity_ms'].min()

        ax5.set_ylim(min_velocity*0.7, max_velocity*1.05) # Setting y-limit for Velocity from 0 to 1.5 times the max velocity

        # Function to convert m/s to min/km (pace) and format as MM:SS
        def ms_to_minkm_mmss(velocity_ms):
            if velocity_ms == 0:
                return 'inf'  # Or some other indicator for 0 velocity
            pace_minutes_decimal = (1000 / velocity_ms) / 60
            minutes = int(pace_minutes_decimal)
            seconds = int((pace_minutes_decimal - minutes) * 60)
            return f'{minutes:02d}:{seconds:02d}'

        # Apply the conversion and formatting to the y-axis tick labels for Velocity
        velocity_ticks = ax5.get_yticks()
        ax5.set_yticks(velocity_ticks) # Set the tick locations
        ax5.set_yticklabels([ms_to_minkm_mmss(y) if ms_to_minkm_mmss(y) != 'inf' else 'inf' for y in velocity_ticks])
        
        plt.tight_layout()
        
        # Determine save path - always save the chart
        if save_path:
            chart_path = save_path
        else:
            # Get the uploads directory path
            current_dir = os.path.dirname(os.path.abspath(__file__))
            app_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            uploads_dir = os.path.join(app_dir, "app", "uploads")
            
            # Create uploads directory if it doesn't exist
            os.makedirs(uploads_dir, exist_ok=True)
            
            # Generate default filename
            chart_path = os.path.join(uploads_dir, f"running_chart_activity_{activity_id}_1.png")
        
        # Save the chart
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        print(f"Chart saved to: {chart_path}")

        print(f"Successfully created running chart for activity {activity_id}")
        return {
            "status": "success",
            "message": f"Successfully created running chart for activity {activity_id}"
        }
        
    except Exception as e:
        print(f"Error creating running chart: {str(e)}")
        return {
            "status": "error",
            "message": f"Error creating running chart: {str(e)}",
            "chart_path": None,
            "activity_info": None
        }