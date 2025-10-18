const profileQuestionsContainer = document.getElementById('profileQuestionsContainer')

async function start() {
    profileUsername = profileQuestionsContainer.dataset.username
    try {
    profileQuestionsContainer.innerHTML = '<p style="text-align: center;">Загрузка...</p>'
        const response = await fetch('/api/questions')
        questions = await response.json()
        questions = questions.filter((question) => question.username === profileUsername)
        render(questions)
    }
    catch (err) {
        profileQuestionsContainer.innerHTML = `<p style="text-align: center;">Ошибка при загрузке вопросов</p>`
    }
}

function render(questions = []) {
    if (questions.length === 0) {
        profileQuestionsContainer.innerHTML = `<p style="text-align: center;">У пользователя нет вопросов</p>`
    }
    else {
        const html = questions.map(toHTML).join('')
        profileQuestionsContainer.innerHTML = html
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
            <a class="btn" href="/question/${question.id}">Посмотреть</a>
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

start()