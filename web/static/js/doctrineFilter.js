document.addEventListener("DOMContentLoaded", () =>{
    const input = document.getElementById("docTable_filter")
    const filas = document.querySelectorAll("#docTable tbody tr");

    input.addEventListener("input", () => {
        const filtro = input.value.toLowerCase().trim()

        filas.forEach(fila => {
            const nombre = fila.querySelector("td:first-child").innerText.toLowerCase();
            fila.style.display = nombre.includes(filtro) ? "" : "none";
        });
    })
})