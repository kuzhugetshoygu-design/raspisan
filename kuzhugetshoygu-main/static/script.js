document.addEventListener('DOMContentLoaded', function () {
    const cells = document.querySelectorAll('.cell');

    cells.forEach(cell => {
        new Sortable(cell, {
            group: 'lessons',
            animation: 150,
            ghostClass: 'sortable-ghost',
            onEnd: function (evt) {
                const lessonId = evt.item.dataset.lessonId;
                const toCell = evt.to;
                const groupId = toCell.dataset.groupId;
                const day = toCell.dataset.day;
                const para = toCell.dataset.para;

                fetch('/lessons/move', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        lesson_id: lessonId,
                        group_id: groupId,
                        day: day,
                        para: para
                    })
                })
                .then(r => r.json())
                .then(data => {
                    if (data.status === 'ok') {
                        window.location.reload();
                    } else if (data.status === 'conflict') {
                        alert('⚠️ ' + data.message);
                        evt.from.appendChild(evt.item);
                    }
                })
                .catch(err => {
                    console.error(err);
                    evt.from.appendChild(evt.item);
                });
            }
        });
    });
});

// ==== Редактирование занятия ====
function openEditLesson(id) {
    const data = LESSONS_DATA[id];
    if (!data) return;

    document.getElementById('edit_group_id').value = data.group_id;
    document.getElementById('edit_teacher_id').value = data.teacher_id;
    document.getElementById('edit_subject_id').value = data.subject_id;
    document.getElementById('edit_day').value = data.day;
    document.getElementById('edit_week1').value = data.week1_lesson || '';
    document.getElementById('edit_week2').value = data.week2_lesson || '';
    document.getElementById('edit_classroom').value = data.classroom || '';
    document.getElementById('edit_lesson_type').value = data.lesson_type || '';

    document.getElementById('editLessonForm').action = '/lessons/edit/' + id;
    document.getElementById('editLessonModal').classList.remove('hidden');
}

// ==== Удаление занятия ====
function deleteLesson(id) {
    if (!confirm('Удалить занятие?')) return;

    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/lessons/delete/' + id;
    document.body.appendChild(form);
    form.submit();
}

// ==== Раскрытие преподавателя ====
function toggleTeacher(id) {
    const list = document.getElementById('subjects-' + id);
    const header = list.previousElementSibling;
    const toggle = header.querySelector('.teacher-toggle');

    if (list.style.display === 'none') {
        list.style.display = 'block';
        toggle.textContent = '▾';
    } else {
        list.style.display = 'none';
        toggle.textContent = '▸';
    }
}

// ==== Открыть форму добавления с подставленными данными ====
function openAddLesson(teacherId, subjectId) {
    document.getElementById('addLessonForm').classList.remove('hidden');
    document.getElementById('add_teacher_id').value = teacherId;
    filterSubjects();
    document.getElementById('add_subject_id').value = subjectId;
}

// ==== Фильтрация дисциплин по преподавателю ====
function filterSubjects() {
    const teacherId = document.getElementById('add_teacher_id').value;
    const subjectSelect = document.getElementById('add_subject_id');

    subjectSelect.innerHTML = '<option value="">— выберите —</option>';

    if (!teacherId || !TEACHERS_DATA[teacherId]) return;

    const subjects = TEACHERS_DATA[teacherId].subjects;
    subjects.forEach(s => {
        const opt = document.createElement('option');
        opt.value = s.id;
        opt.textContent = s.name;
        subjectSelect.appendChild(opt);
    });
}