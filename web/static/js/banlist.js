document.addEventListener('DOMContentLoaded', function () {
    const select = document.getElementById('banlist_category');
    const tbody = document.querySelector('#banlist tbody');

    select.addEventListener('change', function () {
        const filtro = this.value.trim();
        const filas = tbody.querySelectorAll('tr');

        filas.forEach(fila => {
            const categoria = fila.cells[2].textContent.trim(); // Columna "Categoria"
            if (filtro === '' || categoria === filtro) {
                fila.style.display = '';
            } else {
                fila.style.display = 'none';
            }
        });
    });

});