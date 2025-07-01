from ETL.staging_utils import DatabaseControl

class LoadOrchestrator:
    def __init__(self):
        self.conn = DatabaseControl.get_connection()
        self.conn.autocommit = False
        self.procedures = ['DimTeams', 'DimPlayers', 'UpdDimPlayers',
                           'DimGames', 'DimShots', 'DimTime', 'FactShots', 
                           'DeleteStaging']

    # Function to run all procedure names
    def _run_sql(self, proc_name: str) -> int:
        # Call stored procedure with one OUT parameter for rows inserted, return that count
        with self.conn.cursor() as cur:
            args = cur.callproc(proc_name, [0]) # Placeholder for OUT parameter
            rows_inserted = args[0] or 0        # OUT Parameter is now filled
            print(f"{proc_name}: {rows_inserted} rows")
            return rows_inserted

    def run_all(self) -> dict:
        row_counts = {}
        try:
            self.conn.start_transaction()
            for proc in self.procedures:
                row_counts[proc] = self._run_sql(proc)

            self.conn.commit()
            print('ETL Finished successfully')
        except Exception as e:
            self.conn.rollback()
            print(f"Step '{proc}' failed, rolled back: {e}")
            raise
        finally:
            self.conn.close()

        return row_counts
    
