const editBtnName = document.querySelector('.edit-btn-name');
const editBtnEmail = document.querySelector('.edit-btn-email');
const editBtnPhone = document.querySelector('.edit-btn-phone');
const overlayForm = document.querySelector('.overlay-form');
const overlayFormName = document.querySelector('.overlay-form-name');
const overlayFormEmail = document.querySelector('.overlay-form-email');
const overlayFormPhone = document.querySelector('.overlay-form-phone');
const inputFormName = overlayFormName.querySelector('.input-form-name')
const iconCrossName = overlayFormName.querySelector('.icon-cross-wrapper');
const iconCrossEmail = overlayFormEmail.querySelector('.icon-cross-wrapper');
const iconCrossPhone = overlayFormPhone.querySelector('.icon-cross-wrapper');

const nameProfile = document.querySelector('.name-profile');

inputFormName.value = nameProfile.textContent.trim();


editBtnName.addEventListener('click', () => {
    overlayFormName.classList.add('display-f');
    inputFormName.select();
});

iconCrossName.addEventListener('click', () => {
    overlayFormName.classList.remove('display-f');
});

editBtnEmail.addEventListener('click', () => {
    overlayFormEmail.classList.add('display-f');
});

iconCrossEmail.addEventListener('click', () => {
    overlayFormEmail.classList.remove('display-f');
});

editBtnPhone.addEventListener('click', () => {
    overlayFormPhone.classList.add('display-f');
});

iconCrossPhone.addEventListener('click', () => {
    overlayFormPhone.classList.remove('display-f');
});
