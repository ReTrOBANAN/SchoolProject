adminForm = document.getElementById('adminForm')

adminForm.addEventListener('submit', async (e) => {
    e.preventDefault()


    const adminForm = new FormData(e.target)
    const response = await fetch("/admin/add", {
        method: "POST",
        body: adminForm
    });

    if (response.redirected) {
        window.location.href = response.url
    }
    else {
        const data = await response.json();
        document.getElementById('adminInput').value = ''
        document.getElementById("errorMessage").innerText = data.error
    }
})

const createBtn = document.getElementById('create')
const overlayContainer = document.getElementById('overlayCreate')
const closeBtn = document.getElementById('close')

if (createBtn) {
    createBtn.addEventListener('click', () => {
        overlayContainer.classList.add('active')
    })
}

closeBtn.addEventListener('click', () => {
    overlayContainer.classList.remove('active')

    const selects = overlayContainer.querySelectorAll('select')
    selects.forEach((select) => {
        select.selectedIndex = 0;
    })

    const textarea = overlayContainer.querySelector('textarea')
    if (textarea) textarea.value = ''
})