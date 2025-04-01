import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.text import TextPath
from matplotlib.transforms import Affine2D
import matplotlib.image as mpimg
import os
import matplotlib.colors as mcolors

def get_text_width(text, font_size, scale_factor=0.001):
    """Estimate the width of text for matplotlib plotting."""
    text_path = TextPath((0, 0), text, size=font_size)
    bounds = text_path.get_extents(Affine2D())
    return bounds.width * scale_factor

def draw_progress_bar(ax, step, num_graphics, riding):
    """Draw a progress bar showing the current step's progress."""
    progress_bar_x = 0.05
    progress_bar_y = 0.86
    progress_bar_width = 0.9
    progress_bar_height = 0.02
    progress = (step / (num_graphics - 1)) * 100

    # Draw background
    bar_background = plt.Rectangle((progress_bar_x, progress_bar_y), progress_bar_width, progress_bar_height,
                                 color='lightgray', ec='black', alpha=0.8)
    ax.add_patch(bar_background)

    # Draw progress
    progress_bar = plt.Rectangle((progress_bar_x, progress_bar_y), (progress / 100) * progress_bar_width,
                               progress_bar_height, color='blue', ec='black', alpha=0.8)
    ax.add_patch(progress_bar)

    # Add text
    ax.text(progress_bar_x + progress_bar_width / 2, progress_bar_y + progress_bar_height / 2,
            f'{progress:.1f}%', fontsize=12, ha='center', va='center', weight='bold')
    ax.text(0.5, progress_bar_y + progress_bar_height + 0.01, f'{riding["name"]}',
            fontsize=36, ha='center', va='bottom', weight='bold')

def add_party_box(ax, x_pos, picture_y_pos, picture_height, width, sorted_short_parties, j, sorted_Colours):
    """
    Draws a box in the middle of the picture's height and adds centered text inside it.

    Parameters:
    ax (matplotlib axis): The axis on which to draw the box and text.
    x_pos (float): The x-coordinate for positioning the box.
    picture_y_pos (float): The y-coordinate of the bottom of the picture.
    picture_height (float): The height of the picture.
    width (float): The total width of the main box.
    sorted_short_parties (list): The list containing short party names.
    j (int): The index for selecting the party name from the sorted_short_parties list.
    sorted_Colours (list): List of colors for each party.
    """
    print(f"DEBUG: Adding party box for {sorted_short_parties[j]} at position ({x_pos}, {picture_y_pos})")
    print(f"DEBUG: Box dimensions - width: {width}, height: {picture_height}")
    print(f"DEBUG: Using color: {sorted_Colours[j]}")

    # Calculate the middle of the picture's height
    picture_middle_y = picture_y_pos - 0.05 + (picture_height / 2)
    print(f"DEBUG: Picture middle Y: {picture_middle_y}")

    # Define the height and position the new box such that its middle aligns with the picture's middle
    partybox_height = 0.05
    box_y_pos = picture_middle_y - (partybox_height / 2)  # Center the box on the picture's middle
    print(f"DEBUG: Box Y position: {box_y_pos}")

    # Define the width of the new box (from the middle of the box to just before the end)
    new_box_width = (x_pos + width / 2) - x_pos - 0.01  # tiny_margin to leave space before the end of the box
    print(f"DEBUG: Box width: {new_box_width}")

    try:
        # Draw the new box starting in the middle of the picture's height
        new_box = plt.Rectangle((x_pos + 0.005, box_y_pos), new_box_width, partybox_height,
                              color=sorted_Colours[j], alpha=0.5, ec='black')
        ax.add_patch(new_box)
        print(f"DEBUG: Box added successfully at ({x_pos + 0.005}, {box_y_pos})")

        # Add text to the new box, centering it
        text_x_pos = x_pos + new_box_width / 2  # Center the text horizontally in the box
        text_y_pos = box_y_pos + partybox_height / 2  # Center the text vertically in the box
        print(f"DEBUG: Text position: ({text_x_pos}, {text_y_pos})")

        ax.text(text_x_pos + 0.005, text_y_pos, f'{sorted_short_parties[j]}',
                fontsize=18, ha='center', va='center', color='black')
        print(f"DEBUG: Text added successfully: {sorted_short_parties[j]}")

    except Exception as e:
        print(f"ERROR in add_party_box: {str(e)}")
        raise

def draw_candidate_box(ax, x_pos, y_pos, width, height, color, alpha=0.25):
    """Draw a candidate's information box."""
    rect = plt.Rectangle((x_pos - width / 2, y_pos), width, height,
                        color=color, alpha=alpha, ec='black')
    ax.add_patch(rect)
    return rect

def add_candidate_photo(ax, candidate_name, x_pos, picture_y_pos, width, picture_height):
    """Add a candidate's photo to the visualization."""
    candidate_image_path = f'facesteals/{candidate_name}.jpg'
    if not os.path.exists(candidate_image_path):
        candidate_image_path = 'Required_Images/nopic.jpg'
    
    image = plt.imread(candidate_image_path)
    ax.imshow(image, extent=(x_pos - width / 2 + 0.005, x_pos,
                           picture_y_pos - 0.05, picture_y_pos - 0.05 + picture_height),
              aspect='auto', alpha=1, zorder=1)

def add_candidate_name(ax, x_pos, name_y_pos, candidate_name):
    """Add a candidate's name below their photo."""
    name_parts = candidate_name.split()
    if len(name_parts) > 1:
        first_line = ' '.join(name_parts[:len(name_parts)//2])
        second_line = ' '.join(name_parts[len(name_parts)//2:])
        ax.text(x_pos, name_y_pos, first_line,
               fontsize=14, ha='center', va='top',
               color='black', weight='bold')
        ax.text(x_pos, name_y_pos - 0.02, second_line,
               fontsize=14, ha='center', va='top',
               color='black', weight='bold')
    else:
        ax.text(x_pos, name_y_pos, candidate_name,
               fontsize=14, ha='center', va='top',
               color='black', weight='bold')

def add_vote_information(ax, x_pos, y_center, width, votes, percentage, lead_margin=None, name_font_size=22, party_color='blue'):
    """Add vote count and percentage information for a candidate."""
    # Add vote count in center
    text = f'{int(votes)}'
    text_x_center = x_pos
    ax.text(text_x_center, y_center, text,
            fontsize=name_font_size, ha='center', va='center',
            color='black')

    # Add lead margin if applicable
    if lead_margin and lead_margin > 0:
        leadtext = f'+{int(lead_margin)}'
        ax.text(text_x_center, y_center - 0.07, leadtext,
                fontsize=14, ha='center', va='center',
                color='black')

    # Draw percentage bar in bottom left corner
    bar_height = 0.03
    bar_width = width * 0.3  # 30% of the box width
    bar_x = x_pos - width/2 + width*0.1  # 10% margin from left edge
    bar_y = y_center - 0.1  # Position below the center
    
    # Background bar (100%)
    bg_bar = plt.Rectangle((bar_x, bar_y), bar_width, bar_height,
                          color='darkgray', alpha=0.3, ec='black')
    ax.add_patch(bg_bar)
    
    # Percentage bar - use a darker version of the party color
    if percentage > 0:
        fill_width = (percentage/100) * bar_width
        # Convert party color to RGB and darken it
        rgb = mcolors.to_rgb(party_color)
        darker_color = [max(0, c * 0.7) for c in rgb]  # Make color 30% darker
        fill_bar = plt.Rectangle((bar_x, bar_y), fill_width, bar_height,
                               color=darker_color, alpha=0.7, ec='black')
        ax.add_patch(fill_bar)

    # Add percentage text next to bar
    text_x_left = bar_x + bar_width + 0.02
    ax.text(text_x_left, bar_y + bar_height/2, f'{percentage:.1f}%',
            fontsize=14, ha='left', va='center',
            color='black')

def create_line_graph(riding_name, selected_steps, vote_totals, candidate_names, party_colors, winner_step=None):
    """Create a line graph showing vote progression."""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_title(f'Vote Progression in {riding_name}')
    ax.set_xlabel('Steps')
    ax.set_ylabel('Votes')

    x_points = selected_steps
    for idx, candidate_name in enumerate(candidate_names):
        y_points = [vote_totals[step][idx] for step in selected_steps]
        ax.plot(x_points, y_points, label=candidate_name,
                color=party_colors[idx], marker='o')

    if winner_step is not None and winner_step in selected_steps:
        ax.axvline(x=winner_step, color='red', linestyle='--', label='Winner Determined')

    ax.legend(loc='upper left')
    plt.grid(True)
    return fig 