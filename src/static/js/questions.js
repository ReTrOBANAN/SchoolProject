const questionsList = document.querySelector('#questions-list')
const seacrhInput = document.querySelector('#search')
const subjectSelect = document.getElementById('subject')
const gradeSelect = document.getElementById('grade')

let questions = [
    {
        id: 1,
        username: 'Мария',
        subject: 'История',
        time: '20.12.23:23:45:54',
        grade: '5 класс',
        text: 'Кто был первым президентом США?'
    },
    {
        id: 2,
        username: 'Иван',
        subject: 'Биология',
        time: '15 минут назад',
        grade: '9 класс',
        text: 'Какая функция у митохондрий в клетке?'
    },
    {
        id: 3,
        username: 'Елена',
        subject: 'Физика',
        time: '20 минут назад',
        grade: '11 класс',
        text: 'Что такое закон сохранения энергии?'
    },
    {
        id: 4,
        username: 'Сергей',
        subject: 'Химия',
        time: '25 минут назад',
        grade: '9 класс',
        text: 'Какая формула воды?'
    },
    {
        id: 5,
        username: 'Ольга',
        subject: 'Литература',
        time: '30 минут назад',
        grade: '7 класс',
        text: 'Назовите главного героя романа "Война и мир".'
    },
    {
        id: 6,
        username: 'Дмитрий',
        subject: 'География',
        time: '35 минут назад',
        grade: '3 класс',
        text: 'Какая самая высокая гора в мире?'
    },
    {
        id: 7,
        username: 'Наталья',
        subject: 'Математика',
        time: '40 минут назад',
        grade: '11 класс',
        text: 'Что такое квадратный корень числа 144?'
    },
    {
        id: 8,
        username: 'Алексей',
        subject: 'Физика',
        time: '45 минут назад',
        grade: '6 класс',
        text: 'Почему предметы падают на землю?'
    },
    {
        id: 9,
        username: 'Татьяна',
        subject: 'История',
        time: '50 минут назад',
        grade: '9 класс',
        text: 'Когда началась Вторая мировая война?'
    }
];


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
        
        // for (let question of questions) {
        //     let num = question.grade.split(' ')[0]
        //     let min = grade.split(' ')[0]
        //     let max = grade.split(' ')[2]
            
        //     if (min >= num && num <= max) {

        //     }
        // }
    }

    render(filtered)
}

seacrhInput.addEventListener('input', applyFilters)
subjectSelect.addEventListener('change', applyFilters)
gradeSelect.addEventListener('change', applyFilters)


function render(questions = []) {
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

render(questions)