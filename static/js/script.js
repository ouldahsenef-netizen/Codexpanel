// دالة مساعدة لعرض رسالة الحالة بأسفل خانة Creat Bot أو الأدوات الأخرى
function showStatusMessage(elementId, message, success = true) {
    const statusDiv = document.getElementById(elementId);
    statusDiv.textContent = message;
    statusDiv.style.color = success ? "#3b82f6" /* أزرق كودكس */ : "#dc2626" /* أحمر */;
}

// حدث زر إنشاء الحساب
document.getElementById('verify-your-bot').addEventListener('click', () => {
    const botNum = document.getElementById('bot-select').value;
    const botName = document.getElementById('bot-name').value.trim();

    if (!botNum) {
        showStatusMessage('bot-name-status', 'يرجى اختيار رقم الحساب.', false);
        return;
    }
    if (!botName) {
        showStatusMessage('bot-name-status', 'يرجى إدخال اسم البوت.', false);
        return;
    }

    fetch('/create-acc', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ bot: botNum, name: botName })
    })
    .then(res => res.json())
    .then(data => {
        if (data.message) {
            showStatusMessage('bot-name-status', data.message, data.message.includes('نجاح'));
            if(data.nicknames){
                for (const [key, nickname] of Object.entries(data.nicknames)) {
                    const el = document.getElementById(`nick-${key}`);
                    if(el) el.textContent = nickname || "(فارغ)";
                }
            }
        } else if (data.error) {
            showStatusMessage('bot-name-status', 'خطأ: ' + data.error, false);
        } else {
            showStatusMessage('bot-name-status', 'رد غير متوقع', false);
        }
    })
    .catch(err => showStatusMessage('bot-name-status', 'فشل الطلب: ' + err.message, false));
});

// إضافة صديق
document.getElementById('adding-friend').addEventListener('click', () => {
    const botNum = document.getElementById('bot-list-add').value;
    const friendUid = document.getElementById('user-id').value.trim();

    if (!botNum) {
        showStatusMessage('add-friend-status', 'يرجى اختيار رقم الحساب في إضافة صديق.', false);
        return;
    }
    if (!friendUid) {
        showStatusMessage('add-friend-status', 'يرجى إدخال معرف الصديق (UID).', false);
        return;
    }

    fetch('/add-friend', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ bot: botNum, friend_uid: friendUid })
    }).then(res => res.json())
    .then(data => {
        if(data.message) {
            showStatusMessage('add-friend-status', data.message, data.message.includes('نجاح'));
        } else if (data.error) {
            showStatusMessage('add-friend-status', 'خطأ: ' + data.error, false);
        } else {
            showStatusMessage('add-friend-status', 'رد غير متوقع', false);
        }
    }).catch(err => showStatusMessage('add-friend-status', 'فشل الطلب: ' + err.message, false));
});

// إزالة صديق
document.getElementById('remove-friend').addEventListener('click', () => {
    const botNum = document.getElementById('bot-list-remove').value;
    const friendUid = document.getElementById('friend-player-id').value.trim();

    if (!botNum) {
        showStatusMessage('remove-friend-status', 'يرجى اختيار رقم الحساب في إزالة صديق.', false);
        return;
    }
    if (!friendUid) {
        showStatusMessage('remove-friend-status', 'يرجى إدخال معرف الصديق (UID).', false);
        return;
    }

    fetch('/remove-friend', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ bot: botNum, friend_uid: friendUid })
    }).then(res => res.json())
    .then(data => {
        if(data.message) {
            showStatusMessage('remove-friend-status', data.message, data.message.includes('نجاح'));
        } else if (data.error) {
            showStatusMessage('remove-friend-status', 'خطأ: ' + data.error, false);
        } else {
            showStatusMessage('remove-friend-status', 'رد غير متوقع', false);
        }
    }).catch(err => showStatusMessage('remove-friend-status', 'فشل الطلب: ' + err.message, false));
});

// إغلاق المودال
document.querySelector('.close-modal').addEventListener('click', () => {
    document.getElementById('result-modal').style.display = 'none';
});
