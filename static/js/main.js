// Create Elements of an answer, out of the DOM.
const answer = document.getElementsByClassName("answer")[0];
const map = document.getElementsByClassName("map")[0];
const questions = document.getElementsByClassName("questions")[0];

var loading = document.createElement("img");
loading.classList.add("loading");
loading.src = "/static/loading.webp";


// Start search
const button = document.getElementsByClassName("button")[0];
button.addEventListener('click', search);

function search(event){
    event.preventDefault();
    var form = document.getElementsByClassName("form-text")[0].value;
    if (form == "Salut GrandPy ! Est-ce que tu connais l'adresse d'OpenClassrooms ?"){
        scriptReq();
    } else {
        req(form);
    }
}

function scriptReq(){
    // Canonical question and canonical answer.
    var reqAns = {
        question: "Salut GrandPy ! Est-ce que tu connais l'adresse d'OpenClassrooms ?",
        short:  "Bien sûr mon poussin ! La voici : 7 cité Paradis, 75010 Paris.",
        long: "Mais t'ai-je déjà raconté l'histoire de ce quartier qui m'a vu en culottes courtes ? La cité Paradis est une voie publique située dans le 10e arrondissement de Paris. Elle est en forme de té, une branche débouche au 43 rue de Paradis, la deuxième au 57 rue d'Hauteville et la troisième en impasse.",
        link: {
            text: "[En savoir plus sur Wikipedia]",
            href: "https://fr.wikipedia.org/wiki/Cit%C3%A9_Paradis"
        },
        map: "Ceci est une carte"
    };
    insertAns(reqAns);
}

function req(form){
    answer.appendChild(loading);
    // Fetch answer onto the server
    var request = new XMLHttpRequest();
    request.open("GET", `http://127.0.0.1:8080/question/${form}`);
    request.send();

    request.onreadystatechange= function () {
        if (this.readyState == XMLHttpRequest.DONE && this.status == 200){
            answer.removeChild(loading);
            reqAns = JSON.parse(request.responseText);
            reqAns.question = form
            insertAns(reqAns);
        }
    };
}


function insertAns(reqAns){
    // Display answer

    var ansText = document.createElement("div");
    ansText.classList.add("text", "row", "to-right");
    var short = document.createElement("p");
    short.classList.add("short");
    var long = document.createElement("p");
    long.classList.add("long");
    var link = document.createElement("a");
    link.classList.add("link");

    var quesText = document.createElement("div");
    quesText.classList.add("text", "row");
    questions.appendChild(quesText);

    ansText.appendChild(short);
    ansText.appendChild(long);
    ansText.appendChild(link);

    short.innerHTML = reqAns.short;
    long.innerHTML = reqAns.long;
    link.innerHTML = reqAns.link.text;
    link.href = reqAns.link.href;
    quesText.innerHTML = reqAns.question;
    map.innerHTML = reqAns.map;
    if (window.screen.width >= 992){
        answer.appendChild(ansText);
    }
    else {
        questions.appendChild(ansText);
    }
}
