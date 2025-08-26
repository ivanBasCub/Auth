document.addEventListener("DOMContentLoaded", () =>{
    const input = document.getElementById("docTable_filter")
    const select =document.getElementById("docTable_rango_filter")
    const tbody = document.querySelector('#docTable tbody');


    input.addEventListener("input", () => {
        const filtro = input.value.toLowerCase().trim()
        const filas = tbody.querySelectorAll('tr');

        filas.forEach(fila => {
            const nombre = fila.querySelector("td:first-child").innerText.toLowerCase();
            fila.style.display = nombre.includes(filtro) ? "" : "none";
        });
    })

    select.addEventListener('change', function () {
        const filtro = this.value.trim();
        const filas = tbody.querySelectorAll('tr');

        filas.forEach(fila => {
            const categoria = fila.cells[1].textContent.trim(); 
            if (filtro === '' || categoria === filtro) {
                fila.style.display = '';
            } else {
                fila.style.display = 'none';
            }
        });
    });

})