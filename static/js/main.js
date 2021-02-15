// Create Elements of an answer, out of the DOM.
const answer = document.getElementsByClassName("answer")[0];
const mapDiv = document.getElementById("map");
const mapCode = document.getElementsByClassName("map-code")[0];
const questions = document.getElementsByClassName("questions")[0];

var loading = document.createElement("img");
loading.classList.add("loading");
loading.src = "/static/loading.webp";


// Start search
const button = document.getElementsByClassName("button")[0];
button.addEventListener('click', search)

function search(event){
    event.preventDefault();

    var form = document.getElementsByClassName("form-text")[0].value;
    console.log(form);

    answer.appendChild(loading);

    var counter = 0;
    const specialCar = "<>$%{}[]`|~^*";
    for (let s of specialCar) {
        if (form.includes(s)){
            counter = 1;
            break;
        }
    }
    if (counter == 1){
        downloadAns(form, "shdhfhfg");
    } else {
        downloadAns(form, form);
    }
}

function downloadAns(question, form){
    // Fetch answer onto the server
    fetch(`http://ocgrandpy.herokuapp.com/question`, {
        method: 'POST',
        body: form
    })
    .then(res => res.json())
    .then(info => insertAns(question, info));
}


function insertAns(form, info){
    answer.removeChild(loading);

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

    short.innerHTML = info.short;
    long.innerHTML = info.long;
    link.innerHTML = info.link.text;
    link.href = info.link.href;
    quesText.innerHTML = form;
    createMap(info.position, 14);
    if (window.screen.width >= 992){
        answer.appendChild(ansText);
    }
    else {
        questions.appendChild(ansText);
    }
}

function createMap(center, zoom){
    console.log(center)
    var map = new google.maps.Map(mapDiv, {
        zoom: zoom,
        center: center
    })
    var marker = new google.maps.Marker({
        position: center,
        map: map
    })
}

function initMap(){
    createMap({lat:0, lng:0}, 0)
}