// script.js

function editRow(button) {
    var row = button.parentNode.parentNode;
    var cells = row.getElementsByTagName("td");
    
    for (var i = 0; i < cells.length - 1; i++) {
        var input = document.createElement("input");
        input.value = cells[i].innerHTML;
        cells[i].innerHTML = "";
        cells[i].appendChild(input);
    }
    
    var saveButton = document.createElement("button");
    saveButton.innerHTML = "Сохранить";
    saveButton.onclick = function() { saveRow(button); };
    button.disabled = true;
    button.parentNode.insertBefore(saveButton, button);
}


function saveRow(button) {
    var row = button.parentNode.parentNode;
    var cells = row.getElementsByTagName("td");
    
    for (var i = 0; i < cells.length - 1; i++) {
        var input = cells[i].getElementsByTagName("input")[0];
        cells[i].innerHTML = input.value;
    }
    
    button.disabled = false;
    button.parentNode.removeChild(button.previousSibling);
}

function deleteRow(button) {
    var row = button.parentNode.parentNode;
    row.parentNode.removeChild(row);
}

function addRow() {
    var table = document.getElementsByTagName("table")[0];
    var newRow = table.insertRow(table.rows.length - 1);

    var fioCell = newRow.insertCell(0);
    var loginCell = newRow.insertCell(1);
    var gradeCell = newRow.insertCell(2);
    var locationCell = newRow.insertCell(3);
    var actionCell = newRow.insertCell(4);

    var fioInput = document.createElement("input");
    fioCell.appendChild(fioInput);

    var loginInput = document.createElement("input");
    loginCell.appendChild(loginInput);

    var gradeInput = document.createElement("input");
    gradeCell.appendChild(gradeInput);

    var locationInput = document.createElement("input");
    locationCell.appendChild(locationInput);

    var saveButton = document.createElement("button");
    saveButton.innerHTML = "Сохранить";
    saveButton.onclick = function() { saveNewRow(newRow); };
    actionCell.appendChild(saveButton);

    // Add back the buttons
    var editButton = document.createElement("button");
    editButton.innerHTML = "Редактировать";
    editButton.onclick = function() { editRow(editButton); };
    actionCell.appendChild(editButton);

    var deleteButton = document.createElement("button");
    deleteButton.innerHTML = "Удалить";
    deleteButton.onclick = function() { deleteRow(deleteButton); };
    actionCell.appendChild(deleteButton);
}

function saveNewRow(row) {
    var cells = row.getElementsByTagName("td");

    for (var i = 0; i < cells.length - 1; i++) {
        var input = cells[i].getElementsByTagName("input")[0];
        cells[i].innerHTML = input.value;
    }

    // Delete the buttons cell
    cells[cells.length - 1].remove();

    // Add back the buttons
    var editButton = document.createElement("button");
    editButton.innerHTML = "Редактировать";
    editButton.onclick = function() { editRow(editButton); };
    cells[cells.length - 1].appendChild(editButton);

    var deleteButton = document.createElement("button");
    deleteButton.innerHTML = "Удалить";
    deleteButton.onclick = function() { deleteRow(deleteButton); };
    cells[cells.length - 1].appendChild(deleteButton);
}

function cancelNewRow(row) {
    row.parentNode.removeChild(row);
}
