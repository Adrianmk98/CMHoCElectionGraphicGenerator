import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os
from matplotlib import patches
from inputs.party_data import all_parties
from inputs.vote_data import ridings
from inputs.list_candidates import party_listcandidates

def add_candidate_image(ax, img, x, y, candidate_number, candidate, party_colour):
    rect = patches.Rectangle((x + 0.1, y + 0.2), 1.2, 1.8, linewidth=1, edgecolor='black',
                             facecolor=party_colour, alpha=0.3, zorder=1)
    ax.add_patch(rect)

    # Define a small margin for the left side
    left_margin = 0.05  # Left margin
    right_margin = 0.05  # Right margin for text
    top_margin = 0.05  # Small top margin
    bottom_margin = 0.1  # Small bottom margin for image

    # Calculate the vertical center for the rectangle
    rect_y_start = y + 0.2
    rect_y_end = rect_y_start + 1.8
    rect_height = rect_y_end - rect_y_start
    img_height = rect_height - top_margin - bottom_margin  # Total height for image

    # Add the image on the left half of the box, centered vertically
    img_x_start = x + 0.1 + left_margin  # Left margin
    img_x_end = x + 0.1 + 0.55  # Image takes up half of the box
    img_y_start = rect_y_start + (rect_height - img_height) / 2  # Center vertically
    img_y_end = img_y_start + img_height  # Extend to the calculated height

    ax.imshow(img, extent=(img_x_start, img_x_end, img_y_start, img_y_end), aspect='auto', zorder=2)



# Create a function to determine if a candidate was elected or from a list seat
def get_elected_candidates():
    elected_candidates = {}
    for riding in ridings:
        max_votes = max(riding['final_results'])
        for idx, votes in enumerate(riding['final_results']):
            if votes == max_votes:
                party = riding['party_names'][idx]
                candidate = riding['candidate_names'][idx]
                if party not in elected_candidates:
                    elected_candidates[party] = []
                elected_candidates[party].append(candidate)
    return elected_candidates

def get_elected_ridings():
    elected_ridings = {}
    for riding in ridings:
        max_votes = max(riding['final_results'])
        for idx, votes in enumerate(riding['final_results']):
            if votes == max_votes:
                party = riding['party_names'][idx]
                candidate = riding['candidate_names'][idx]
                riding_name = riding['name']  # Get the riding name
                if candidate not in elected_ridings:
                    elected_ridings[candidate] = (party, riding_name)  # Store party and riding
    return elected_ridings

elected_ridings=get_elected_ridings()
elected_candidates = get_elected_candidates()

def listcreation():
    number_of_mmp = {party['name']: party['seats_list'] for party in all_parties if party['name'] != 'Independent'}
    number_list_seats = {
        party['name']: number_of_mmp.get(party['name'], 0)
        for party in all_parties if party['name'] != 'Independent'
    }
    print(number_list_seats)

    # Create a graphic for each party
    output_dir = "party_graphics"
    os.makedirs(output_dir, exist_ok=True)
    facesteals_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../facesteals")
    required_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../Required_Images")
    party_colors = {party['name']: party['color'] for party in all_parties}

    for party in party_listcandidates:
        party_name = party['party_name'][0]
        # Create a dictionary for quick lookup of party colors
        party_colour = party_colors.get(party_name, 'grey')  # Get party color, default to grey if not found
        print(party_name, party_colour)
        candidates = party['list_names']

        # Gather elected candidates from this party
        elected_seats = elected_candidates.get(party_name, [])
        listseats = []
        for idx, candidate in enumerate(candidates):
            candidate_number = idx + 1  # Candidate number starts from 1
            emptyspot = ""
            riding_name = ""
            if candidate in elected_ridings:  # Check if the candidate is in the elected_candidates dictionary
                party, riding_name = elected_ridings[candidate]  # Unpack party and riding name
            elif len(listseats) < number_list_seats.get(party_name, 0):
                if candidate not in elected_ridings:
                    listseats.append(candidate)
            else:
                emptyspot = "not elected"
        total_needed_seats = number_list_seats.get(party_name, 0) - len(listseats)

        # Set up the figure with dynamic height
        unique_elected_seats = [candidate for candidate in elected_seats if candidate not in candidates]
        total_candidates = len(candidates) + len(unique_elected_seats)+total_needed_seats  # Total unique candidates to display
        print(total_candidates)
        num_cols = 2 if total_candidates <= 16 else 3  # Up to 2 columns for 16 candidates or less, else 3
        num_rows = ((total_candidates + num_cols) // num_cols)  # Calculate number of rows needed
        fig_height = 3 + num_rows * 2  # Adjust height based on rows
        fig, ax = plt.subplots(figsize=(8, fig_height))

        ax.set_xlim(0, num_cols * 1.5)  # Set width based on number of columns
        ax.set_ylim(0, fig_height)

        # Add a banner with the party name
        ax.text(1.5, fig_height - 0.5, party_name, ha='center', va='center', fontsize=16, weight='bold', color='white',
                bbox=dict(facecolor=party_colour, alpha=0.7, boxstyle="round,pad=0.5"))

        ax.axis('off')

        # Track assigned list seats
        assigned_list_seats = []

        # Draw boxes for candidates on the list
        for idx, candidate in enumerate(candidates):
            col = idx // num_rows  # Calculate column based on row number
            row = idx % num_rows  # Calculate row number
            x = col * 1.5  # Set x position based on column
            y = fig_height - (0.8+2 + (row * 2))  # Adjust y to fit within the dynamic height

            # Load candidate image
            image_path = os.path.join(facesteals_dir, f"{candidate}.jpg")
            img = mpimg.imread(image_path) if os.path.exists(image_path) else mpimg.imread(os.path.join(required_dir, "nopic.jpg"))

            add_candidate_image(ax, img, x, y, idx + 1, candidate, party_colour)

            # Position the text on the right half of the box with margins
            top_margin = 0.05  # Small top margin
            right_margin = 0.05
            text_x = x + 0.1 + 0.9  # Start text after the image with a small margin
            text_y_start = y + 1.05 - top_margin  # Position for candidate name
            text_y_status = y + 0.80 - top_margin  # Position for status text

            # Display the number based on column and row index
            candidate_number = idx + 1  # Candidate number starts from 1
            # Position the candidate number in the top right corner of the rectangle
            number_x = x + 0.1 + 1.2 - right_margin  # Right edge of rectangle minus margin
            number_y = y + 1.7  # Near the top of the rectangle

            ax.text(number_x, number_y, str(candidate_number), ha='right', va='top', fontsize=12, weight='bold')
            ax.text(text_x, text_y_start, f"{candidate}", ha='center', va='top', fontsize=10)

            # Determine candidate status
            status = ""
            riding_name = ""
            if candidate in elected_ridings:  # Check if the candidate is in the elected_candidates dictionary
                party, riding_name = elected_ridings[candidate]  # Unpack party and riding name
                formatted_riding_name = riding_name.replace(" and ", " \nand ")  # Replace "and" with "\nand"
                status = f"elected \n{formatted_riding_name}"  # Create status with formatted riding name
                colour = 'green'
            elif len(assigned_list_seats) < number_list_seats.get(party_name, 0):
                if candidate not in elected_ridings:
                    status = "list seat"
                    assigned_list_seats.append(candidate)
                    colour = 'blue'
            else:
                status = "not elected"
                colour = 'red'

            # Draw status text
            ax.text(text_x, text_y_status, status, ha='center', va='top', fontsize=6, weight='bold',
                    color=colour)

        # Handle placeholders for remaining list seats
        total_needed_seats = number_list_seats.get(party_name, 0) - len(assigned_list_seats)
        for i in range(total_needed_seats):
            # Calculate position for placeholders
            idx = len(candidates) + i  # Increment index for placeholder
            col = idx // num_rows  # Calculate column based on index
            row = idx % num_rows  # Calculate row number
            x = col * 1.5
            y = fig_height - (0.8+2 + (row * 2))

            img = mpimg.imread(os.path.join(required_dir, "nopic.jpg"))
            add_candidate_image(ax, img, x, y, idx + 1, candidate, party_colour)
            # Position the text on the right half of the box with margins
            top_margin = 0.05  # Small top margin
            text_x = x + 0.1 + 0.9  # Start text after the image with a small margin
            text_y_start = y + 1.05 - top_margin  # Position for candidate name
            text_y_status = y + 0.80 - top_margin  # Position for status text
            # Position the candidate number in the top right corner of the rectangle
            right_margin = 0.05
            number_x = x + 0.1 + 1.2 - right_margin  # Right edge of rectangle minus margin
            number_y = y + 1.7  # Near the top of the rectangle
            ax.text(number_x, number_y, "NL", ha='right', va='top', fontsize=12, weight='bold')

            ax.text(text_x, text_y_start, "Placeholder", ha='center', va='top', fontsize=10)
            ax.text(text_x, text_y_status, "list seat", ha='center', va='top', fontsize=6, color='blue')

        # Draw boxes for elected candidates not on the list
        non_list_elected_candidates = [c for c in elected_seats if c not in candidates]
        for i, candidate in enumerate(non_list_elected_candidates):
            # Calculate position for non-list elected candidates
            idx = len(candidates) + total_needed_seats + i  # Increment index for non-list elected candidates
            col = idx // num_rows  # Up to 2 or 3 columns
            row = idx % num_rows

            x = col * 1.5
            y = fig_height - (0.8+2 + (row * 2))

            # Load candidate image
            image_path = os.path.join(facesteals_dir, f"{candidate}.jpg")
            img = mpimg.imread(image_path) if os.path.exists(image_path) else mpimg.imread(os.path.join(required_dir, "nopic.jpg"))

            add_candidate_image(ax, img, x, y, idx + 1, candidate, party_colour)
            # Position the text on the right half of the box with margins
            top_margin = 0.05  # Small top margin
            text_x = x + 0.1 + 0.9  # Start text after the image with a small margin
            text_y_start = y + 1.05 - top_margin  # Position for candidate name
            text_y_status = y + 0.80 - top_margin  # Position for status text

            # Position the candidate number in the top right corner of the rectangle
            right_margin = 0.05
            number_x = x + 0.1 + 1.2 - right_margin  # Right edge of rectangle minus margin
            number_y = y + 1.7  # Near the top of the rectangle
            ax.text(number_x, number_y, "NL", ha='right', va='top', fontsize=12, weight='bold')

            # Display the number based on index
            # Determine candidate status
            status = ""
            riding_name = ""
            if candidate in elected_ridings:  # Check if the candidate is in the elected_candidates dictionary
                party, riding_name = elected_ridings[candidate]  # Unpack party and riding name
                status = f"elected \n{riding_name}"  # Create status with riding name

            ax.text(text_x, text_y_start, f"{candidate}", ha='center', va='top', fontsize=10)
            ax.text(text_x, text_y_status, status, ha='center', va='top', fontsize=6, color='green')

        # Save the graphic as a jpg file
        # Set background image
        background_image_path = os.path.join(required_dir, "background.jpg")
        img = mpimg.imread(background_image_path)

        # Set extent to stretch the background image to cover the entire figure area
        ax.imshow(img, aspect='auto', extent=[0, num_cols * 2, 0, fig_height], zorder=-1,alpha=0.2)

        # Keep existing elements and drawings on top of the background image
        ax.set_xlim(0, num_cols * 1.5)
        ax.set_ylim(0, fig_height)
        ax.axis('off')

        output_path = os.path.join(output_dir, f"{party_name.replace(' ', '_')}.jpg")
        plt.savefig(output_path, format='jpg', bbox_inches='tight')
        plt.close()
