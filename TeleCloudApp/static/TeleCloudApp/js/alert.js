const body = document.querySelector("body");

const newToast = document.createElement("div");
newToast.classList.add("alert");
newToast.innerHTML = `

<div class="title-alert">
Alert Title
</div>
<div class="msg-alert">
Lorem ipsum dolor, sit amet consectetur adipisicing elit.
</div>

`;

body.appendChild(newToast);

const alert = document.querySelector(".alert");
const tilteAlert = document.querySelector(".title-alert");
const msgAlert = document.querySelector(".msg-alert");

alert.style.opacity = 0;

function toast(alertTitle, alertMsg, msgClr) {
    tilteAlert.innerText = alertTitle;
    
    msgAlert.innerText = alertMsg;

    if(msgClr === "red") {
        msgAlert.classList.add("clr-general-red-400")
    } else if(msgClr === "green") {
        msgAlert.classList.add("clr-general-green-400")
    } else if(msgClr === "yellow") {
        msgAlert.classList.add("clr-general-yellow-400")
    } else if(msgClr === "blue") {
        msgAlert.classList.add("clr-general-blue-400")
    } else {
        msgAlert.classList.add("clr-general-yellow-400")
    }

    alert.style.opacity = 1;

    setTimeout(function(){
        alert.style.opacity = 0;
        let classes = msgAlert.className.split(" ");
        let firstClass = classes[0];
        msgAlert.className = firstClass;
    }, 4000);
};
