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