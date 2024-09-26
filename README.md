# CMHoCElectionGraphicGenerator

The CMHoC Election Graphic Generator allows for the quick generation of results if there is a list seat requirement for the election. To do this it takes a specific input in the vote_data file, for as many ridings as required.

{ 'name': 'Golden Horseshoe',
    'final_results': [531801, 408861],
    'candidate_names': ['generic_CPC', 'generic_Liberal'],
    'party_names': ['Conservative Party of Canada', 'Liberal Party of Canada'],
    'short_name': ['CPC', 'LPC']
  }

It will track the vote counts of the parties and allows for a random generation of different results. The user is able to able to set the number of steps they wish to generate, and have have that many images generated 

![Golden_Horseshoe_step_27](https://github.com/user-attachments/assets/ab7a2f8f-df7a-4fba-9fc9-dd0004bb9e40)


It also has a seat counter at the bottom, which keeps track of the total vote count to be able to calculate the list vote.

Alongside the code will generate a line graph which shows the progression of the riding so you can watch the vote come in

![line_graph_riding_03_Golden_Horseshoe](https://github.com/user-attachments/assets/d011eade-9eab-4e3e-b2f5-bfd0e259ca58)

It will also generate an svg with the riding with the ridings coloured with the winner. It will also create a json file that can be used with the original svg in order to see ridings results mapped on their real life counterparts
