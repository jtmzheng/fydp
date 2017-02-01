/*TODO: Add some constraints */

CREATE TABLE IF NOT EXISTS experiment (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    datetime    INTEGER
);

/* Microphone array */
CREATE TABLE IF NOT EXISTS array (
    experiment_id INTEGER,
    array_id      INTEGER,
    x             REAL,
    y             REAL,
    PRIMARY KEY   (experiment_id, array_id)
);

/* Microphone (3 per array, 6 per experiment for 2D) */
CREATE TABLE IF NOT EXISTS mic (
    experiment_id   INTEGER,
    array_id        INTEGER,
    mic_id          INTEGER,
    data            BLOB, /* CSV */
    delay           REAL, /* relative delay, 1 mic will have a delay of 0 for ach array */

    FOREIGN KEY     (experiment_id, array_id) REFERENCES array(experiment_id, array_id)
    PRIMARY KEY     (experiment_id, array_id, mic_id)
);
