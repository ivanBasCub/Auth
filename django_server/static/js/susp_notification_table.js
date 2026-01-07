document.addEventListener('DOMContentLoaded', function () {
    const select = document.getElementById('suspiciuos_table_filter_pj');
    const tbody = document.querySelector('#suspiciuos_table tbody');

    select.addEventListener('change', function () {
        const filtro = this.value.trim();
        const filas = tbody.querySelectorAll('tr');

        filas.forEach(fila => {
            const categoria = fila.cells[0].textContent.trim();
            if (filtro === '' || categoria === filtro) {
                fila.style.display = '';
            } else {
                fila.style.display = 'none';
            }
        });
    });

});