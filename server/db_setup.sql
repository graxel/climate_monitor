CREATE TABLE IF NOT EXISTS webpage_plot_data (
    obs_time                    TIMESTAMP NOT NULL,
    sensor__bedroom_hum         REAL,
    sensor__bedroom_temp        REAL,
    sensor__closet_hum          REAL,
    sensor__closet_temp         REAL,
    sensor__kitchen_hum         REAL,
    sensor__kitchen_temp        REAL,
    sensor__office_hum          REAL,
    sensor__office_temp         REAL,
    PRIMARY KEY (obs_time)
);

CREATE INDEX IF NOT EXISTS idx_observations_sensor_id ON observations (sensor_id);


CREATE TABLE update_status (
    table_name TEXT,
    sensor_id  TEXT,
    last_updated TIMESTAMP,
    PRIMARY KEY (table_name, sensor_id)
);

