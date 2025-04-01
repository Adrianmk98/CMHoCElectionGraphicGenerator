import random
import numpy as np
import logging

def calculate_selected_steps(num_graphics, num_selected_steps):
    """Calculate evenly distributed steps with some randomness."""
    selected_steps = [0]  # Always include first step
    
    if num_selected_steps > 2:
        # Calculate evenly spaced steps between 1 and num_graphics-2
        step_size = (num_graphics - 1) / (num_selected_steps - 1)
        middle_steps = []
        
        for i in range(1, num_selected_steps - 1):
            step = int(i * step_size)
            # Add some small randomness to avoid monotony
            step = min(max(1, step + random.randint(-1, 1)), num_graphics - 2)
            if step not in middle_steps:
                middle_steps.append(step)
        
        # Sort and add middle steps
        middle_steps.sort()
        selected_steps.extend(middle_steps)
    
    # Always include final step
    if num_graphics - 1 not in selected_steps:
        selected_steps.append(num_graphics - 1)
    
    # Ensure we have exactly num_selected_steps
    while len(selected_steps) > num_selected_steps:
        # Remove steps from the middle, keeping first and last
        middle_indices = list(range(1, len(selected_steps) - 1))
        if middle_indices:
            remove_idx = random.choice(middle_indices)
            selected_steps.pop(remove_idx)
    
    selected_steps.sort()
    return selected_steps

def store_party_state(all_parties):
    """Store the current state of all parties."""
    return [{
        'name': party['name'],
        'pop_vote': party.get('pop_vote', 0),
        'temp_vote': party.get('temp_vote', 0),
        'seats': party.get('seats', 0),
        'seats_list': party.get('seats_list', 0)
    } for party in all_parties]

def restore_party_state(all_parties, stored_state):
    """Restore party state from stored state."""
    for stored_party in stored_state:
        for party in all_parties:
            if party['name'] == stored_party['name']:
                party['pop_vote'] = stored_party['pop_vote']
                party['temp_vote'] = stored_party['temp_vote']
                party['seats'] = stored_party['seats']
                party['seats_list'] = stored_party['seats_list']
                break

def initialize_riding_data(riding, max_parties):
    """Initialize and validate riding data, padding with empty entries if needed."""
    if len(riding['party_names']) != len(riding['final_results']):
        min_length = min(len(riding['party_names']), len(riding['final_results']))
        riding['party_names'] = riding['party_names'][:min_length]
        riding['final_results'] = riding['final_results'][:min_length]
        riding['short_name'] = riding['short_name'][:min_length]
        riding['candidate_names'] = riding['candidate_names'][:min_length]
    
    # Pad arrays if needed
    current_parties = len(riding['final_results'])
    if current_parties < max_parties:
        padding_needed = max_parties - current_parties
        riding['final_results'] = np.pad(riding['final_results'], (0, padding_needed), 'constant').tolist()
        riding['party_names'].extend(["Empty"] * padding_needed)
        riding['short_name'].extend(["Empty"] * padding_needed)
        riding['candidate_names'].extend(["Empty"] * padding_needed)
    
    return riding

def get_valid_candidates(sorted_votes, sorted_parties):
    """Get list of valid candidates (excluding empty entries)."""
    valid_candidates = []
    for i, (vote, party) in enumerate(zip(sorted_votes, sorted_parties)):
        if party != "Empty":
            valid_candidates.append((i, vote))
            logging.debug(f"Added candidate {i} with party {party} and vote {vote} to valid candidates")
        else:
            logging.debug(f"Skipped empty candidate {i}")
    
    logging.debug(f"Total valid candidates: {len(valid_candidates)}")
    return valid_candidates 