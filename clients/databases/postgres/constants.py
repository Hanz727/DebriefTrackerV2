DB_FETCH_QUERY = '''
SELECT 
    "DATE", "FL_NAME", "SQUADRON", "RIO_NAME", "PLT_NAME", "TAIL_NUMBER", 
    "WEAPON_TYPE", "WEAPON", "TARGET", "TARGET_ALT", "OWN_ALT", "SPEED", 
    "RANGE", "HIT", "DESTROYED", "QTY", "MSN_NR", "MSN_NAME", "EVENT", "NOTES", "ID"
FROM public.debriefs
ORDER BY "ID" ASC;
'''

DB_INSERT_QUERY = '''
            INSERT INTO debriefs (
        	"DATE", "FL_NAME", "SQUADRON", "RIO_NAME", "PLT_NAME", "TAIL_NUMBER", "WEAPON_TYPE", "WEAPON", "TARGET", 
        	"TARGET_ALT", "OWN_ALT", "SPEED", "RANGE", "HIT", "DESTROYED", "QTY", "MSN_NR", "MSN_NAME", "EVENT", "NOTES"
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            );
            '''