window.onload = function () {
    for (let i = 1; i < 5; i++) {
        i = i.toString()
        document.getElementById(i).addEventListener("change", function () {
            if (this.checked) {
                // получить все id которые оканчиваются на type{{i}}
                let selector = "[id*='type" + i.toString() + "']"
                let elements = document.querySelectorAll(selector);
                for (let j = 0; j < elements.length; j++) {
                    document.getElementById(elements[j].id).disabled = false;
                }
            } else {
                let selector = "[id*='type" + i.toString() + "']"
                let elements = document.querySelectorAll(selector);
                for (let j = 0; j < elements.length; j++) {
                document.getElementById(elements[j].id).checked = false;
                document.getElementById(elements[j].id).disabled = true;
                }
            }
        });

    }
}