CREATE TABLE players (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    player_id INT NOT NULL,
    player_score INT,
    dealer_score INT,
    result VARCHAR(10),
    timestamp DATETIME,
    FOREIGN KEY (player_id) REFERENCES players(id)
);
