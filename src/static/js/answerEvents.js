const createBtn = document.getElementById('create')
const overlayContainer = document.getElementById('overlayCreate')
const closeBtn = document.getElementById('close')
if (createBtn) {
    createBtn.addEventListener('click', () => {
        overlayContainer.classList.add('active')
    })
}


if (closeBtn) {
    closeBtn.addEventListener('click', () => {
        overlayContainer.classList.remove('active')
        
        const selects = overlayContainer.querySelectorAll('select')
        selects.forEach((select) => {
            select.selectedIndex = 0;
        })

        const textarea = overlayContainer.querySelector('textarea')
        if (textarea) textarea.value = ''
    })
}

const editBtn = document.getElementById('editBtn')
const editContainer = document.getElementById('editContainer')
if (editBtn && editContainer) {
    editBtn.addEventListener('click', (e) => {
        e.stopPropagation();

        const activeContainers = document.querySelectorAll('.question-edit-container.active');
        activeContainers.forEach(active => {
            if (active !== editContainer) active.classList.remove('active');
        });
        editContainer.classList.toggle('active');
    })
}

answersList.addEventListener('click', (e) => {
    const editBtn = e.target.closest('#editBtn')
    const reportAnswerBtn = e.target.closest('#reportAnswerBtn')
    const deleteAnswerBtn = e.target.closest('#deleteAnswerBtn')
    const changeAnswerBtn = e.target.closest('#changeAnswerBtn')
    const finishReadBtn = e.target.closest('#finishReadBtn')

    
    // Обработка кнопки редактирования
    if (editBtn) {
        const container = editBtn.closest('.questions-content-item')
                            .querySelector('.question-edit-container');
        
        // Закрываем все активные контейнеры кроме текущего
        document.querySelectorAll('.question-edit-container.active')
                .forEach(active => {
                    if (active !== container) {
                        active.classList.remove('active');
                    }
                });
        
        container.classList.toggle('active');
        e.stopPropagation();
        return;
    }
    
    // Обработка кнопки жалобы
    if (reportAnswerBtn) {
        const overlayReportAnswerContainer = document.getElementById('overlayReportAnswerContainer');
        const closeReportAnswerContainerBtn = document.getElementById('closeReportAnswerContainerBtn');
        
        if (closeReportAnswerContainerBtn && closeReportAnswerContainerBtn) {
            overlayReportAnswerContainer.classList.add('active');

            const reportAnswerId = document.getElementById('reportAnswerId')
            const reportAnswerQuestionId = document.getElementById('reportAnswerQuestionId')

            reportAnswerId.value = reportAnswerBtn.dataset.id
            reportAnswerQuestionId.value = reportAnswerBtn.dataset.questionid
            

            
            // Убираем дублирование обработчиков
            closeReportAnswerContainerBtn.onclick = () => {
                overlayReportAnswerContainer.classList.remove('active');
            };
        }
    }
    
    if (deleteAnswerBtn) {
        const overlaySureAnswerDelete = document.getElementById('overlaySureAnswerDelete')
        const sureCancelAnswerBtn = document.getElementById('sureCancelAnswerBtn')
        const sureCloseAnswerBtn = document.getElementById('sureCloseAnswerBtn')

        if (overlaySureAnswerDelete && sureCancelAnswerBtn && sureCloseAnswerBtn) {
            overlaySureAnswerDelete.classList.add('active')

            const deleteAnswerOwner = document.getElementById('deleteAnswerOwner')
            const deleteAnswerId = document.getElementById('deleteAnswerId')
            const deleteAnswerQuestionId = document.getElementById('deleteAnswerQuestionId')
            deleteAnswerOwner.value = deleteAnswerBtn.dataset.owner
            deleteAnswerId.value = deleteAnswerBtn.dataset.id
            deleteAnswerQuestionId.value = deleteAnswerBtn.dataset.questionid

            sureCancelAnswerBtn.addEventListener('click', () => {
                overlaySureAnswerDelete.classList.remove('active')
            })
            sureCloseAnswerBtn.addEventListener('click', () => {
                overlaySureAnswerDelete.classList.remove('active')
            })
        }
    }
    if (changeAnswerBtn) {
        const overlayChangeAnswerContainer = document.getElementById('overlayChangeAnswerContainer')
        const closeChangeAnswerContainerBtn = document.getElementById('closeChangeAnswerContainerBtn')
        if (overlayChangeAnswerContainer && closeChangeAnswerContainerBtn) {
            overlayChangeAnswerContainer.classList.add('active')

            const changeAnswerOwner = document.getElementById('changeAnswerOwner')
            const changeAnswerId = document.getElementById('changeAnswerId')
            const changeQuestionId = document.getElementById('changeQuestionId')
            changeAnswerOwner.value = changeAnswerBtn.dataset.owner
            changeAnswerId.value = changeAnswerBtn.dataset.id
            changeQuestionId.value = changeAnswerBtn.dataset.questionid

            closeChangeAnswerContainerBtn.addEventListener('click', () => {
                overlayChangeAnswerContainer.classList.remove('active')

                const textarea = overlayChangeAnswerContainer.querySelector('textarea')
                if (textarea) textarea.value = ''
            })
        }
    }

    if (finishReadBtn) {
        const container = finishReadBtn.closest('.questions-content-item')
        const textBlock = container.querySelector('.answer-text')

        if (textBlock.classList.contains('short-text')) {
            textBlock.classList.remove('short-text')
            finishReadBtn.textContent = 'Скрыть'
        }
        else {
            textBlock.classList.add('short-text')
            finishReadBtn.textContent = 'Читать далее'
        }
    }
})
document.addEventListener('click', (e) => {
    const activeContainers = document.querySelectorAll('.question-edit-container.active');

    activeContainers.forEach(container => {
        container.classList.remove('active');
    });
});



const deleteQuestionBtn = document.getElementById('deleteQuestionBtn')
const overlaySureQuestionDelete = document.getElementById('overlaySureQuestionDelete')
const sureCancelQuestionBtn = document.getElementById('sureCancelQuestionBtn')
const sureCloseQuestionBtn = document.getElementById('sureCloseQuestionBtn')

if (deleteQuestionBtn && overlaySureQuestionDelete && sureCancelQuestionBtn && sureCloseQuestionBtn) {
    deleteQuestionBtn.addEventListener('click', () => {
        overlaySureQuestionDelete.classList.add('active')
    })
    sureCancelQuestionBtn.addEventListener('click', () => {
        overlaySureQuestionDelete.classList.remove('active')
    })
    sureCloseQuestionBtn.addEventListener('click', () => {
        overlaySureQuestionDelete.classList.remove('active')
    })
}


const changeQuestionBtn = document.getElementById('changeQuestionBtn')
const overlayChangeQuestionContainer = document.getElementById('overlayChangeQuestionContainer')
const closeChangeQuestionContainerBtn = document.getElementById('closeChangeQuestionContainerBtn')
if (changeQuestionBtn && overlayChangeQuestionContainer && closeChangeQuestionContainerBtn) {
    changeQuestionBtn.addEventListener('click', () => {
        overlayChangeQuestionContainer.classList.add('active')
    })
    closeChangeQuestionContainerBtn.addEventListener('click', () => {
        overlayChangeQuestionContainer.classList.remove('active')

        const selects = overlayChangeQuestionContainer.querySelectorAll('select')
        selects.forEach((select) => {
            select.selectedIndex = 0;
        })

        const textarea = overlayChangeQuestionContainer.querySelector('textarea')
        if (textarea) textarea.value = ''
    })
}


const reportQuestionBtn = document.getElementById('reportQuestionBtn')
const overlayReportQuestionContainer = document.getElementById('overlayReportQuestionContainer')
const closeReportQuestionContainerBtn = document.getElementById('closeReportQuestionContainerBtn')
if (reportQuestionBtn && overlayReportQuestionContainer) {
    reportQuestionBtn.addEventListener('click', () => {
        overlayReportQuestionContainer.classList.add('active')
    })
    closeReportQuestionContainerBtn.addEventListener('click', () => {
        overlayReportQuestionContainer.classList.remove('active')
    })
}

// Поле ответа
const textarea = document.getElementById('answerTextArea')
textarea.addEventListener("input", () => {
    textarea.style.height = "auto"
    textarea.style.height = Math.min(textarea.scrollHeight, 1000) + "px";
});



