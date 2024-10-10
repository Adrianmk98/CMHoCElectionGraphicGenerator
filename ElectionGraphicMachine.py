import math
import matplotlib.pyplot as plt
import numpy as np
import os
import random
import matplotlib.image as mpimg
from data.vote_calculations import calculate_vote_totals, determine_winner, calculate_lead_margin,update_running_tally,finalize_riding_votes
from data.party_utils import get_leading_party
from data.MapMaker import mapmaker_main
from data.listMaker import listcreation
from matplotlib.text import TextPath
from matplotlib.transforms import Affine2D
import matplotlib.patches as patches


def MMP_calculation(all_parties, seatsToProcess, seatsprocessed):
    """
    Perform the MMP seat allocation calculation for parties excluding 'Independent'.

    Args:
    all_parties (list): A list of dictionaries representing all parties with keys like 'name', 'temp_vote', etc.
    seatsToProcess (int): Total number of seats available for allocation.
    seatsprocessed (int): Number of seats that have already been processed.

    Returns:
    dict: A dictionary with the number of seats allocated to each party.
    """

    # Calculate total votes excluding Independent
    noindytotal_temp_vote = sum(party['temp_vote'] for party in all_parties if party['name'] != 'Independent')

    # Initialize seat allocations and store initial vote totals
    seats_allocated = {party['name']: 0 for party in all_parties if party['name'] != 'Independent'}
    original_party_votes = {party['name']: party['temp_vote'] for party in all_parties if party['name'] != 'Independent'}
    party_votes = original_party_votes.copy()  # Copy the original votes for modification

    total_seats_to_allocate = seatsToProcess

    # Get the seat count for Independent parties
    independent_seats = sum(party['seats'] for party in all_parties if party['name'] == 'Independent')
    print(f"Independent seats: {independent_seats}")
    fptp_seats = {party['name']: party['seats'] for party in all_parties}
    print(f"party fptp seats: {fptp_seats}")

    # Loop for the remaining rounds (excluding already processed independent seats)
    for round in range(total_seats_to_allocate - independent_seats):
        # Determine the leading party based on remaining votes
        leading_party = max(party_votes, key=party_votes.get)

        # Allocate a seat to the leading party
        seats_allocated[leading_party] += 1

        # Calculate the current seats won by the leading party
        seats_won = seats_allocated[leading_party]

        # Reset the party_votes to the original value divided by the number of seats won
        party_votes[leading_party] = original_party_votes[leading_party] / (seats_won + 1)  # +1 to avoid division by zero

        # Optional: Print round info (for debugging)
        print(f"Round {round + 1}: {leading_party} gets a seat. Remaining votes: {party_votes}")

    # Final seat allocation
    print(f"Final seat allocation: {seats_allocated}")
    # Final seat allocation after removing FPTP seats
    final_seat_allocation = {party: seats_allocated[party] - fptp_seats.get(party, 0) for party in seats_allocated}

    print(f"Final seat allocation (excluding FPTP seats): {final_seat_allocation}")

    return final_seat_allocation

# Example usage
# seats_allocated = MMP_calculation(all_parties, seatsToProcess, seatsprocessed)


def get_text_width(text, font_size, scale_factor=0.001):
    # Estimate the width of the text using TextPath and scale it
    text_path = TextPath((0, 0), text, size=font_size)
    bounds = text_path.get_extents(Affine2D())
    return bounds.width * scale_factor  # Scale the width to match plot dimensions

def draw_progress_bar(ax, step, num_graphics,riding):
    """
    Draws a progress bar on the given axis.

    Parameters:
    ax (matplotlib axis): The axis on which to draw the progress bar.
    step (int): The current step in the progress.
    num_graphics (int): The total number of graphics to determine progress.
    """

    # Define progress bar properties
    progress_bar_x = 0.05
    progress_bar_y = 0.86
    progress_bar_width = 0.9
    progress_bar_height = 0.02

    # Calculate the progress percentage
    progress = (step / (num_graphics - 1)) * 100

    # Draw the background of the progress bar
    bar_background = plt.Rectangle((progress_bar_x, progress_bar_y), progress_bar_width, progress_bar_height,
                                   color='lightgray', ec='black', alpha=0.8)
    ax.add_patch(bar_background)

    # Draw the progress bar
    progress_bar = plt.Rectangle((progress_bar_x, progress_bar_y), (progress / 100) * progress_bar_width,
                                 progress_bar_height, color='blue', ec='black', alpha=0.8)
    ax.add_patch(progress_bar)

    # Add text showing the progress percentage
    ax.text(progress_bar_x + progress_bar_width / 2, progress_bar_y + progress_bar_height / 2,
            f'{progress:.1f}%', fontsize=12, ha='center', va='center', weight='bold')
    # Add the riding name as a title above the progress bar
    ax.text(0.5, progress_bar_y + progress_bar_height + 0.01, f'{riding["name"]}',
            fontsize=36, ha='center', va='bottom', weight='bold')


def add_party_box(ax, x_pos, picture_y_pos, picture_height, width, sorted_short_parties, j,sorted_Colours):
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
    """

    # Calculate the middle of the picture's height
    picture_middle_y = picture_y_pos - 0.05 + (picture_height / 2)

    # Define the height and position the new box such that its middle aligns with the picture's middle
    partybox_height = 0.05
    box_y_pos = picture_middle_y - (partybox_height / 2)  # Center the box on the picture's middle

    # Define the width of the new box (from the middle of the box to just before the end)
    new_box_width = (x_pos + width / 2) - x_pos - 0.01  # tiny_margin to leave space before the end of the box

    # Draw the new box starting in the middle of the picture's height
    new_box = plt.Rectangle((x_pos + 0.005, box_y_pos), new_box_width, partybox_height,
                            color=sorted_Colours[j], alpha=0.5, ec='black')
    ax.add_patch(new_box)

    # Add text to the new box, centering it
    text_x_pos = x_pos + new_box_width / 2  # Center the text horizontally in the box
    text_y_pos = box_y_pos + partybox_height / 2  # Center the text vertically in the box

    ax.text(text_x_pos + 0.005, text_y_pos, f'{sorted_short_parties[j]}',
            fontsize=18, ha='center', va='center', color='black')


def generate_individual_graphics(ridings, all_parties, num_graphics, num_selected_steps,seatsToProcess,byelection):
    # Sort ridings alphabetically by name

    global seats_allocated
    sorted_ridings = ridings  # Keep the original order from the spreadsheet
    winning_candidate_indices = [-1] * len(sorted_ridings)  # -1 indicates no winner yet
    winner_determined_steps = [None] * len(sorted_ridings)  # Initialize with None for each riding
    # Initialize party colors
    party_colors = {party['name']: party['color'] for party in all_parties}
    party_seat_counts = {party['name']: party['seats'] for party in all_parties}
    party_listseat_counts = {party['name']: party['seats_list'] for party in all_parties}
    party_total_seats = {party['name']: party['seats'] + party['seats_list'] for party in all_parties}
    # Initialize vote totals matrix for each riding
    vote_totals_by_riding = [np.zeros((num_graphics, len(riding['final_results']))) for riding in sorted_ridings]
    # Generate random vote totals for each candidate in each riding
    seatsprocessed = 0

    for r, riding in enumerate(sorted_ridings):

        num_parties = len(riding['final_results'])
        for j in range(num_parties):
            total_votes = riding['final_results'][j]
            vote_totals_by_riding[r][:, j] = calculate_vote_totals(total_votes, num_graphics)

        # Ensure final step has exact totals
        vote_totals_by_riding[r][-1] = riding['final_results']

        # Include step 0 where everyone has 0 votes
        vote_totals_by_riding[r][0] = np.zeros(num_parties)

    # Include steps at increments of 2.5%
    increments = np.linspace(0, num_graphics, num=num_graphics)

    # Always include step 0 and step 40

    all_steps = list(range(1, num_graphics - 1))
    selected_steps = sorted(random.sample(all_steps, num_selected_steps - 2) + [0, num_graphics - 1])
    selected_steps.sort()

    # Check if output directory exists; if not, create it
    output_dir = 'output_images'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Load the background image
    background_img = mpimg.imread('Required_Images/background.jpg')

    # Generate a separate image for each selected step for each riding
    for r, riding in enumerate(sorted_ridings):
        print(f'Starting processing for riding {riding["name"]}')
        # Track if seat counts have been updated for this riding
        previous_leading_party=None
        name_font_size = 22


        # Then loop through all steps for that specific riding
        for step in selected_steps:
            print(f'Starting graphics for step {step} for riding {riding["name"]}')
            try:
                # Calculate remaining votes for current step
                total_votes = np.sum(vote_totals_by_riding[r][step])
                remaining_votes = np.sum(riding['final_results']) - total_votes

                # Determine if winner is decided
                is_winner_determined = determine_winner(vote_totals_by_riding[r][step], remaining_votes)

                # Update the winning candidate index if a winner is determined and not already set
                if is_winner_determined and winning_candidate_indices[r] == -1:
                    winning_candidate_indices[r] = np.argmax(vote_totals_by_riding[r][step])
                    winner_determined_steps[r] = step  # Store the step where the winner was determined

                fig, ax = plt.subplots(figsize=(12, 8))

                # Ensure this line is added before saving each figure
                plt.subplots_adjust(left=0, right=1, top=1, bottom=0)  # Remove any margins around the plot

                ax.imshow(background_img, aspect='auto', extent=[0, 1, 0, 1],
                          alpha=0.2)  # Make sure it covers the full area

                ax.axis('off')
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)

                # Sort candidates by vote count for the current step
                sorted_indices = np.argsort(-vote_totals_by_riding[r][step])
                sorted_votes = vote_totals_by_riding[r][step][sorted_indices]
                sorted_names = np.array(riding['candidate_names'])[sorted_indices]
                sorted_parties = np.array(riding['party_names'])[sorted_indices]
                sorted_short_parties = np.array(riding['short_name'])[sorted_indices]
                sorted_colors = np.array([party_colors[party] for party in sorted_parties])

                total_votes_step = sorted_votes.sum()
                num_candidates = min(len(riding['candidate_names']), 4)
                width = 0.8 / 4
                padding = 0.1 / 4

                # Dimensions for the picture placeholder
                picture_width = width * 0.5
                picture_height = 0.2  # Height of the picture placeholder

                # Adjust y_pos for the picture box so it ends before the candidate information box


                # Limit to first 4 candidates
                max_displayed_candidates = 4
                num_candidates_to_display = min(len(sorted_votes), max_displayed_candidates)

                # Calculate the number of columns and rows needed
                num_displayed_columns = min(num_candidates_to_display, 4)  # Number of columns, up to a max of 4
                num_displayed_rows = (num_candidates_to_display - 1) // num_displayed_columns + 1  # Number of rows

                # Calculate the total width and height needed for the displayed candidate boxes
                total_width = num_displayed_columns * (width + padding) - padding  # Total width required for boxes
                total_height = num_displayed_rows * (
                            0.35 + picture_height)  # Total height required for boxes, including picture space

                # Calculate starting position to center the candidate block within the screen
                start_x = (1 - total_width) / 2  # Horizontal centering
                start_y = (1 - total_height) / 2  # Vertical centering
                # Set the initial font size




                for j in range(num_candidates_to_display):
                    col = j % num_displayed_columns
                    row = j // num_displayed_columns

                    # Calculate position for each candidate box
                    x_pos = start_x + col * (width + padding) + width / 2
                    y_pos = start_y + row * (0.45 + picture_height)  # Position adjusted for picture and info space
                    picture_y_pos = y_pos + 0.35  # Position it such that it starts at y_pos + 0.35 and ends before the information box
                    # Draw candidate's information box
                    # Create the rectangle with a transparent fill
                    rect = plt.Rectangle((x_pos - width / 2, y_pos), width, 0.35 + picture_height,
                                         color=sorted_colors[j], alpha=0.25)  # Fill color with transparency
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

                    # Determine image path
                    candidate_image_path = f'facesteals/{sorted_names[j]}.jpg'
                    if not os.path.exists(candidate_image_path):
                        candidate_image_path = 'Required_Images/nopic.jpg'

                    # Load the image
                    image = plt.imread(candidate_image_path)

                    # Draw picture image above the candidate's information box
                    ax.imshow(image, extent=(x_pos - width / 2+0.005, x_pos,
                                             picture_y_pos - 0.05, picture_y_pos - 0.05 + picture_height),
                              aspect='auto', alpha=1, zorder=1)
                    # Calculate the middle of the picture's height
                    picture_middle_y = picture_y_pos - 0.05 + (picture_height / 2)



                    text_y_pos = y_pos + 0.15   # Center the text within the party color box

                    # Define text margin based on rank
                    lead_margin = calculate_lead_margin(sorted_votes, j,num_candidates_to_display)

                    percentage_of_all = (sorted_votes[j] / total_votes_step) * 100 if total_votes_step > 0 else 0

                    # Fixed Y position for the top of the text
                    fixed_y_pos = text_y_pos  # The same Y position for all text, no adjustment

                    # Generate the text with or without the lead margin
                    # Calculate the center of the unified box for consistent Y positioning
                    y_center = y_pos + 0.25 / 2  # Centered vertically in the box

                    # Prepare the text for the right side
                    text = f'{int(sorted_votes[j])}'



                    # Define the available width for the right side text
                    available_width_right = width / 2-0.02  # Right half of the box

                    # Loop to reduce font size if text width exceeds available width
                    while get_text_width(text,
                                         name_font_size) > available_width_right and name_font_size > 1:  # Ensure font size doesn't go below 1
                        name_font_size -= 1

                    # Calculate positions for the information text on the right side
                    text_x_center = x_pos + (width / 2) / 2  # Center in the right half
                    text_y_center = y_center  # Use common y_center for consistent vertical alignment

                    # Add the information text inside the bottomcandidatebox (right side)
                    ax.text(text_x_center, text_y_center, text,
                            fontsize=name_font_size, ha='center', va='center',
                            color='black')  # Centered both horizontally and vertically

                    if lead_margin > 0:
                        leadtext = f'{int(lead_margin)} \nlead'  # Append lead margin information if applicable
                        ax.text(text_x_center, text_y_center-0.07, leadtext,
                                fontsize=14, ha='center', va='center',
                                color='black')  # Centered both horizontally and vertically

                    # Calculate positions for the percentage text on the left side
                    half_width = width / 2  # Half-width for the left box
                    text_x_left = x_pos - width / 2 + half_width / 2  # Center in the left half
                    text_y_left = y_center  # Use common y_center for consistent vertical alignment

                    # Add the text (percentage_of_all) to the center of the left half
                    ax.text(text_x_left, text_y_left, f'{percentage_of_all:.1f}%',
                            fontsize=22, ha='center', va='center',
                            color='black')  # Centered both horizontally and vertically

                    # Add a progress bar in the bottom third of what was the left half
                    progress_bar_height = 0.02  # Set a height for the progress bar
                    progress_bar_y = y_pos  # Start at the bottom of the box

                    # Calculate the width of the progress bar based on percentage_of_all
                    progress_bar_width = (percentage_of_all / 100) * half_width

                    # Create and add the progress bar to what was the left half of the unified box
                    progress_bar = plt.Rectangle((x_pos - width / 2, progress_bar_y), progress_bar_width,
                                                 progress_bar_height, color=sorted_colors[j], alpha=0.8)
                    ax.add_patch(progress_bar)

                    # Optionally, add the border of the full progress bar area for clarity
                    progress_bar_outline = plt.Rectangle((x_pos - width / 2, progress_bar_y), half_width,
                                                         progress_bar_height, fill=False, edgecolor='black',
                                                         linewidth=1)
                    ax.add_patch(progress_bar_outline)

                    # Use sorted_names[j] as the message
                    message_text = sorted_names[j]  # Set the text to the name
                    message_text_x = x_pos  # Centered across the entire box
                    message_text_y = y_pos + 0.25 - 0.02  # Positioned slightly below the top edge (inside the box)

                    # Set an initial font size for the message
                    initial_font_size = 22
                    minimum_font_size = 12  # Minimum font size to prevent excessive shrinking

                    # Dynamically adjust font size to fit within the box
                    current_font_size = initial_font_size
                    available_width = width - 0.04  # Leave a small margin

                    # Debugging output
                    print(f"Available Width: {available_width}")
                    print(f"Initial Font Size: {current_font_size}")

                    # Only shrink if the text is too wide
                    current_text_width = get_text_width(message_text, current_font_size)
                    print(f"Text Width with Initial Font Size: {current_text_width}")

                    if current_text_width > available_width:
                        while current_text_width > available_width and current_font_size > minimum_font_size:
                            current_font_size -= 1  # Decrease the font size until it fits
                            current_text_width = get_text_width(message_text, current_font_size)  # Update text width
                            print(f"Reducing Font Size: {current_font_size}, Text Width: {current_text_width}")

                    # Add the text message inside the top part with adjusted font size
                    ax.text(message_text_x, message_text_y, message_text,
                            fontsize=current_font_size, ha='center', va='top', color='black')

                    # Calculate the center of the left half of the unified box for the percentage text
                    text_x_left = x_pos - width / 2 + half_width / 2
                    text_y_left = y_pos + 0.25 / 2  # Vertical center of the box

                    # Add the percentage text in the middle of what was the left half
                    ax.text(text_x_left, text_y_left, f'{percentage_of_all:.1f}%',
                            fontsize=22, ha='center', va='center', color='black')

                    # Calculate the center of the left half of the unified box for the percentage text
                    text_x_left = x_pos - width / 2 + half_width / 2
                    text_y_left = y_pos + 0.25 / 2  # Vertical center of the box

                    # Add the percentage text in the middle of what was the left half
                    ax.text(text_x_left, text_y_left, f'{percentage_of_all:.1f}%',
                            fontsize=22, ha='center', va='center', color='black')

                    add_party_box(ax, x_pos, picture_y_pos, picture_height, width, sorted_short_parties, j,sorted_colors)

                    # Draw checkmark if the candidate is the winner
                    if winning_candidate_indices[r] != -1:
                        winning_index = winning_candidate_indices[r]

                        # Find the new index of the winning candidate in the sorted list
                        sorted_winning_index = np.where(sorted_indices == winning_index)[0][0]


                        # Only draw the checkmark if it's among the displayed candidates
                        if sorted_winning_index < max_displayed_candidates:
                            x_pos_check = start_x + (sorted_winning_index % num_displayed_columns) * (
                                        width + padding) + width / 2
                            y_pos_check = start_y + (sorted_winning_index // num_displayed_columns) * (
                                        0.35 + picture_height)

                            # Draw the checkmark closer to the right side of the candidate box
                            ax.text(x_pos_check + width / 2 - 0.005, y_pos_check + 0.35, '✓',
                                    fontsize=72, ha='right', va='top', color='green')

                draw_progress_bar(ax, step, num_graphics,riding)

                # Create a dictionary for party seat counts using 'seats' from all_parties

                # Example votes for a riding
                votes_by_riding = vote_totals_by_riding[r][step]  # e.g., [5000, 3000, 2000, 500]
                parties_by_riding = np.array(riding['party_names'])

                # 1. Update temp_vote for each step
                update_running_tally(votes_by_riding, parties_by_riding, all_parties)

                # Print the temp_vote to track running totals
                for party in all_parties:
                    print(f"{party['name']} - Running Tally (temp_vote): {party['temp_vote']}")

                if np.any(votes_by_riding > 0):
                    # Get the leading party for the current riding
                    leading_party = get_leading_party(votes_by_riding, parties_by_riding)

                    # Check if there is a change in the leading party
                    if leading_party != previous_leading_party:
                        # Decrement the seat count for the previous leading party if it exists
                        if previous_leading_party:
                            if previous_leading_party in party_seat_counts:
                                party_seat_counts[previous_leading_party] -= 1
                                print(f"Decremented seat count for previous leading party: {previous_leading_party}")

                        # Increment the seat count for the new leading party
                        if leading_party:
                            if leading_party not in party_seat_counts:
                                party_seat_counts[leading_party] = 0
                            party_seat_counts[leading_party] += 1
                            print(f"Incremented seat count for new leading party: {leading_party}")

                        # Update the previous leading party to the new leading party
                        previous_leading_party = leading_party

                        # Mark seat counts as updated
                        seat_counts_updated = True
                    else:
                        seat_counts_updated = False
                        print("Leading party has not changed; seat count not updated.")
                else:
                    seat_counts_updated = False
                    print("No votes available, seat counts not updated.")

                # Sort parties by seat count in descending order
                sorted_party_seat_counts = dict(
                    sorted(party_seat_counts.items(), key=lambda item: item[1], reverse=True))
                print("Virginia",party_seat_counts.items())

                party_listseat_counts = {party['name']: party['seats_list'] for party in all_parties}

                combined_seat_counts = {
                    party_name: party_seat_counts.get(party_name, 0) + party_listseat_counts.get(party_name, 0)
                    for party_name in party_seat_counts
                }

                # Sort the combined_seat_counts dictionary by the combined value in descending order
                sorted_combined_seat_counts = dict(
                    sorted(combined_seat_counts.items(), key=lambda item: item[1], reverse=True)
                )


                # Print sorted seat counts (for debugging purposes)
                print("Ohio Sorted Combined Seat Counts:", sorted_combined_seat_counts)



                # Draw party seat counts

                seat_count_y_pos = y_pos - 0.35  # Positioning for the seat counts row
                seat_count_height = 0.3  # Height for the seat counts row
                padding = 0.03  # Reduced padding between party boxes
                num_parties = min(len(sorted_combined_seat_counts), 6)  # Limit to first 6 parties for display
                party_width = 0.6 / num_parties  # Adjust width to fit more compactly
                total_width = num_parties * party_width + (num_parties - 1) * padding  # Total width including padding
                start_x = (1 - total_width) / 2  # Center the seat count boxes horizontally
                for i, (party_name, count) in enumerate(
                        list(sorted_combined_seat_counts.items())[:6]):  # Only take the first 6 parties

                    temp_vote = next((party['temp_vote'] for party in all_parties if party['name'] == party_name), 0)

                    # Ensure pop_vote is converted to an integer without decimals
                    temp_vote = math.floor(temp_vote)  # Rounds down to nearest integer
                    # Calculate the total temp_vote across all parties
                    total_temp_vote = sum(party['temp_vote'] for party in all_parties)

                    # Ensure total_temp_vote is converted to an integer without decimals
                    total_temp_vote = math.floor(total_temp_vote)  # Rounds down to nearest integer

                    # Calculate the total temp_vote across all parties excluding 'Independent'
                    noindytotal_temp_vote = sum(
                        party['temp_vote'] for party in all_parties if party['name'] != 'Independent')

                    # Ensure total_temp_vote is converted to an integer without decimals
                    noindytotal_temp_vote = math.floor(total_temp_vote)  # Rounds down to nearest integer

                    # Retrieve the party dictionary using party_name
                    party_dict = next((party for party in all_parties if party['name'] == party_name), None)

                    # Get the short_pname from the dictionary
                    short_pname = party_dict['short_pname'] if party_dict else party_name

                    for party in all_parties:
                        if party['name'] == party_name:
                            party['seats'] = party_seat_counts[party['name']]

                    if party_name != 'Independent' and total_temp_vote > 0:
                        print("doctor ", seatsToProcess)

                        seats_allocated = MMP_calculation(all_parties, seatsToProcess, seatsprocessed)

                        for party in all_parties:
                            if party['name'] == party_name:
                                party['seats'] = party_seat_counts[party['name']]

                        for party in all_parties:
                            if party['name'] in seats_allocated:
                                party['seats_list'] = seats_allocated[party['name']]
                            else:
                                party['seats_list'] = 0  # Set to 0 if the party was not allocated any seats

                party_listseat_counts = {party['name']: party['seats_list'] for party in all_parties}
                party_fptp_counts = {party['name']: party['seats'] for party in
                                     all_parties}  # Assuming you meant 'seats', not 'seats_list'

                combined_seat_counts = {
                    party['name']: party_fptp_counts.get(party['name'], 0) + party_listseat_counts.get(party['name'], 0)
                    for party in all_parties
                }

                sorted_combined_seat_counts = dict(
                    sorted(combined_seat_counts.items(), key=lambda item: item[1], reverse=True)
                )

                for i, (party_name, count) in enumerate(
                        list(sorted_combined_seat_counts.items())[:6]):  # Only take the first 6 parties

                    party_x_pos = start_x + i * (party_width + padding) + party_width / 2

                    # Draw the party box
                    party_box = plt.Rectangle((party_x_pos - party_width / 2, seat_count_y_pos),
                                              party_width, seat_count_height,
                                              color=party_colors.get(party_name, 'grey'),
                                              ec='black',alpha=0.25)  # Use 'grey' if color not found
                    ax.add_patch(party_box)

                    temp_vote = next((party['temp_vote'] for party in all_parties if party['name'] == party_name), 0)

                    # Ensure pop_vote is converted to an integer without decimals
                    temp_vote = math.floor(temp_vote)  # Rounds down to nearest integer
                    # Calculate the total temp_vote across all parties
                    total_temp_vote = sum(party['temp_vote'] for party in all_parties)

                    # Ensure total_temp_vote is converted to an integer without decimals
                    total_temp_vote = math.floor(total_temp_vote)  # Rounds down to nearest integer

                    # Calculate the total temp_vote across all parties excluding 'Independent'
                    noindytotal_temp_vote = sum(party['temp_vote'] for party in all_parties if party['name'] != 'Independent')

                    # Ensure total_temp_vote is converted to an integer without decimals
                    noindytotal_temp_vote = math.floor(total_temp_vote)  # Rounds down to nearest integer

                    # Retrieve the party dictionary using party_name
                    party_dict = next((party for party in all_parties if party['name'] == party_name), None)


                    # Get the short_pname from the dictionary
                    short_pname = party_dict['short_pname'] if party_dict else party_name

                    # Calculate total_vote_percent only if total_temp_vote is greater than 0
                    if total_temp_vote > 0:
                        total_vote_percent = (temp_vote / total_temp_vote) * 100
                    else:
                        total_vote_percent = 0
                    total_vote_percent_formatted = f'{total_vote_percent:.1f}%'

                    # National vote seat allocation

                    if party_name != 'Independent' and total_temp_vote > 0:
                        print("doctor ",seatsToProcess)
                        seats_allocated = MMP_calculation(all_parties, seatsToProcess, seatsprocessed)
                        for party in all_parties:
                            print("bad wolf", party_seat_counts[party['name']])
                            if party['name'] == party_name:
                                party['seats'] = party_seat_counts[party['name']]

                        for party in all_parties:
                            if party['name'] in seats_allocated:
                                party['seats_list'] = seats_allocated[party['name']]
                            else:
                                party['seats_list'] = 0  # Set to 0 if the party was not allocated any seats

                        # Use `seats_allocated` for drawing the seat count text
                        print(all_parties,"tyler")


                        ax.text(party_x_pos, seat_count_y_pos + seat_count_height / 2 + 0.0005,
                                f'{int(seats_allocated.get(party_name, 0))+party_seat_counts.get(party_name,0)}', fontsize=20, ha='center', va='center',
                                color='black')

                    else:
                        ax.text(party_x_pos, seat_count_y_pos + seat_count_height / 2 + 0.0005,
                                f'{int(count)}', fontsize=20, ha='center', va='center', color='black')



                    # Set the position and text for the label
                    # Format the text to be displayed
                    # Main text with fontsize 16
                    # Base vertical position for the main text
                    base_y = seat_count_y_pos + seat_count_height / 2 + 0.075

                    # Vertical offset for spacing between lines
                    offset = 0.03  # Adjust as needed for spacing

                    # Add text for short_pname
                    ax.text(
                        party_x_pos,
                        base_y + offset+0.02,  # Positioned at the top
                        f'{short_pname}',
                        fontsize=16,
                        ha='center',
                        va='center',
                        color='black',
                        bbox=dict(facecolor=party_colors.get(party_name, 'grey'), edgecolor='black',
                                  boxstyle='round,pad=0.1')
                    )
                    # Add text for temp_vote
                    ax.text(party_x_pos, base_y,  # Positioned in the middle
                            f'{temp_vote}',
                            fontsize=12, ha='center', va='center', color='black')

                    # Define the y-positions for the texts
                    vote_text_y = base_y - offset

                    # Add text for total_vote_percent_formatted
                    ax.text(
                        party_x_pos,
                        vote_text_y,  # Positioned at the bottom
                        f'{total_vote_percent_formatted}',
                        fontsize=16,
                        ha='center',
                        va='center',
                        color='black'
                    )

                    # Add a horizontal line directly under total_vote_percent_formatted text
                    line_y = vote_text_y - 0.02  # Adjust the value to control the distance between the text and the line
                    half_party_width = party_width / 2  # Half the width for symmetric positioning
                    ax.hlines(
                        y=line_y,
                        xmin=party_x_pos - half_party_width+0.005,
                        xmax=party_x_pos + half_party_width-0.005,
                        color='black',
                        linewidth=1
                    )

                # Add background image last
                ax.imshow(background_img, aspect='auto', extent=[0, 1, 0, 1], alpha=0.3)

                # Remove the axis lines and labels
                ax.axis('off')

                # Set limits
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)

                # Save the figure
                filename = f'{riding["name"].replace(" ", "_")}_step_{step + 1:02}.png'
                filepath = os.path.join(output_dir, filename)
                plt.savefig(filepath, bbox_inches='tight')
                plt.close()

                # Generate line graph
                fig, ax = plt.subplots(figsize=(max(10, num_candidates * 2), 8))
                ax.set_title(f'Vote Progression in {riding["name"]}')
                ax.set_xlabel('Steps')
                ax.set_ylabel('Votes')

                for idx, candidate_name in enumerate(riding['candidate_names']):
                    ax.plot(increments, vote_totals_by_riding[r][:, idx], label=candidate_name,
                            color=party_colors[riding['party_names'][idx]])

                # Draw a horizontal dotted line at the step where the winner is determined
                if winner_determined_steps[r] is not None:
                    winner_step = winner_determined_steps[r]
                    ax.axvline(x=winner_step, color='red', linestyle='--', label='Winner Determined')

                ax.legend(loc='upper left')
                plt.grid(True)

                line_graph_filename = f'line_graph_riding_{r + 1:02}_{riding["name"].replace(" ", "_")}.png'
                line_graph_filepath = os.path.join(output_dir, line_graph_filename)
                plt.savefig(line_graph_filepath)
                plt.close()



            except Exception as e:

                print(f"Error processing step {step} for riding {riding['name']}: {e}")
        votes_by_riding = vote_totals_by_riding[r][step]  # e.g., [5000, 3000, 2000, 500]
        parties_by_riding = riding[
                    'party_names']  # e.g., ['Liberal Party of Canada', 'Conservative Party of Canada', ...]
                # 2. After processing the whole riding, finalize the frozentotal (pop_vote)
        finalize_riding_votes(votes_by_riding, parties_by_riding, all_parties)
        seatsprocessed = seatsprocessed + 1


                # Now print the final updated pop_vote after finalizing
        for party in all_parties:
            print(f"{party['name']} - Total Votes (pop_vote): {party['pop_vote']}")

        print(f'Completed all graphics for riding {riding["short_name"]} with final results: {riding["final_results"]}')


        # Update the 'seats_list' field in all_parties based on the seat allocation
        for party in all_parties:
            if party['name'] in seats_allocated:
                party['seats_list'] = seats_allocated[party['name']]


            riding_name = riding['name']
            file_path = f'irlriding/{riding_name}.txt'
            input_svg = f'svg/{riding_name}.svg'
            output_dir = f'output_images'
            party_names=riding['short_name']  # Assuming this is a list of party short names
            pop_votes=riding['final_results']  # Flatten the list of final results

            # Ensure pop_votes is a list of integers or floats
            pop_votes = [float(vote) for vote in pop_votes]

            # After the loop, call mapmaker_main with the collected data
            mapmaker_main(file_path, input_svg, output_dir, party_names, pop_votes,riding_name)

        print('Processed all ridings for all steps')
        for party in all_parties:
            print(f"Name: {party.get('name')}")
            print(f"Short Name: {party.get('short_pname')}")
            print(f"Color: {party.get('color')}")
            print(f"Seats: {party.get('seats')}")
            print(f"Seat Hold: {party.get('seats_list')}")
            print(f"Popular Vote: {party.get('pop_vote')}")
            print(f"Temporary Vote: {party.get('temp_vote')}")
            print("-" * 20)
    print('end')
    listcreation()



