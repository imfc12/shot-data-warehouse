import ETL.reference_data as reference_data
import ETL.staging_data as staging_data
from ETL.orchestrate_load import LoadOrchestrator

# Rename to run_all.py?

'''
REFERENCE DATA

ref_data() adds teams and players in reference tables.
Use 'first_insert=True' argument for first time data loading (affectes ref_players only)
Other wise 'first_insert=False'
'''
# reference_data.ref_data(first_insert=True)


'''
STAGING DATA

Loads 3 teams at a time with stg_data() function call. Can put in a for loop with 10 numbers for continuation.
add time.sleep(10) to avoid overloading API

Team Stacks:
(1: ATL, BOS, BKN)1/6   (2: CHA, CHI, CLE)1/6   (3: DAL, DEN, DET)1/6   (4: GSW, HOU, IND)1/6   (5: LAC, LAL, MEM)31/5 
(6: MIA, MIL, MIN)1/6   (7: NOP, NYK, OKC)1/6   (8: ORL, PHI, PHX)   (9: POR, SAC, SAS)1/6   (10: TOR, UTA, WAS)1/6
'''

# Call one stack at a time (3 teams in one stack)
# staging_data.stg_data(8)

# Get last update for teams
# staging_data.get_updates()

# One team / season at a time
"""
DONE
staging_data.stg_one('NYK', 'Regular Season')
staging_data.stg_one('NYK', 'Playoffs')
staging_data.stg_one('MIN', 'Regular Season')
staging_data.stg_one('MIN', 'Playoffs')
"""
# staging_data.stg_one('OKC', 'Regular Season')
# staging_data.stg_one('DEN', 'Playoffs')



rows = LoadOrchestrator().run_all()
print(rows)

