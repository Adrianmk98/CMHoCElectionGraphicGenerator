# CMHoCElectionGraphicGenerator

The CMHoC Election Graphic Generator allows for the quick generation of results if there is a list seat requirement for the election. To do this it takes a specific input in the vote_data file, for as many ridings as required.

{ 'name': 'Golden Horseshoe',
    'final_results': [531801, 408861],
    'candidate_names': ['generic_CPC', 'generic_Liberal'],
    'party_names': ['Conservative Party of Canada', 'Liberal Party of Canada'],
    'short_name': ['CPC', 'LPC']
  }

It will track the vote counts of the parties and allows for a random generation of different results. The user is able to able to set the number of steps they wish to generate, and have have that many images generated 

![Golden_Horseshoe_step_15](https://github.com/user-attachments/assets/62642fb5-8243-43be-b677-468731c8087e)

It also has a seat counter at the bottom, which keeps track of the total vote count to be able to calculate the list vote.

Alongside the code will generate a line graph which shows the progression of the riding so you can watch the vote come in

![line_graph_riding_01_Golden_Horseshoe](https://github.com/user-attachments/assets/8b852668-5999-43af-a30d-81b094acfac1)

It will also generate an svg with the riding with the ridings coloured with the winner. It will also create a json file that can be used with the original svg in order to see ridings results mapped on their real life counterparts
