document.addEventListener('DOMContentLoaded', function () {
    const select = document.getElementById('pj_filter');
    const tbody = document.querySelector('#FatsTable tbody');
    const span = document.getElementById('FatsPJ');

    select.addEventListener('change', function () {
        
        const filtro = this.value.trim();
        const filas = tbody.querySelectorAll('tr');
        let count = 0;

        filas.forEach(fila => {
            const pj = fila.cells[5].textContent.trim(); // Columna "PJ"
            if (filtro === '' || pj === filtro) {
                fila.style.display = '';
                count++;
            } else {
                fila.style.display = 'none';
            }
        })
        if (filtro != ''){
            span.textContent = `Flotas con ${select.value}: ${count}`;
        }else{
            span.textContent = ``;
        }
        
    })
});