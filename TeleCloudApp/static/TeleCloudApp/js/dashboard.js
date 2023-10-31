const nav = document.querySelector(".nav");
const rightBar = document.querySelector(".right-bar");
const mainContainer = document.querySelector(".main-container");
const folderAdd = document.querySelector(".folder-add");
const folder = document.querySelector(".folder");
// mainContainer.style.marginLeft = nav.style.width;

mainContainer.style.marginLeft = getComputedStyle(nav).width;

if(rightBar) {
mainContainer.style.marginRight = getComputedStyle(rightBar).width;
}

if(folderAdd && folder) {
    folderAdd.style.height = getComputedStyle(folder).height;

} 