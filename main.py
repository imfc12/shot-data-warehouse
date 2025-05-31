import reference_data
from staging_data import StageTeamShotData

# Rename to run_all.py?

'''
REFERENCE DATA

ref_data() adds teams and players in reference tables.
Use 'first_insert=True' argument for first time data loading (affectes ref_players only)
Other wise 'first_insert=False'
'''
reference_data.ref_data(first_insert=False)



'''
STAGING DATA
- Manually select one team and season segment at a time
- Loop over teams?
'''

instance = StageTeamShotData()

