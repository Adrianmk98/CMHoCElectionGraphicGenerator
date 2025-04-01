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

OPERATION MANUAL

in MAIN.PY
**num_selected_steps** is the number of images created per riding
**byelection** should be set as 0
**SeatsinElection** is the number of seats in the GE

in inputs/party_data ensure parties are correct and in the below format
all_parties = [
    {'name': 'Liberal Party of Canada','short_pname':'LPC', 'color': 'red','seats':0,'seats_list':0,'pop_vote':0, 'temp_vote': 0},
    {'name': 'Conservative Party of Canada','short_pname':'CPC', 'color': 'blue','seats':0,'seats_list':0,'pop_vote':0, 'temp_vote': 0},
    {'name': 'New Democratic Party','short_pname':'NDP', 'color': 'orange','seats':0,'seats_list':0,'pop_vote':0, 'temp_vote': 0},
    {'name': 'Independent','short_pname':'IND', 'color': 'gray','seats':0,'seats_list':0,'pop_vote':0, 'temp_vote': 0}

in inputs/list_candidates ensure that the list seats are in order
party_listcandidates = [
    {
        'party_name': ['Conservative Party of Canada'],
        'list_names': ['Hayley182_', 'FreedomCanada2025','Unlucky_Kale_5342','ThomasKaffee','realbassist','raymondl810','jeninhenin','melp8836']
    },
    {
        'party_name': ['Liberal Party of Canada'],
        'list_names': ['WonderOverYander', 'Trick_Bar_1439','SaskPoliticker','zetix026','Ohwen','Phonexia2','Tyty_1234','CosmoCosma']
    },
    {
        'party_name': ['New Democratic Party'],
        'list_names': ['zhuk236', 'redwolf177','PhlebotinumEddie','Scribba25','Effective-Cow-9223','Model-EpicMFan','AdSea260','MrWhiteyIsAwesome','NinjjaDragon','ConfidentIt','username222222345','natelooney','SHOCKULAR','Ibney00']
    }

    ]
]

In **vote_data** ensure that riding results are in the below order in the below format
ridings = [

{ 'name': 'Atlantic Canada',
    'final_results': [467355, 737582],
    'candidate_names': ['Phonexia2', 'PhlebotinumEddie'],
    'party_names': ['Liberal Party of Canada', 'New Democratic Party'],
    'short_name': ['LPC', 'NDP']
  },
 { 'name': 'Centre of Quebec and Eastern Townships',
    'final_results': [422434, 482489, 168439],
    'candidate_names': ['jeninhenin', 'Model-Ben', 'PGF3'],
    'party_names': ['Conservative Party of Canada', 'Liberal Party of Canada', 'New Democratic Party'],
    'short_name': ['CPC', 'LPC', 'NDP']
  },  { 'name': 'Montreal',
    'final_results': [502274, 499859],
    'candidate_names': ['Zhuk236', 'model-av'],
    'party_names': ['Conservative Party of Canada', 'Liberal Party of Canada'],
    'short_name': ['CPC', 'LPC']
  },]
