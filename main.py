from staging_data import DatabaseControl
import reference_data
import staging_data
import time

# Rename to run_all.py?

'''
REFERENCE DATA

ref_data() adds teams and players in reference tables.
Use 'first_insert=True' argument for first time data loading (affectes ref_players only)
Other wise 'first_insert=False'
'''
# reference_data.ref_data(first_insert=False)


'''
STAGING DATA

Loads 3 teams at a time with stg_data() function call. Can put in a for loop with 10 numbers for continuation.
add time.sleep(10) to avoid overloading API

Team Stacks:
(1: ATL, BOS, BKN)   (2: CHA, CHI, CLE)   (3: DAL, DEN, DET)   (4: GSW, HOU, IND)   (5: LAC, LAL, MEM)31/5 
(6: MIA, MIL, MIN)   (7: NOP, NYK, OKC)   (8: ORL, PHI, PHX)   (9: POR, SAC, SAS)   (10: TOR, UTA, WAS)
'''
# NOT WORKING PROPERLY
# Option 1: Continuous
# for n in range(1, 11):
#     staging_data.stg_data(stack=n, database_on=True)
#     time.sleep(10)
# # Close the connection
# DatabaseControl.connection.close()

# Option 2: Individual call (3 at a time)
staging_data.stg_data(5)