document.getElementById("addRPerson").onclick = function () {

    var name  = document.createElement('p')
    name.innerText = 'имя'
    var appointment  = document.createElement('p')
    appointment.innerText = 'должность'

    var petCell = document.getElementById("rperson_div");
    var input_1 = document.createElement("input");
    input_1.type = "text";
    input_1.name = "rperson_name" + counter;
    var br = document.createElement("br");
    petCell.appendChild(name);
    petCell.appendChild(input_1);
    petCell.appendChild(br);

    var input_2 = document.createElement("input");
    input_2.type = "text";
    input_2.name = "appointment" + counter;
    petCell.appendChild(appointment);
    petCell.appendChild(input_2);
    petCell.appendChild(br);
    counter++;
}

var counter = 0




