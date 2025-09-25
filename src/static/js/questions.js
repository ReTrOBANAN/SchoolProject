const questionsList = document.querySelector('#questions-list')
const seacrhInput = document.querySelector('#search')
let questions = [
    {
        id: 1,
        username: 'Андрей',
        subject: 'Математика',
        time: '5 минут назад',
        text: `Когда родился пушкин?.`
    },
    {
        id: 1,
        username: 'Андрей',
        subject: 'Математика',
        time: '5 минут назад',
        text: `КОГДА умер Пушкин.`
    },{
        id: 1,
        username: 'Андрей',
        subject: 'Математика',
        time: '5 минут назад',
        text: `сколько будет два плюс 2 + 3.`
    },
    {
        id: 1,
        username: 'Андрей',
        subject: 'Математика',
        time: '5 минут назад',
        text: `сколько будет два плюс 2 + 3.`
    },
    {
        id: 1,
        username: 'Андрей',
        subject: 'Математика',
        time: '5 минут назад',
        text: `сколько будет два плюс 2 + 3.`
    },
    {
        id: 1,
        username: 'Андрей',
        subject: 'Математика',
        time: '5 минут назад',
        text: `сколько будет два плюс 2 + 3.`
    },
    {
        id: 1,
        username: 'Андрей',
        subject: 'Математика',
        time: '5 минут назад',
        text: `сколько будет два плюс 2 + 3.`
    }
]

seacrhInput.addEventListener('input', (event) => {
    const value = event.target.value.toLowerCase()
    const filteredQuestions = questions.filter((question) => question.text.toLowerCase().includes(value))
    render(filteredQuestions)
})

function render(questions = []) {
    console.log(questions)
    if (questions.length === 0) {
        questionsList.innerHTML = `<p style="text-align: center;">Пока вопросов нет</p>`
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

render(questions)