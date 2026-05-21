CREATE TABLE IF NOT EXISTS GlobalStats (
    stats_id INT PRIMARY KEY,
    metric_name VARCHAR(50) PRIMARY KEY,
    metric_value INT NOT NULL DEFAULT 0
);

-- Εισαγωγή των αρχικών δεδομένων (Seed Data)
INSERT IGNORE INTO GlobalStats (metric_name, metric_value) VALUES 
('total_reservations', 0),
('total_cancellations', 0);