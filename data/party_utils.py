import numpy as np

def get_leading_party(votes, parties):
    if len(votes) > 0 and len(parties) > 0:
        # Get the index of the maximum vote count
        leading_index = np.argmax(votes)
        return parties[leading_index]
    return None