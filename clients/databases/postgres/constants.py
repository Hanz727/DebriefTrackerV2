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

DB_UPDATE_QUERY = '''
            UPDATE debriefs SET
                "DATE" = %s,
                "FL_NAME" = %s,
                "SQUADRON" = %s,
                "RIO_NAME" = %s,
                "PLT_NAME" = %s,
                "TAIL_NUMBER" = %s,
                "WEAPON_TYPE" = %s,
                "WEAPON" = %s,
                "TARGET" = %s,
                "TARGET_ALT" = %s,
                "OWN_ALT" = %s,
                "SPEED" = %s,
                "RANGE" = %s,
                "HIT" = %s,
                "DESTROYED" = %s,
                "QTY" = %s,
                "MSN_NR" = %s,
                "MSN_NAME" = %s,
                "EVENT" = %s,
                "NOTES" = %s
            WHERE "ID" = %s;
            '''