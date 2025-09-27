document.addEventListener("DOMContentLoaded", () =>{
    const input = document.getElementById("candidateTable_filter")
    const tbody = document.querySelector('#candidateTable tbody');


    input.addEventListener("input", () => {
        const filtro = input.value.toLowerCase().trim()
        const filas = tbody.querySelectorAll('tr');

        filas.forEach(fila => {
            const nombre = fila.querySelector("td:first-child").innerText.toLowerCase();
            fila.style.display = nombre.includes(filtro) ? "" : "none";
        });
    })
})