
var has_ended = false;
var user_id = null;
var word_match = false;
var letter_colors = "#####";

let guessedWords = [[]];
let availableSpace = 1;

let word;
let guessedWordCount = 0;

var regex = /^[a-z]+$/

var hold_input = false;

var letter_set = new Set();

var keys = null;

var grey_rgb = "rgb(58, 58, 60)";
var green_rgb = "rgb(83, 141, 78)";
var yellow_rgb ="rgb(181, 159, 59)";

function getServerAddress(end_str){
  address = "http://" + server_ip + ":" + server_port + "/" + end_str;
  console.log(address);
  return address;
}

function getNewWord() {
  console.log("client getting new word");
  user_id = null;

  fetch(
    getServerAddress(`wordle`),
    {
      method: "POST",
      headers: {"Content-type": "application/json"},
    }).then((response) => {
        return response.json();
    }).then((res) => {
      user_id = res.userid;
      console.log("userid response was:", user_id);
    }).catch((err) => {
        console.error(err);
    });
}

function getCurrentWordArr() {
  const numberOfGuessedWords = guessedWords.length;
  return guessedWords[numberOfGuessedWords - 1];
}

function updateGuessedWords(letter) {
  const currentWordArr = getCurrentWordArr();

  if (currentWordArr && currentWordArr.length < 5) {
    currentWordArr.push(letter);

    const availableSpaceEl = document.getElementById(String(availableSpace));

    availableSpace = availableSpace + 1;
    availableSpaceEl.textContent = letter;
  }
}

function getTileColor(letter, index) {

  if (letter_colors.charAt(index) == '#') {
    return grey_rgb;
  }
  if (letter_colors.charAt(index) == '*') {
    return green_rgb;
  }
  return yellow_rgb;
}

function handleSubmitWord() {
  const currentWordArr = getCurrentWordArr();
  if (currentWordArr.length !== 5) {
    window.alert("Word must be 5 letters");
    return false;
  }
  if(user_id == null){
    window.alert("Waiting for serve to generate user id, try again");
    return false;
  }
  const currentWord = currentWordArr.join("");
  hold_input = true;
  fetch(
      getServerAddress(`wordle?userid=` + user_id + `&word=` + currentWord), {
      method: "GET",
      headers: {"Content-type": "application/x-www-form-urlencoded"},
    }).then((response) => {
      if (!response.ok) {
        throw Error();
      }
      return response.json();
    }).then((res) => {
      word_match = JSON.parse(res).word_match;
      letter_colors = JSON.parse(res).letter_colors;
      let used = JSON.parse(res).used;
      let return_word = JSON.parse(res).return_word;

      if(used === true){
        window.alert("Word already entered");
        return false;
      }

      const firstLetterId = guessedWordCount * 5 + 1;
      const interval = 200;
      currentWordArr.forEach((letter, index) => {
        setTimeout(() => {
          const tileColor = getTileColor(letter, index);

          const letterId = firstLetterId + index;
          const letterEl = document.getElementById(letterId);
          letterEl.classList.add("animate__flipInX");
          letterEl.style = `background-color:${tileColor};border-color:${tileColor}`;
        }, interval * index);
      });

      changeKeyboardColors(currentWord, letter_colors);

      guessedWordCount += 1;

      if(word_match == true) {
        window.alert("Congratulations!");
        return false;
      }

      if (word_match == false && guessedWords.length === 6) {
        window.alert(`Sorry, you have no more guesses!`);
        window.alert(`The word is ${return_word}.`);
        has_ended = true;
        return false;
      }

      guessedWords.push([]);
      return true;
      
    })
    .catch((err) => {
      console.log(err);
      window.alert("Word is not recognised!");
      return false;
    }).finally((r)=>{
      hold_input = false;
    });
}

function createSquares() {
  const gameBoard = document.getElementById("board");

  for (let index = 0; index < 30; index++) {
    let square = document.createElement("div");
    square.classList.add("square");
    square.classList.add("animate__animated");
    square.setAttribute("id", index + 1);
    gameBoard.appendChild(square);
  }
}

function changeKeyboardColors(currentWord, letter_colors){
  let color = green_rgb;
  for(let i=0; i<5; i++){
    let letter = currentWord.charAt(i);
    if(letter_colors.charAt(i) == '*'){ // green
      color = green_rgb;
    }
    else if(letter_colors.charAt(i) == '^'){  // yellow
      color = yellow_rgb;
    }
    else{ // grey
      color = grey_rgb;
    }
    if(letter_set.has(letter)===false){
      for (let i = 0; i < keys.length; i++) {
        let key = keys[i];
        if(key.getAttribute("data-key")== letter){
          key.style = `background-color:${color};border-color:${color}`;
        }
      }
      letter_set.add(letter);
    }
  }

}

function handleDeleteLetter() {
  const currentWordArr = getCurrentWordArr();
  if(currentWordArr.length > 0){
    const removedLetter = currentWordArr.pop();
    guessedWords[guessedWords.length - 1] = currentWordArr;
    const lastLetterEl = document.getElementById(String(availableSpace - 1));
    lastLetterEl.textContent = "";
    availableSpace = availableSpace - 1;
  }
}

function setLetter(letter){
  if(word_match === false && has_ended === false && hold_input == false){
    if (letter === "enter")handleSubmitWord();
    else if (letter === "del") handleDeleteLetter();
    else updateGuessedWords(letter);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  createSquares();
  getNewWord();
  keys = document.querySelectorAll(".keyboard-row button");
  for (let i = 0; i < keys.length; i++) {
    keys[i].onclick = ({ target }) => {
      const letter = target.getAttribute("data-key");
      setLetter(letter);
    };
  }
});

document.addEventListener('keydown', function(event) {
  if(regex.test(event.key) == true) {
    setLetter(event.key);
  }
  else if(event.key === 'Enter'){
    setLetter('enter');
  }
  else if(event.key === 'Backspace'){
    setLetter('del');
  }
});