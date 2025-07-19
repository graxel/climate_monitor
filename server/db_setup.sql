CREATE TABLE IF NOT EXISTS hist_10m (
    sensor_id   VARCHAR(64) NOT NULL,
    obs_time    TIMESTAMP NOT NULL,
    temp        REAL,
    hum         REAL,
    PRIMARY KEY (sensor_id, obs_time)
);

CREATE INDEX IF NOT EXISTS idx_observations_sensor_id ON observations (sensor_id);