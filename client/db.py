import sqlite3
import time
import io
import numpy as np

def adapt_array(arr):
    """
    http://stackoverflow.com/a/31312102/190597 (SoulNibbler)
    NB: np.save(out, arr) would save the file in npy format (with a variable length
    header which is too annoying to parse
    """
    out = io.BytesIO()
    out.write(arr.tobytes())
    out.seek(0)
    return sqlite3.Binary(out.read())

def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)

# Converts np.array to TEXT when inserting
sqlite3.register_adapter(np.ndarray, adapt_array)

# Converts TEXT to np.array when selecting
sqlite3.register_converter("array", convert_array)

#TODO: Clean up this code lol
conn = sqlite3.connect('./schema/test.db', detect_types=sqlite3.PARSE_DECLTYPES)

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
def create_experiment(cur, src_x, src_y):
    try:
        cur.execute('INSERT INTO experiment(datetime, x, y) VALUES (:datetime, :x, :y)',
            {'datetime': int(time.time()), 'x': src_x, 'y': src_y})
        return cur.lastrowid
    except sqlite3.IntegrityError as s:
        print 'Error creating experiment: %s' % s.message
        raise s

@with_cursor
def create_array(cur, exp_id, arr_id, x, y, r, theta):
    try:
        cur.execute('INSERT INTO array VALUES(:exp_id, :arr_id, :x, :y, :r, :theta)',
            {'exp_id': exp_id, 'arr_id': arr_id, 'x': x, 'y': y, 'r': r, 'theta': theta})
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

@with_cursor
def get_mic_data(cur, exp_id, arr_id, mic_id):
    try:
        return cur.execute('SELECT data FROM mic WHERE experiment_id=:exp_id AND array_id=:arr_id AND mic_id=:mic_id',
            {'exp_id': exp_id, 'arr_id': arr_id, 'mic_id': mic_id}).fetchone()
    except sqlite3.IntegrityError as s:
        print 'Error getting mic data : %s' % s.message
        raise s


if __name__ == '__main__':
    exp_id = create_experiment()
    print 'Experiment ID: %s' % str(exp_id)
    array = create_array(exp_id, 1, 0.1, 0.2)
    print 'Array ID: %s' % str(array)
    mic = create_mic(exp_id, 1, 0, 'Testing data', 0.123)
    print 'Mic ID: %s' % str(mic)
