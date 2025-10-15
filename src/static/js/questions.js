const questionsList = document.querySelector('#questionsList')
const seacrhInput = document.querySelector('#search')
const subjectSelect = document.getElementById('subject')
const gradeSelect = document.getElementById('grade')

let questions = []

async function start() {
    try {
        questionsList.innerHTML = '<p style="text-align: center;">Загрузка...</p>'
        const response = await fetch('/api/questions')
        questions = await response.json()
        render(questions)
    }
    catch (err) {
        questionsList.innerHTML = `<p style="text-align: center;">Ошибка при загрузке вопросов</p>`
    }
}

function applyFilters() {
    const value = seacrhInput.value.toLowerCase()
    const subject = subjectSelect.options[subjectSelect.selectedIndex].text.toLowerCase();
    const grade = gradeSelect.options[gradeSelect.selectedIndex].text.toLowerCase();

    let filtered = questions
    
    
    if (value) {
        console.log(questions)
        filtered = filtered.filter((question) => question.text.toLowerCase().includes(value))
    }
    if (subject !== 'все предметы') {
        filtered = filtered.filter((question) => question.subject.toLowerCase().includes(subject))
    }
    if (grade !== 'все классы') {
        filtered = filtered.filter((question) => {
            let num = Number(question.grade)
            let min = Number(grade.split(' ')[0])
            let max = Number(grade.split(' ')[2])

            return num >= min && num <= max
        })
    }

    render(filtered)
}

seacrhInput.addEventListener('input', applyFilters)
subjectSelect.addEventListener('change', applyFilters)
gradeSelect.addEventListener('change', applyFilters)


function render(questions = []) {
    if (questions.length === 0) {
        questionsList.innerHTML = `<p style="text-align: center;">Вопросов нет</p>`
    }
    else {
        const html = questions.map(toHTML).join('')
        questionsList.innerHTML = html
    }
}

function toHTML(question) {
    return `<li class="questions-content-item">
        <div class="questions-item-header">
            <div class="item-header-name">${question.name} (${question.username})</div>
            <div class="item-header-subject">${question.subject}</div>
            <div class="item-header-grade">${question.grade} класс</div>
            <div class="item-header-time">${timeAgo(question.created_at)}</div>
        </div>
        <div class="questions-item-body">${question.text}</div>
        <div class="questions-item-footer">
            <a class="btn" href="question/${question.id}">Ответить</a>
        </div>
    </li>`
}

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

    const selects = overlayContainer.querySelectorAll('select')
    selects.forEach((select) => {
        select.selectedIndex = 0;
    })

    const textarea = overlayContainer.querySelector('textarea')
    if (textarea) textarea.value = ''
})

start()


window.addEventListener('DOMContentLoaded', () => {
    const selects = document.querySelectorAll('select')
    selects.forEach((select) => {
        select.selectedIndex = 0;
    })
});
