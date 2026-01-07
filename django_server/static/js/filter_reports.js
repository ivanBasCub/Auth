
document.addEventListener("DOMContentLoaded", () => {
    const rows_main = document.querySelectorAll('#table_main > tbody > tr');
    const main_input = document.getElementById("filter_main")
    
    main_input.addEventListener("input", () => {
        const filtro = main_input.value.toLowerCase().trim()

        rows_main.forEach(fila => {
            const nombre = fila.querySelector("td:first-child").innerText.toLowerCase();
            fila.style.display = nombre.includes(filtro) ? "" : "none";
        })

    })
})

