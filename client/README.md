# Python Client for Beaglebone Server

python client for Beaglebone server.

## Monitoring

Monitoring uses pyaudio, callbacks attached to the monitor which loops
until trigger activated (currently a threshold)

## Database

Uses sqlite3. See ./schema/create.sql for schema.
Creating db:
    sqlite3 test.db
    .read create.sql

Useful dot commands (proper formating):
    .header on
    .mode columns

NB: Currently client only supports `test.db` as database name in current path!

## TODO

- Config file specifying (x, y) position of each array
- Config for db to use in client
- Add Jupyter notebook support
- Clean up db layer (also add queries)
- Enable multi-array support
- Tests
