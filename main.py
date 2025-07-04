import ETL.reference_data as reference_data
import ETL.staging_data as staging_data
from ETL.orchestrate_load import LoadOrchestrator

'''
REFERENCE DATA

ref_data() adds teams and players in reference tables.
Use 'first_insert=True' argument for first time data loading (affects ref_players only)
Other wise 'first_insert=False' (default)
'''
reference_data.ref_data(first_insert=False)


'''
STAGING DATA
Loads 3 teams at a time with stg_data() function call.

Team Stacks:
(1: ATL, BOS, BKN)   (2: CHA, CHI, CLE)   (3: DAL, DEN, DET)   (4: GSW, HOU, IND)   (5: LAC, LAL, MEM) 
(6: MIA, MIL, MIN)   (7: NOP, NYK, OKC)   (8: ORL, PHI, PHX)   (9: POR, SAC, SAS)   (10: TOR, UTA, WAS)
'''
# Call one stack at a time (3 teams in one stack)
# staging_data.stg_data(8)


# One team / season segment at a time
staging_data.stg_one('MIL', 'Regular Season')
staging_data.stg_one('MIL', 'Playoffs')

rows = LoadOrchestrator().run_all()
print(rows)


# Get latest insert update for teams
# staging_data.get_updates()