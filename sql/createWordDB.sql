CREATE DATABASE wordDB;
USE wordDB;
CREATE TABLE wordList (words varchar(5));
LOAD DATA INFILE "sgb-words.txt" INTO TABLE wordList;
ALTER TABLE wordList ADD PRIMARY KEY (words);

CREATE TABLE game (userId varchar(36),
	firstGuess varchar(5),
	secondGuess varchar(5),
	thirdGuess varchar(5),
	fourthGuess varchar(5),
	fifthGuess varchar(5),
	sixthGuess varchar(5),
	word varchar(5),
