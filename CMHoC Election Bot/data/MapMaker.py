import xml.etree.ElementTree as ET
import json


def normalize_riding_name(name):
    normalized_name = name.replace('—', '-').replace('–', '-').replace('−', '-').replace('â€”', '-')
    print(f"Normalized riding name: {name} -> {normalized_name}")
    return normalized_name


def parse_results(file_path):
    riding_results = {}
    parties = ['LPC', 'CPC', 'NDP', 'GRN', 'BLOC', 'PPC', 'IND']
    print(f"Parsing results from file: {file_path}")
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(',')
            if len(parts) < 8:
                print(f"Skipping incomplete line: {line.strip()}")
                continue
            riding_name = normalize_riding_name(parts[0])
            if len(parts) != 1 + len(parties) * 3:
                print(f"Skipping line with incorrect number of columns: {line.strip()}")
                continue
            try:
                vote_percentages = [float(x.strip('%')) / 100 for x in parts[1:]]
                print(f"Parsed vote percentages for {riding_name}: {vote_percentages}")
            except ValueError:
                print(f"Skipping line due to value error: {line.strip()}")
                continue
            riding_results[riding_name] = vote_percentages
    return riding_results


def calculate_weighted_average(nvp, year_weights, year, riding, party):
    print(f"Calculating weighted average for Year: {year}, Riding: {riding}, Party: {party}")
    print(f"NVP Values: {nvp}")
    print(f"Year Weights: {year_weights}")
    weighted_average = sum(value * weight for value, weight in zip(nvp, year_weights))
    print(f"Weighted average: {weighted_average}")
    return weighted_average

def lighten_color(color, factor):
    """Lightens the color by multiplying each RGB component by (1 - factor)."""
    hex_color = color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    lighter_rgb = tuple(int((1 - factor) * component + factor * 255) for component in rgb)
    return '#{:02x}{:02x}{:02x}'.format(*lighter_rgb)


def calculate_party_averages_per_year(riding_results, parties, year_index):
    party_totals = {party: 0.0 for party in parties}
    party_counts = {party: 0 for party in parties}
    print(f"Calculating party averages for year index: {year_index}")

    for riding_name, percentages in riding_results.items():
        start_index = year_index * len(parties)
        end_index = start_index + len(parties)
        year_percentages = percentages[start_index:end_index]

        print(f"Riding: {riding_name}, Year Percentages: {year_percentages}")

        for party_index, party in enumerate(parties):
            vote_percentage = year_percentages[party_index]
            if vote_percentage != 0:
                party_totals[party] += vote_percentage
                party_counts[party] += 1

    party_averages = {party: (party_totals[party] / party_counts[party] if party_counts[party] > 0 else 0) for party in parties}
    print(f"Party Averages for year index {year_index}: {party_averages}")
    return party_averages


def update_svg_fill(input_svg, output_svg,output_json, riding_results, year_index, ratios):
    print(f"Updating SVG file: {input_svg}")
    tree = ET.parse(input_svg)
    root = tree.getroot()
    color_map = {
        'LPC': '#ff0000',
        'CPC': '#0000ff',
        'NDP': '#ffa500',
        'GRN': '#00ff00',
        'BLOC': '#00ffdd',
        'PPC': '#ff1493',
        'IND': '#808080',
        'others': '#d3d3d3'
    }
    parties = ['LPC', 'CPC', 'NDP', 'GRN', 'BLOC', 'PPC', 'IND']
    year_weights = [0.50, 0.333, 0.167]  # Weights for 2019, 2015, and 2011

    # Calculate averages for each party over the years
    party_averages = calculate_party_averages_per_year(riding_results, parties, year_index)
    print(f"Party Averages for Year {year_index + 1}: {party_averages}")
    svg_data = []

    for elem in root.findall(".//*[@data-riding]"):
        elem_riding_name = normalize_riding_name(elem.attrib.get('data-riding'))
        if elem_riding_name in riding_results:
            results = riding_results[elem_riding_name]
            year_results = results[year_index * len(parties):(year_index + 1) * len(parties)]

            print(f"Processing element for riding: {elem_riding_name}")
            print(f"Year Results: {year_results}")
            total_votes=0
            party_votes = {}

            for party_index, party in enumerate(parties):
                riding_vote_percent = year_results[party_index]
                entered_vote_percent = ratios.get(party, 0)

                print(
                    f"Party: {party}, Riding Vote Percent: {riding_vote_percent}, Entered Vote Percent: {entered_vote_percent}")

                if party_averages[party] > 0:  # Avoid division by zero
                    ratio_change = entered_vote_percent / party_averages[party]
                    nvp = riding_vote_percent * ratio_change
                    party_votes[party] = nvp
                    total_votes += nvp
                    print(f"Ratio Change for {party}: {ratio_change}, NVP: {nvp}")
                else:
                    party_votes[party] = 0

            # Normalize party_votes to be percentages of the total
            if total_votes > 0:
                for party in party_votes:
                    party_votes[party] = (party_votes[party] / total_votes) * 100

            # Optionally, you might want to print the normalized results to verify
            for party, vote_percent in party_votes.items():
                print(f"Normalized Vote Percent for {party}: {vote_percent:.2f}%")

            # Compile results for all years into one result
            nvp_values = [party_votes.get(party, 0) for party in parties]
            #weighted_average = calculate_weighted_average(nvp_values, year_weights, year_index + 1, elem_riding_name, party)

            # Sort party votes by percentage and find the top two
            sorted_votes = sorted(party_votes.items(), key=lambda x: x[1], reverse=True)
            if len(sorted_votes) > 1:
                margin = sorted_votes[0][1] - sorted_votes[1][1]
            else:
                margin = 0  # Only one party has votes

            print(f"Margin between first and second: {margin}")

            # Determine the winner and adjust color brightness based on margin
            winner_party = sorted_votes[0][0]
            color = color_map.get(winner_party, '#d3d3d3')  # Default to gray if no match

            if margin < 5:  # Less than 5% margin, lighten color significantly
                color = lighten_color(color, 0.5)  # Lighten the color more
            elif margin < 20:  # Less than 10% margin, lighten color slightly
                color = lighten_color(color, 0.3)  # Lighten the color slightly

            print(f"Winner Party: {winner_party}, Fill Color: {color}")
            elem.set('fill', color)

            svg_data.append({
                'riding': elem_riding_name,
                'party': winner_party,
                'votes': party_votes,
                'margin': margin,
                'fill_color': color
            })

        tree.write(output_svg)
        print(f"SVG file written to: {output_svg}")
        with open(output_json, 'w') as json_file:
            json.dump(svg_data, json_file, indent=4)
        print(f"Data written to {output_json}")


def mapmaker_main(file_path, input_svg, output_dir,party_names, pop_votes,riding_name):
    # Debugging: Print party_names and pop_votes
    print(f"Party Names: {party_names}")
    print(f"Pop Votes: {pop_votes}")
    riding_results = parse_results(file_path)

    # Create a dictionary for party votes
    party_votes = {party_name: 0 for party_name in party_names}
    totalpopvotes=0

    # Assuming pop_votes matches the order of party_names
    for name, votes in zip(party_names, pop_votes):
        if name in party_votes:
            party_votes[name] += votes
            totalpopvotes+=votes

    print(f"Party Votes: {party_votes}")

    ratios = {}
    for party_name in party_names:
        if totalpopvotes > 0:
            percent = (party_votes[party_name] / totalpopvotes) * 100
            print(percent)
            ratios[party_name] = percent / 100
        else:
            ratios[party_name] = 0

    print(f"Ratios: {ratios}")

    # Continue with further logic


    # You can add additional code here to handle SVG and output

    for year_index in range(1):  # Adjust range for more years if needed
        print(f"Processing year index: {year_index}")
        output_svg = f'{output_dir}/{riding_name}.svg'
        output_json = f'{output_dir}/{riding_name}_data.json'
        update_svg_fill(input_svg, output_svg,output_json, riding_results, year_index, ratios)




