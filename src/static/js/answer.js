const questionTime = document.getElementById('questionTime')
const time = questionTime.dataset.questionTime

questionTime.innerHTML = timeAgo(time)

function timeAgo(dateString) {
    dateString += "Z";
    const now = new Date();
    const date = new Date(dateString);
    const diff = (now - date) / 1000;

    if (diff < 60) {
        return `${Math.round(diff)} сек. назад`
    }
    else if (diff < 3600) {
        return `${Math.round(diff / 60)} мин. назад`
    }
    else if (diff < 86400) {
        return `${Math.round(diff / 3600)} ч. назад`
    }
    else if (diff < 2628000) {
        return `${Math.round(diff / 86400)} дн. назад`
    }
    else if (diff < 31540000){
        return `${Math.round(diff / 2628000)} мес. назад`
    }
    else {
        return `${date.toLocaleDateString("ru-RU")}`
    }
}


const answersList = document.getElementById('answerList')
async function start() {
    try {
        answersList.innerHTML = `<p style="text-align: center; margin-top: 20px">Загрузка ответов...</p>`
        const response = await fetch('/api/answers')
        answers = await response.json()
        render(answers)
    }
    catch (err) {
        answersList.innerHTML = `<p style="text-align: center; margin-top: 20px">Ошибка при загрузке ответов</p>`
    }
}



function render(answers = []) {
    const questionid = answersList.dataset.questionid
    answers = answers.filter((answer) => answer.question_id === Number(questionid))
    console.log(answers)
    if (answers.length === 0) {
        answersList.innerHTML = `<p style="text-align: center; margin-top: 20px">Нет ответов. Будьте первыми!</p>`
    }
    else {
        const html = answers.map(toHTML).join('')
        answersList.innerHTML = html
    }
}

function toHTML(answer) {
    return `<li class="questions-content-item">
        <div class="questions-item-header">
            <div>${answer.name}</div>
            <div>${timeAgo(answer.created_at)}</div>
        </div>
        <div class="question-text">
            ${answer.text}
        </div>
    </li>
    `
}

start()

const createBtn = document.getElementById('create')
const overlayContainer = document.getElementById('overlay')
const closeBtn = document.getElementById('close')
if (createBtn) {
    createBtn.addEventListener('click', () => {
        overlayContainer.classList.add('active')
    })
}


closeBtn.addEventListener('click', () => {
    overlayContainer.classList.remove('active')
})



const editBtn = document.getElementById('editBtn')
const editContainer = document.getElementById('editContainer')
if (editBtn && editContainer) {
    editBtn.addEventListener('click', (e) => {
        e.stopPropagation()
        if (editContainer.classList.value.includes('active')) {
            editContainer.classList.remove('active')
        }
        else {
            editContainer.classList.add('active')
        }
    })

    document.addEventListener('click', () => {
        editContainer.classList.remove('active')
    })
}



const deleteBtn = document.getElementById('deleteBtn')
const overlaySuredelete = document.getElementById('overlaySureDelete')
const sureCancelBtn = document.getElementById('sureCancelBtn')
const sureCloseBtn = document.getElementById('sureCloseBtn')
if (deleteBtn && overlaySuredelete) {
    deleteBtn.addEventListener('click', () => {
        overlaySuredelete.classList.add('active')
    })
    sureCancelBtn.addEventListener('click', () => {
        overlaySuredelete.classList.remove('active')
    })
    sureCloseBtn.addEventListener('click', () => {
        overlaySuredelete.classList.remove('active')
    })
}


const changeBtn = document.getElementById('changeBtn')
const overlayChangeContainer = document.getElementById('overlayChangeContainer')
const closeChangeContainerBtn = document.getElementById('closeChangeContainerBtn')
if (changeBtn && overlayChangeContainer) {
    changeBtn.addEventListener('click', () => {
        overlayChangeContainer.classList.add('active')
    })
    closeChangeContainerBtn.addEventListener('click', () => {
        overlayChangeContainer.classList.remove('active')
    })
}