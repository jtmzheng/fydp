import sqlite3
import time

#TODO: Clean up this code lol
conn = sqlite3.connect('./schema/test.db')

def with_cursor(func):
    """Decorator to inject transaction into each query
    """
    def query(*args, **kwargs):
        """http://stackoverflow.com/a/19522634
        """
        with conn:
            return func(conn.cursor(), *args, **kwargs)
    return query

@with_cursor
def create_experiment(cur):
    try:
        cur.execute('INSERT INTO experiment(datetime) VALUES (:datetime)',
            {'datetime': int(time.time())})
        return cur.lastrowid
    except sqlite3.IntegrityError as s:
        print 'Error creating experiment: %s' % s.message
        raise s

@with_cursor
def create_array(cur, exp_id, arr_id, x, y):
    try:
        cur.execute('INSERT INTO array VALUES(:exp_id, :arr_id, :x, :y)',
            {'exp_id': exp_id, 'arr_id': arr_id, 'x': x, 'y': y})
        return cur.lastrowid
    except sqlite3.IntegrityError as s:
        print 'Error creating array: %s' % s.message
        raise s

@with_cursor
def create_mic(cur, exp_id, arr_id, mic_id, data, delay):
    try:
        cur.execute('INSERT INTO mic VALUES(:exp_id, :arr_id, :mic_id, :data, :delay)',
            {'exp_id': exp_id, 'arr_id': arr_id, 'mic_id': mic_id, 'data': data, 'delay': delay})
        return cur.lastrowid
    except sqlite3.IntegrityError as s:
        print 'Error creating mic : %s' % s.message
        raise s


if __name__ == '__main__':
    exp_id = create_experiment()
    print 'Experiment ID: %s' % str(exp_id)
    array = create_array(exp_id, 1, 0.1, 0.2)
    print 'Array ID: %s' % str(array)
    mic = create_mic(exp_id, 1, 0, 'Testing data', 0.123)
    print 'Mic ID: %s' % str(mic)
