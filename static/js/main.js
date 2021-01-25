var answer = document.getElementsByClassName("answer")[0];

// Create Elements of an answer, out of the DOM.
var ansText = document.createElement("span");
ansText.classList.add("ans-text");

var short = document.createElement("p");
short.classList.add("short");
var long = document.createElement("p");
long.classList.add("long");
var link = document.createElement("a");
link.classList.add("link");

ansText.appendChild(short);
ansText.appendChild(long);
ansText.appendChild(link);

var ansMap = document.createElement("span");
ansMap.classList.add("ans-map");

// Reveal search results.
function search(event){
    event.preventDefault();
    let question = document.getElementsByClassName("question")[0].value;
    if (question == "Salut GrandPy ! Est-ce que tu connais l'adresse d'OpenClassrooms ?"){
        short.innerHTML = "Bien sûr mon poussin ! La voici : 7 cité Paradis, 75010 Paris.";
        long.innerHTML = "Mais t'ai-je déjà raconté l'histoire de ce quartier qui m'a vu en culottes courtes ? La cité Paradis est une voie publique située dans le 10e arrondissement de Paris. Elle est en forme de té, une branche débouche au 43 rue de Paradis, la deuxième au 57 rue d'Hauteville et la troisième en impasse.";
        link.innerHTML = "[En savoir plus sur Wikipedia]";
        link.href = "https://fr.wikipedia.org/wiki/Cit%C3%A9_Paradis";
        answer.appendChild(ansText);

        ansMap.innerHTML = "Ceci est une carte.";
        answer.appendChild(ansMap);
    }

}

const button = document.getElementsByClassName("button")[0];
button.addEventListener('click', search);