document.addEventListener('DOMContentLoaded', () => {
    const select = document.getElementById("user");
    
    select.addEventListener('change', () => {
        const user_id = select.value.trim()
        const elements = document.querySelectorAll(`.user-${user_id}`)

        document.querySelectorAll('.char').forEach(el => { el.style.display = 'none'; });

        elements.forEach(el => {
            el.style.display = 'block';
        })
    })
})