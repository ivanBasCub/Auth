document.addEventListener("DOMContentLoaded", () =>{
    const input = document.getElementById("fitTable_filter")
    const filas = document.querySelectorAll("#fitTable tbody tr");

    input.addEventListener("input", () => {
        const filtro = input.value.toLowerCase().trim()

        filas.forEach(fila => {
            const nombre = fila.querySelector("td:nth-child(2)").innerText.toLowerCase();
            fila.style.display = nombre.includes(filtro) ? "" : "none";
        });
    })
})