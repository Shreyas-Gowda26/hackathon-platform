-- Run on existing hackathon_db if JudgeAssignments is missing
USE hackathon_db;

CREATE TABLE IF NOT EXISTS JudgeAssignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    judge_id INT NOT NULL,
    team_id INT NOT NULL,
    UNIQUE KEY unique_judge_team (judge_id, team_id),
    FOREIGN KEY (judge_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (team_id) REFERENCES Teams(team_id) ON DELETE CASCADE
);
