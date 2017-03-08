/*TODO: Add some constraints */

CREATE TABLE IF NOT EXISTS experiment (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    datetime    INTEGER,
    x           REAL,
    y           REAL,
    x_hat       REAL DEFAULT 0,
    y_hat       REAL DEFAULT 0,

    /* Describe experiment */
    comment     text
);

/* Microphone array */
CREATE TABLE IF NOT EXISTS array (
    experiment_id INTEGER,
    array_id      INTEGER,
    x             REAL,
    y             REAL,

    /* Polar position estimate of sound source (NB: r is typically very bad) */
    r             REAL,
    theta         REAL,
    PRIMARY KEY   (experiment_id, array_id)
);

/* Microphone (3 per array, 6 per experiment for 2D) */
CREATE TABLE IF NOT EXISTS mic (
    experiment_id   INTEGER,
    array_id        INTEGER,
    mic_id          INTEGER,
    data            BLOB, /* CSV */

    FOREIGN KEY     (experiment_id, array_id) REFERENCES array(experiment_id, array_id)
    PRIMARY KEY     (experiment_id, array_id, mic_id)
);

/* Microphone pair */
CREATE TABLE IF NOT EXISTS mic_pair(
    experiment_id   INTEGER,
    array_id        INTEGER,
    mic_1           INTEGER,
    mic_2           INTEGER,
    delay           REAL,       /* Relative delay of mic_2 to mic_1  */

    FOREIGN KEY     (experiment_id, array_id) REFERENCES array(experiment_id, array_id)
    FOREIGN KEY     (mic_1) REFERENCES mic(mic_id)
    FOREIGN KEY     (mic_2) REFERENCES mic(mic_id)
    PRIMARY KEY     (experiment_id, array_id, mic_1, mic_2)
);
