const questionsList = document.querySelector('#questions-list')
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
        filtered = filtered.filter((question) => question.text.toLowerCase().includes(value))
    }
    if (subject !== 'все предметы') {
        filtered = filtered.filter((question) => question.subject.toLowerCase().includes(subject))
    }
    if (grade !== 'все классы') {
        filtered = filtered.filter((question) => {
            let num = Number(question.grade.split(' ')[0])
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
    console.log(questions)
    if (questions.length === 0) {
        questionsList.innerHTML = `<p style="text-align: center;">Таких вопросов нет</p>`
    }
    else {
        const html = questions.map(toHTML).join('')
        questionsList.innerHTML = html
    }
}

function toHTML(question) {
    return `<li class="questions-content-item">
        <div class="questions-item-header">
            <div class="item-header-name">${question.username}</div>
            <div class="item-header-subject">${question.subject}</div>
            <div class="item-header-grade">${question.grade}</div>
            <div class="item-header-time">${question.time}</div>
        </div>
        <div class="questions-item-body">
            ${question.text}
        </div>
        <div class="questions-item-footer">
            <a class="btn" href="">Ответить</a>
        </div>
    </li>`
}

const createBtn = document.getElementById('create')
const overlayContainer = document.getElementById('overlay')
const closeBtn = document.getElementById('close')
createBtn.addEventListener('click', () => {
    overlayContainer.classList.add('active')
})
closeBtn.addEventListener('click', () => {
    overlayContainer.classList.remove('active')
})

start()