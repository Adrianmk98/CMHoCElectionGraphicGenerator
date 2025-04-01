"""
Election Graphics Machine - Main module for generating election visualizations
This module handles the creation of election graphics, including vote progression,
candidate displays, and riding-specific visualizations.
"""

import math
import matplotlib.pyplot as plt
import numpy as np
import os
import random
import matplotlib.image as mpimg
import logging
from data.vote_calculations import calculate_vote_totals, determine_winner, calculate_lead_margin, update_running_tally, \
    finalize_riding_votes
from data.party_utils import get_leading_party
from data.MapMaker import mapmaker_main
from data.listMaker import listcreation
from matplotlib.text import TextPath
from matplotlib.transforms import Affine2D
import matplotlib.patches as patches
from data.graphics_utils import (get_text_width, draw_progress_bar, add_party_box, draw_candidate_box,
                                 add_candidate_photo, add_candidate_name, add_vote_information, create_line_graph)
from data.step_utils import (calculate_selected_steps, store_party_state, restore_party_state,
                             initialize_riding_data, get_valid_candidates)

# Debug logging configuration
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='election_graphics.log'
)


def MMP_calculation(all_parties, seatsToProcess, seatsprocessed):
    """
    Perform the MMP seat allocation calculation for parties excluding 'Independent'.

    Args:
        all_parties (list): List of party dictionaries with vote and seat information
        seatsToProcess (int): Total number of seats available for allocation
        seatsprocessed (int): Number of seats already processed

    Returns:
        dict: Final seat allocation for each party

    Debug Info:
        - Logs initial party votes and seat counts
        - Tracks each round of seat allocation
        - Reports final allocations and any anomalies
    """
    logging.debug(f"Starting MMP calculation - Seats to process: {seatsToProcess}, Processed: {seatsprocessed}")

    try:
        # Calculate total votes excluding Independent
        noindytotal_temp_vote = sum(party['temp_vote'] for party in all_parties if party['name'] != 'Independent')
        logging.debug(f"Total votes excluding Independent: {noindytotal_temp_vote}")

        # Initialize seat allocations and store initial vote totals
        seats_allocated = {party['name']: 0 for party in all_parties if party['name'] != 'Independent'}
        original_party_votes = {party['name']: party['temp_vote'] for party in all_parties if party['name'] != 'Independent'}
        party_votes = original_party_votes.copy()

        logging.debug("Initial vote totals:")
        for party, votes in original_party_votes.items():
            logging.debug(f"  {party}: {votes}")

        total_seats_to_allocate = seatsToProcess
        logging.debug(f"Total seats to allocate: {total_seats_to_allocate}")

        # Get the seat count for Independent parties
        independent_seats = sum(party['seats'] for party in all_parties if party['name'] == 'Independent')
        logging.debug(f"Independent seats: {independent_seats}")

        fptp_seats = {party['name']: party['seats'] for party in all_parties}
        logging.debug("FPTP seats by party:")
        for party, seats in fptp_seats.items():
            logging.debug(f"  {party}: {seats}")

        # Loop for the remaining rounds
        remaining_seats = total_seats_to_allocate - independent_seats
        logging.debug(f"Beginning allocation of {remaining_seats} remaining seats")

        for round in range(remaining_seats):
            # Determine the leading party based on remaining votes
            leading_party = max(party_votes, key=party_votes.get)
            old_votes = party_votes[leading_party]

            # Allocate a seat to the leading party
            seats_allocated[leading_party] += 1
            seats_won = seats_allocated[leading_party]

            # Reset the party_votes
            party_votes[leading_party] = original_party_votes[leading_party] / (seats_won + 1)

            logging.debug(f"Round {round + 1}:")
            logging.debug(f"  Leading party: {leading_party}")
            logging.debug(f"  Votes before: {old_votes:.2f}")
            logging.debug(f"  Votes after: {party_votes[leading_party]:.2f}")
            logging.debug(f"  Seats won: {seats_won}")

        # Calculate final allocations
        logging.debug("\nFinal seat allocation before FPTP adjustment:")
        for party, seats in seats_allocated.items():
            logging.debug(f"  {party}: {seats}")

        # Adjust for FPTP seats
        final_seat_allocation = {party: seats_allocated[party] - fptp_seats.get(party, 0) for party in seats_allocated}

        logging.debug("\nFinal seat allocation after FPTP adjustment:")
        for party, seats in final_seat_allocation.items():
            logging.debug(f"  {party}: {seats}")

        return final_seat_allocation

    except Exception as e:
        logging.error(f"Error in MMP calculation: {str(e)}", exc_info=True)
        raise


# Example usage
# seats_allocated = MMP_calculation(all_parties, seatsToProcess, seatsprocessed)


def get_text_width(text, font_size, scale_factor=0.001):
    """
    Calculate the width of text for proper positioning in graphics.

    Args:
        text (str): The text to measure
        font_size (int): Font size in points
        scale_factor (float): Scale factor for width calculation

    Returns:
        float: Scaled width of the text
    """
    logging.debug(f"Calculating width for text: '{text}' with font size {font_size}")
    text_path = TextPath((0, 0), text, size=font_size)
    bounds = text_path.get_extents(Affine2D())
    width = bounds.width * scale_factor
    logging.debug(f"Calculated width: {width}")
    return width


def draw_progress_bar(ax, step, num_graphics, riding):
    """
    Draw a progress bar showing the current step in the graphics generation.

    Args:
        ax (matplotlib.axes.Axes): The axes to draw on
        step (int): Current step number
        num_graphics (int): Total number of graphics
        riding (dict): Riding information
    """
    logging.debug(f"Drawing progress bar for step {step}/{num_graphics - 1} in {riding['name']}")

    # Define progress bar properties
    progress_bar_x = 0.05
    progress_bar_y = 0.86
    progress_bar_width = 0.9
    progress_bar_height = 0.02

    # Calculate progress
    progress = (step / (num_graphics - 1)) * 100
    logging.debug(f"Progress: {progress:.1f}%")

    try:
        # Draw background
        bar_background = plt.Rectangle((progress_bar_x, progress_bar_y), progress_bar_width, progress_bar_height,
                                     color='lightgray', ec='black', alpha=0.8)
        ax.add_patch(bar_background)

        # Draw progress bar
        progress_bar = plt.Rectangle((progress_bar_x, progress_bar_y), (progress / 100) * progress_bar_width,
                                   progress_bar_height, color='blue', ec='black', alpha=0.8)
        ax.add_patch(progress_bar)

        # Add text
        ax.text(progress_bar_x + progress_bar_width / 2, progress_bar_y + progress_bar_height / 2,
                f'{progress:.1f}%', fontsize=12, ha='center', va='center', weight='bold')
        ax.text(0.5, progress_bar_y + progress_bar_height + 0.01, f'{riding["name"]}',
                fontsize=36, ha='center', va='bottom', weight='bold')

        logging.debug("Progress bar drawn successfully")
    except Exception as e:
        logging.error(f"Error drawing progress bar: {str(e)}", exc_info=True)
        raise


def add_party_box(ax, x_pos, picture_y_pos, picture_height, width, sorted_short_parties, j, sorted_Colours):
    """
    Draw a party identification box with the party's short name.

    Args:
        ax (matplotlib.axes.Axes): The axes to draw on
        x_pos (float): X-coordinate for the box
        picture_y_pos (float): Y-coordinate of the picture
        picture_height (float): Height of the picture
        width (float): Width of the box
        sorted_short_parties (list): List of party short names
        j (int): Index of the current party
        sorted_Colours (list): List of party colors
    """
    logging.debug(f"Adding party box for {sorted_short_parties[j]} at position ({x_pos}, {picture_y_pos})")

    try:
        # Calculate positions
        picture_middle_y = picture_y_pos - 0.05 + (picture_height / 2)
        partybox_height = 0.05
        box_y_pos = picture_middle_y - (partybox_height / 2)
        new_box_width = (x_pos + width / 2) - x_pos - 0.01

        # Draw box
        new_box = plt.Rectangle((x_pos + 0.005, box_y_pos), new_box_width, partybox_height,
                              color=sorted_Colours[j], alpha=0.5, ec='black')
        ax.add_patch(new_box)

        # Add text
        text_x_pos = x_pos + new_box_width / 2
        text_y_pos = box_y_pos + partybox_height / 2
        ax.text(text_x_pos + 0.005, text_y_pos, f'{sorted_short_parties[j]}',
                fontsize=18, ha='center', va='center', color='black')

        logging.debug(f"Party box added successfully for {sorted_short_parties[j]}")
    except Exception as e:
        logging.error(f"Error adding party box for {sorted_short_parties[j]}: {str(e)}", exc_info=True)
        raise


def generate_single_riding(riding, all_parties, num_graphics, num_selected_steps, seatsToProcess, byelection, r,
                         vote_totals_by_riding, winning_candidate_indices, winner_determined_steps, party_colors,
                         party_seat_counts, party_listseat_counts, party_total_seats, seatsprocessed,
                         current_total_votes, pre_riding_votes):
    """
    Generate graphics for a single riding, including vote progression and candidate displays.

    Args:
        riding (dict): Riding information including name, results, and candidates
        all_parties (list): List of all party information
        num_graphics (int): Total number of graphics to generate
        num_selected_steps (int): Number of steps to visualize
        ... (other parameters)
        current_total_votes (dict): Current running total of votes for each party
        pre_riding_votes (dict): Vote totals before this riding started
    """
    logging.debug(f"=== Starting generation for riding: {riding['name']} ===")
    logging.debug(f"Parameters: num_graphics={num_graphics}, num_selected_steps={num_selected_steps}")

    try:
        # Initialize vote calculations
        seats_allocated = {party['name']: 0 for party in all_parties}
        num_parties = len(riding['final_results'])
        logging.debug(f"Number of parties in riding: {num_parties}")

        # Update current vote totals for this riding
        current_votes = {party['name']: 0 for party in all_parties}
        for i, party_name in enumerate(riding['party_names']):
            current_votes[party_name] = riding['final_results'][i]
            
        # If this is the first riding, initialize accumulated_votes with current votes
        if r == 0:
            for party_name, votes in current_votes.items():
                party_total_seats[party_name] = votes
                # Also update the temp_vote in all_parties
                for party in all_parties:
                    if party['name'] == party_name:
                        party['temp_vote'] = votes

        # Calculate vote totals for all steps
        logging.debug("Calculating vote totals...")
        for j in range(num_parties):
            total_votes = riding['final_results'][j]
            vote_totals_by_riding[r][:, j] = calculate_vote_totals(total_votes, num_graphics)
            logging.debug(f"Party {j} vote progression calculated")

        vote_totals_by_riding[r][-1] = riding['final_results']  # Exact final totals
        vote_totals_by_riding[r][0] = np.zeros(num_parties)  # Start at zero

        # Get selected steps for visualization
        selected_steps = calculate_selected_steps(num_graphics, num_selected_steps)
        print(f"DEBUG: Selected steps for {riding['name']}: {selected_steps}")

        # Create output directory if needed
        output_dir = 'output_images'
        os.makedirs(output_dir, exist_ok=True)

        # Generate line graph
        final_step = selected_steps[-1]
        final_votes = vote_totals_by_riding[r][final_step]
        fig = create_line_graph(riding['name'], selected_steps, vote_totals_by_riding[r],
                              riding['candidate_names'], [party_colors[party] for party in riding['party_names']],
                              winner_determined_steps[r])

        line_graph_filename = f'line_graph_riding_{r + 1:02}_{riding["name"].replace(" ", "_")}.png'
        fig.savefig(os.path.join(output_dir, line_graph_filename))
        plt.close(fig)

        # Generate step images
        for step in selected_steps:
            try:
                # Calculate current state
                total_votes = np.sum(vote_totals_by_riding[r][step])
                remaining_votes = np.sum(riding['final_results']) - total_votes
                is_winner_determined = determine_winner(vote_totals_by_riding[r][step], remaining_votes)

                # Update winner if determined
                if is_winner_determined and winning_candidate_indices[r] == -1:
                    winning_candidate_indices[r] = np.argmax(vote_totals_by_riding[r][step])
                winner_determined_steps[r] = step

                # Create figure
                fig, ax = plt.subplots(figsize=(12, 8))
                plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

                # Set up background
                background_img = plt.imread('Required_Images/background.jpg')
                ax.imshow(background_img, aspect='auto', extent=[0, 1, 0, 1], alpha=0.2)
                ax.axis('off')
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)

                # Sort candidates by votes
                sorted_indices = np.argsort(-vote_totals_by_riding[r][step])
                sorted_votes = vote_totals_by_riding[r][step][sorted_indices]
                sorted_names = np.array(riding['candidate_names'])[sorted_indices]
                sorted_parties = np.array(riding['party_names'])[sorted_indices]
                sorted_short_parties = np.array(riding['short_name'])[sorted_indices]
                sorted_colors = np.array([party_colors[party] for party in sorted_parties])

                # Layout calculations
                total_votes_step = sorted_votes.sum()
                width = 0.8 / 4
                padding = 0.1 / 4
                picture_height = 0.2

                # Get valid candidates
                valid_candidates = get_valid_candidates(sorted_votes, sorted_parties)
                num_candidates_to_display = len(valid_candidates)

                # Calculate layout
                num_displayed_columns = min(num_candidates_to_display, 4)
                num_displayed_rows = (num_candidates_to_display - 1) // num_displayed_columns + 1
                total_width = num_displayed_columns * (width + padding) - padding
                total_height = num_displayed_rows * (0.35 + picture_height)
                start_x = (1 - total_width) / 2
                start_y = (1 - total_height) / 2

                # Draw candidates
                logging.debug(f"Starting to draw {len(valid_candidates)} candidates for step {step}")
                for j, (orig_idx, vote) in enumerate(valid_candidates):
                    col = j % num_displayed_columns
                    row = j // num_displayed_columns

                    # Calculate position for each candidate box
                    x_pos = start_x + col * (width + padding) + width / 2
                    y_pos = start_y + row * (0.45 + picture_height)  # Position adjusted for picture and info space
                    picture_y_pos = y_pos + 0.35  # Position it such that it starts at y_pos + 0.35 and ends before the information box
                    
                    # Draw candidate's information box
                    # Create the rectangle with a transparent fill
                    rect = plt.Rectangle((x_pos - width / 2, y_pos), width, 0.35 + picture_height,
                                      color=sorted_colors[orig_idx], alpha=0.25)  # Fill color with transparency
                    # Add the rectangle to the axis
                    ax.add_patch(rect)

                    # Calculate the x-coordinate for the vertical line (center of the rectangle)
                    center_x = x_pos  # The rectangle is centered at x_pos, so this is the midpoint

                    # Draw a vertical line through the center of the rectangle
                    ax.vlines(x=center_x, ymin=y_pos+0.05, ymax=y_pos + 0.18, color='black', linewidth=1.5)

                    # Set the edge color, linewidth, and edge alpha
                    edge_color = 'black'
                    edge_alpha = 0.7  # Set your desired alpha for the edge color
                    rect.set_edgecolor(edge_color)

                    # Create a new edge line with the specified alpha
                    edge_line = plt.Line2D([0], [0], color=edge_color, alpha=edge_alpha, linewidth=3)
                    ax.add_line(edge_line)

                    # Add photo
                    candidate_image_path = f'facesteals/{sorted_names[orig_idx]}.jpg'
                    if not os.path.exists(candidate_image_path):
                        candidate_image_path = 'Required_Images/nopic.jpg'

                    # Load and draw the image
                    image = plt.imread(candidate_image_path)
                    ax.imshow(image, extent=(x_pos - width / 2+0.005, x_pos,
                                          picture_y_pos - 0.05, picture_y_pos - 0.05 + picture_height),
                            aspect='auto', alpha=1, zorder=1)

                    # Calculate the middle of the picture's height
                    picture_middle_y = picture_y_pos - 0.05 + (picture_height / 2)

                    text_y_pos = y_pos + 0.15   # Center the text within the party color box
                    
                    # Calculate lead margin and percentage
                    lead_margin = calculate_lead_margin(sorted_votes, orig_idx, num_candidates_to_display)
                    percentage_of_all = (sorted_votes[orig_idx] / total_votes_step * 100) if total_votes_step > 0 else 0

                    # Calculate centers for positioning
                    y_center = y_pos + 0.25 / 2  # Centered vertically in the box
                    text = f'{int(sorted_votes[orig_idx])}'

                    # Define available width and adjust font size
                    available_width_right = width / 2 - 0.02  # Right half of the box
                    name_font_size = 22
                    while get_text_width(text, name_font_size) > available_width_right and name_font_size > 1:
                        name_font_size -= 1

                    # Add vote count text
                    text_x_center = x_pos + (width / 2) / 2  # Center in the right half
                    ax.text(text_x_center, y_center, text,
                          fontsize=name_font_size, ha='center', va='center',
                          color='black')

                    # Add lead margin if applicable
                    if lead_margin > 0:
                        leadtext = f'{int(lead_margin)} \nlead'
                        ax.text(text_x_center, y_center-0.07, leadtext,
                              fontsize=14, ha='center', va='center',
                              color='black')

                    # Add percentage text and progress bar
                    half_width = width / 2
                    text_x_left = x_pos - width / 2 + half_width / 2
                    ax.text(text_x_left, y_center, f'{percentage_of_all:.1f}%',
                          fontsize=22, ha='center', va='center',
                          color='black')

                    # Add progress bar
                    progress_bar_height = 0.02
                    progress_bar_y = y_pos
                    progress_bar_width = (percentage_of_all / 100) * half_width
                    progress_bar = plt.Rectangle((x_pos - width / 2, progress_bar_y), progress_bar_width,
                                              progress_bar_height, color=sorted_colors[orig_idx], alpha=0.8)
                    ax.add_patch(progress_bar)
                    progress_bar_outline = plt.Rectangle((x_pos - width / 2, progress_bar_y), half_width,
                                                      progress_bar_height, fill=False, edgecolor='black',
                                                      linewidth=1)
                    ax.add_patch(progress_bar_outline)

                    # Add candidate name
                    message_text = sorted_names[orig_idx]
                    message_text_x = x_pos
                    message_text_y = y_pos + 0.25 - 0.02

                    # Adjust font size for name
                    current_font_size = 22
                    minimum_font_size = 12
                    available_width = width - 0.04

                    current_text_width = get_text_width(message_text, current_font_size)
                    if current_text_width > available_width:
                        while current_text_width > available_width and current_font_size > minimum_font_size:
                            current_font_size -= 1
                            current_text_width = get_text_width(message_text, current_font_size)

                    ax.text(message_text_x, message_text_y, message_text,
                          fontsize=current_font_size, ha='center', va='top', color='black')

                    # Add party box
                    add_party_box(ax, x_pos, picture_y_pos, picture_height, width,
                                sorted_short_parties, orig_idx, sorted_Colours=sorted_colors)

                    # Draw checkmark for winner
                    if winning_candidate_indices[r] != -1:
                        winning_index = winning_candidate_indices[r]
                        sorted_winning_index = np.where(sorted_indices == winning_index)[0][0]
                        if sorted_winning_index < num_candidates_to_display:
                            x_pos_check = start_x + (sorted_winning_index % num_displayed_columns) * (width + padding) + width / 2
                            y_pos_check = start_y + (sorted_winning_index // num_displayed_columns) * (0.35 + picture_height)
                            ax.text(x_pos_check + width / 2 - 0.005, y_pos_check + 0.35, '✓',
                                  fontsize=72, ha='right', va='top', color='green')

                    logging.debug(f"Completed drawing candidate {sorted_names[orig_idx]}")

                logging.debug(f"Completed drawing all candidates for step {step}")

                # Initialize combined seat counts
                party_data = []
                for party in all_parties:
                    # Count both leading and elected seats
                    total_seats = party_seat_counts.get(party['name'], 0)
                    # For the first riding, use current step votes, otherwise use accumulated votes
                    if r == 0:
                        temp_vote = sum(vote_totals_by_riding[r][step][i] for i, p in enumerate(riding['party_names']) if p == party['name'])
                    else:
                        temp_vote = party_total_seats.get(party['name'], 0)
                    party_data.append((party['name'], total_seats, temp_vote))
                
                # Sort by total seats (descending) and then by temp_vote (descending) for ties
                sorted_party_data = sorted(party_data, key=lambda x: (-x[1], -x[2]))
                
                # Convert to dictionary format for compatibility with existing code
                sorted_combined_seat_counts = {party_name: seats for party_name, seats, _ in sorted_party_data}

                # Draw party seat counts
                seat_count_y_pos = y_pos - 0.35  # Positioning for the seat counts row
                seat_count_height = 0.3  # Height for the seat counts row
                padding = 0.03  # Reduced padding between party boxes
                num_parties = min(len(sorted_combined_seat_counts), 6)  # Limit to first 6 parties for display
                party_width = 0.6 / num_parties  # Adjust width to fit more compactly
                total_width = num_parties * party_width + (num_parties - 1) * padding  # Total width including padding
                start_x = (1 - total_width) / 2  # Center the seat count boxes horizontally

                # Draw party boxes and seat counts
                for i, (party_name, count) in enumerate(list(sorted_combined_seat_counts.items())[:6]):
                    party_x_pos = start_x + i * (party_width + padding) + party_width / 2
                    
                    # Get party info and short name
                    party_dict = next((party for party in all_parties if party['name'] == party_name), None)
                    short_pname = party_dict['short_pname'] if party_dict else party_name
                    party_color = party_colors.get(party_name, 'grey')
                    
                    # Draw party box
                    party_box = plt.Rectangle((party_x_pos - party_width / 2, seat_count_y_pos),
                                           party_width, seat_count_height,
                                           color=party_color,
                                           ec='black', alpha=0.25)
                    ax.add_patch(party_box)
                    
                    # Calculate current vote totals for this step
                    current_riding_votes = sum(vote_totals_by_riding[r][step][i] for i, p in enumerate(riding['party_names']) if p == party_name)
                    # Total votes is pre-riding votes plus current riding votes
                    temp_vote = pre_riding_votes[party_name] + current_riding_votes
                    
                    # Calculate total votes (sum of all pre-riding votes plus current riding votes)
                    total_pre_riding_votes = sum(pre_riding_votes.values())
                    total_current_votes = sum(vote_totals_by_riding[r][step])
                    total_temp_vote = total_pre_riding_votes + total_current_votes
                    
                    temp_vote = math.floor(temp_vote)
                    total_temp_vote = math.floor(total_temp_vote)
                    
                    # Calculate and format vote percentage
                    total_vote_percent = (temp_vote / total_temp_vote * 100) if total_temp_vote > 0 else 0
                    total_vote_percent_formatted = f'{total_vote_percent:.1f}%'
                    
                    # Set the position and text for the label
                    base_y = seat_count_y_pos + seat_count_height / 2 + 0.075
                    offset = 0.03

                    # Add party short name in a colored box at the top
                    ax.text(
                        party_x_pos,
                        base_y + offset + 0.02,
                        f'{short_pname}',
                        fontsize=16,
                        ha='center',
                        va='center',
                        color='black',
                        bbox=dict(facecolor=party_color, edgecolor='black',
                                boxstyle='round,pad=0.1', alpha=0.5)
                    )

                    # Add text for temp_vote
                    ax.text(party_x_pos, base_y,
                           f'{temp_vote}',
                           fontsize=12, ha='center', va='center', color='black')

                    vote_text_y = base_y - offset

                    # Add text for total_vote_percent_formatted
                    ax.text(
                        party_x_pos,
                        vote_text_y,
                        f'{total_vote_percent_formatted}',
                        fontsize=16,
                        ha='center',
                        va='center',
                        color='black'
                    )

                    # Add a horizontal line under total_vote_percent_formatted text
                    line_y = vote_text_y - 0.02
                    half_party_width = party_width / 2
                    ax.hlines(
                        y=line_y,
                        xmin=party_x_pos - half_party_width + 0.005,
                        xmax=party_x_pos + half_party_width - 0.005,
                        color='black',
                        linewidth=1
                    )
                    
                    # Calculate and draw seat counts
                    if party_name != 'Independent':
                        # Get current FPTP seats
                        fptp_seats = 0
                        # Count leading or elected seats for this party
                        for i, p in enumerate(riding['party_names']):
                            if p == party_name:
                                # Check if this party is leading in the current step
                                current_votes = vote_totals_by_riding[r][step]
                                if i == np.argmax(current_votes) and sum(current_votes) > 0:
                                    fptp_seats = party_seat_counts.get(party_name, 0) + 1
                                else:
                                    fptp_seats = party_seat_counts.get(party_name, 0)
                        
                        # Calculate MMP seats if we have votes
                        if total_temp_vote > 0:
                            # Update temp_vote for MMP calculation
                            for party in all_parties:
                                if party['name'] == party_name:
                                    party['temp_vote'] = temp_vote
                                elif party['name'] not in pre_riding_votes:
                                    party['temp_vote'] = 0
                                else:
                                    current_riding_votes = sum(vote_totals_by_riding[r][step][i] for i, p in enumerate(riding['party_names']) if p == party['name'])
                                    party['temp_vote'] = pre_riding_votes[party['name']] + current_riding_votes
                            
                            seats_allocated = MMP_calculation(all_parties, seatsToProcess, seatsprocessed)
                            mmp_seats = seats_allocated.get(party_name, 0)
                            total_seats = fptp_seats + mmp_seats
                        else:
                            total_seats = fptp_seats
                    else:
                        # For Independent, just show FPTP seats
                        fptp_seats = 0
                        for i, p in enumerate(riding['party_names']):
                            if p == party_name:
                                current_votes = vote_totals_by_riding[r][step]
                                if i == np.argmax(current_votes) and sum(current_votes) > 0:
                                    fptp_seats = party_seat_counts.get(party_name, 0) + 1
                                else:
                                    fptp_seats = party_seat_counts.get(party_name, 0)
                        total_seats = fptp_seats

                    # Draw the seat count
                    ax.text(party_x_pos, line_y - 0.02,
                           f'{int(total_seats)}',
                           fontsize=20, ha='center', va='center', color='black')

                # Add progress bar
                draw_progress_bar(ax, step, num_graphics, riding)

                # Save the image
                filename = f'{riding["name"].replace(" ", "_")}_step_{step + 1:02}.png'
                plt.savefig(os.path.join(output_dir, filename), bbox_inches='tight')
                plt.close()

                # Update running tally and calculate seats
                votes_by_riding = vote_totals_by_riding[r][step]
                parties_by_riding = np.array(riding['party_names'])
                update_running_tally(votes_by_riding, parties_by_riding, all_parties)

                if not byelection and np.any(votes_by_riding > 0):
                    seats_allocated = MMP_calculation(all_parties, seatsToProcess, seatsprocessed)

            except Exception as e:
                print(f"ERROR processing step {step} for riding {riding['name']}: {e}")
                import traceback
                traceback.print_exc()

        # Process final votes
        finalize_riding_votes(final_votes, riding['party_names'], all_parties)
        seatsprocessed += 1

        # Generate map
        try:
            riding_name = riding['name']
            mapmaker_main(f'irlriding/{riding_name}.txt',
                        f'svg/{riding_name}.svg',
                        output_dir,
                        riding['short_name'],
                        [float(vote) for vote in riding['final_results']],
                        riding_name)
        except Exception as e:
            print(f"DEBUG ERROR: Error in mapmaker_main: {e}")

        try:
            listcreation()
        except Exception as e:
            print(f"DEBUG ERROR: Error in listcreation: {e}")

        return

    except Exception as e:
        logging.error(f"Error in generate_single_riding: {str(e)}", exc_info=True)
        raise


def generate_individual_graphics(ridings, all_parties, num_graphics, num_selected_steps, seatsToProcess, byelection,
                               callback=None):
    """
    Generate graphics for all ridings with reroll option.

    Args:
        ridings (list): List of riding information
        all_parties (list): List of all party information
        num_graphics (int): Total number of graphics to generate
        num_selected_steps (int): Number of steps to visualize
        seatsToProcess (int): Total seats to process
        byelection (bool): Whether this is a byelection
        callback (function, optional): Callback function for progress updates

    Debug Info:
        - Tracks overall progress
        - Monitors state management
        - Reports riding-specific issues
    """
    logging.debug("=== Starting individual graphics generation ===")
    logging.debug(f"Total ridings: {len(ridings)}, Graphics: {num_graphics}, Selected steps: {num_selected_steps}")

    try:
        num_ridings = len(ridings)
        max_parties = max(len(riding['final_results']) for riding in ridings)
        logging.debug(f"Maximum parties in any riding: {max_parties}")

        # Initialize arrays and validate ridings
        logging.debug("Initializing data structures...")
        for riding in ridings:
            initialize_riding_data(riding, max_parties)
            logging.debug(f"Initialized riding: {riding['name']}")

        # Initialize arrays
        vote_totals_by_riding = np.zeros((num_ridings, num_graphics, max_parties))
        winning_candidate_indices = np.full(num_ridings, -1)
        winner_determined_steps = np.full(num_ridings, None)
        logging.debug("Arrays initialized successfully")

        # Initialize party data
        party_colors = {party['name']: party['color'] for party in all_parties}
        party_colors["Empty"] = "gray"
        party_seat_counts = {party['name']: 0 for party in all_parties}
        party_listseat_counts = {party['name']: 0 for party in all_parties}
        party_total_seats = {party['name']: 0 for party in all_parties}
        
        # Initialize vote tracking
        starting_votes = {party['name']: party.get('starting_votes', 0) for party in all_parties}
        current_total_votes = starting_votes.copy()  # Running total of votes including current riding
        pre_riding_votes = starting_votes.copy()  # Vote totals before current riding
        seatsprocessed = 0

        # Store initial state
        last_accepted_state = store_party_state(all_parties)

        # Process each riding
        for r, riding in enumerate(ridings):
            logging.debug(f"\nProcessing riding {r + 1}/{num_ridings}: {riding['name']}")
            while True:
                try:
                    current_state = store_party_state(all_parties)
                    # Store vote totals before processing this riding
                    pre_riding_votes = current_total_votes.copy()

                    # Update status if callback exists
                    if callback and hasattr(callback, '__self__') and hasattr(callback.__self__, 'status_label'):
                        status_text = f"Generating {riding['name']} ({r + 1}/{num_ridings})..."
                        callback.__self__.status_label.config(text=status_text)
                        callback.__self__.root.update()

                    # Generate graphics
                    generate_single_riding(riding, all_parties, num_graphics, num_selected_steps, seatsToProcess,
                                        byelection, r, vote_totals_by_riding, winning_candidate_indices,
                                        winner_determined_steps, party_colors, party_seat_counts,
                                        party_listseat_counts, party_total_seats, seatsprocessed,
                                        current_total_votes, pre_riding_votes)

                    # Handle callback
                    if callback:
                        if hasattr(callback, '__self__') and hasattr(callback.__self__, 'status_label'):
                            status_text = f"Reviewing {riding['name']} ({r + 1}/{num_ridings})..."
                            callback.__self__.status_label.config(text=status_text)
                            callback.__self__.root.update()

                        reroll = callback(riding, r, num_ridings)
                        if not reroll:
                            last_accepted_state = store_party_state(all_parties)
                            # Update current total votes with final results from this riding
                            for party_name in current_total_votes:
                                current_riding_votes = sum(vote_totals_by_riding[r][-1][i] for i, p in enumerate(riding['party_names']) if p == party_name)
                                current_total_votes[party_name] = pre_riding_votes[party_name] + current_riding_votes
                            break
                        else:
                            logging.debug(f"Rerolling riding {riding['name']}")
                            vote_totals_by_riding[r] = np.zeros((num_graphics, max_parties))
                            winning_candidate_indices[r] = -1
                            winner_determined_steps[r] = None
                            restore_party_state(all_parties, last_accepted_state)
                            # Reset vote totals to pre-riding state
                            current_total_votes = pre_riding_votes.copy()
                    else:
                        last_accepted_state = store_party_state(all_parties)
                        # Update current total votes
                        for party_name in current_total_votes:
                            current_riding_votes = sum(vote_totals_by_riding[r][-1][i] for i, p in enumerate(riding['party_names']) if p == party_name)
                            current_total_votes[party_name] = pre_riding_votes[party_name] + current_riding_votes
                        break

                except Exception as e:
                    logging.error(f"Error processing riding {riding['name']}: {str(e)}", exc_info=True)
                    restore_party_state(all_parties, last_accepted_state)
                    # Reset vote totals to pre-riding state
                    current_total_votes = pre_riding_votes.copy()
                    if callback:
                        from tkinter import messagebox
                        if messagebox.askyesno("Error",
                                             f"An error occurred processing riding {riding['name']}:\n{str(e)}\n\nSkip this riding?"):
                            logging.warning(f"Skipping riding {riding['name']} due to error")
                            break
                    else:
                        break

        logging.debug("=== Completed all ridings successfully ===")
        return True

    except Exception as e:
        logging.error(f"Critical error in generate_individual_graphics: {str(e)}", exc_info=True)
        raise



