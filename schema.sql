CREATE TABLE RSPUsers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE RSPEquipment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT, 
    shoe VARCHAR(100),
    brand VARCHAR(50),
    miles FLOAT DEFAULT 0,
    model VARCHAR(100),
    retired BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES RSPUsers(id)
);

CREATE TABLE RSPWorkouts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    date DATE,
    type VARCHAR(50),
    duration INT,
    distance FLOAT,
    notes TEXT,
    equipment_id INT,
    complete BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES RSPUsers(id),
    FOREIGN KEY (equipment_id) REFERENCES RSPEquipment(id)
);

CREATE TABLE RSPRaces (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    title VARCHAR(150),
    date DATE,
    location VARCHAR(150),
    notes TEXT,
    FOREIGN KEY(user_id) REFERENCES RSPUsers(id)
);