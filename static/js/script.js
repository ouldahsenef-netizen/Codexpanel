// دالة مساعدة لعرض رسالة الحالة بأسفل خانة Creat Bot
function showStatusMessage(message, success = true) {
    const statusDiv = document.getElementById('bot-name-status');
    statusDiv.textContent = message;
    statusDiv.style.color = success ? "#3b82f6" /* ازرق كودكس */ : "#dc2626" /* أحمر */;
}

// حدث زر إنشاء الحساب
document.getElementById('verify-your-bot').addEventListener('click', () => {
    const botNum = document.getElementById('bot-select').value;
    const botName = document.getElementById('bot-name').value.trim();

    if (!botNum) {
        showStatusMessage('يرجى اختيار رقم الحساب.', false);
        return;
    }
    if (!botName) {
        showStatusMessage('يرجى إدخال اسم البوت.', false);
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
            showStatusMessage(data.message, data.message.includes('نجاح'));
            if(data.nicknames){
                for (const [key, nickname] of Object.entries(data.nicknames)) {
                    const el = document.getElementById(`nick-${key}`);
                    if(el) el.textContent = nickname || "(فارغ)";
                }
            }
        } else if (data.error) {
            showStatusMessage('خطأ: ' + data.error, false);
        } else {
            showStatusMessage('رد غير متوقع', false);
        }
    })
    .catch(err => showStatusMessage('فشل الطلب: ' + err.message, false));
});

// إضافة صديق
document.getElementById('adding-friend').addEventListener('click', () => {
    const botNum = document.getElementById('bot-list-add').value;
    const friendUid = document.getElementById('user-id').value.trim();

    if (!botNum) {
        showStatusMessage('يرجى اختيار رقم الحساب في إضافة صديق.', false);
        return;
    }
    if (!friendUid) {
        showStatusMessage('يرجى إدخال معرف الصديق (UID).', false);
        return;
    }

    fetch('/add-friend', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ bot: botNum, friend_uid: friendUid })
    }).then(res => res.json())
    .then(data => {
        if(data.message) {
            showStatusMessage(data.message, data.message.includes('نجاح'));
        } else if (data.error) {
            showStatusMessage('خطأ: ' + data.error, false);
        } else {
            showStatusMessage('رد غير متوقع', false);
        }
    }).catch(err => showStatusMessage('فشل الطلب: ' + err.message, false));
});

// إزالة صديق
document.getElementById('remove-friend').addEventListener('click', () => {
    const botNum = document.getElementById('bot-list-remove').value;
    const friendUid = document.getElementById('friend-player-id').value.trim();

    if (!botNum) {
        showStatusMessage('يرجى اختيار رقم الحساب في إزالة صديق.', false);
        return;
    }
    if (!friendUid) {
        showStatusMessage('يرجى إدخال معرف الصديق (UID).', false);
        return;
    }

    fetch('/remove-friend', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ bot: botNum, friend_uid: friendUid })
    }).then(res => res.json())
    .then(data => {
        if(data.message) {
            showStatusMessage(data.message, data.message.includes('نجاح'));
        } else if (data.error) {
            showStatusMessage('خطأ: ' + data.error, false);
        } else {
            showStatusMessage('رد غير متوقع', false);
        }
    }).catch(err => showStatusMessage('فشل الطلب: ' + err.message, false));
});

// إغلاق المودال
document.querySelector('.close-modal').addEventListener('click', () => {
    document.getElementById('result-modal').style.display = 'none';
});
