const questionTime = document.getElementById('questionTime')
const time = questionTime.dataset.questionTime

questionTime.innerHTML = timeAgo(time)
