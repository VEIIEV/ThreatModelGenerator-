const checkboxGroup = document.querySelectorAll('input[name="options"]');
const form = document.querySelector('form');

form.addEventListener('submit', function(event) {
  let isChecked = Array.from(checkboxGroup).some(checkbox => checkbox.checked);
  checkboxGroup[0].setCustomValidity(isChecked ? "" : "Необходимо выбрать хотя бы один вариант.");

  if (!form.checkValidity()) {
    event.preventDefault();
  }
});