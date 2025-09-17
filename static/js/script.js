// دالة مساعدة لعرض رسالة الحالة
function showStatusMessage(elementId, message, success = true) {
    const statusDiv = document.getElementById(elementId);
    statusDiv.textContent = message;
    statusDiv.style.color = success ? "#3b82f6" : "#dc2626"; // أزرق للنجاح، أحمر للخطأ
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

    fetch('/api/create_account', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ account_id: botNum, nickname: botName })
    })
    .then(res => {
        if (!res.ok) {
            return res.json().then(err => {throw new Error(err.message || "خطأ في الخادم")});
        }
        return res.json();
    })
    .then(data => {
        if (data.message) {
            showStatusMessage('bot-name-status', data.message, data.success);
            if(data.nicknames){
                for (const [key, nickname] of Object.entries(data.nicknames)) {
                    const el = document.getElementById(`nick-${key}`);
                    if(el) el.textContent = nickname || "(فارغ)";
                }
            }
        } else {
            showStatusMessage('bot-name-status', 'رد غير متوقع', false);
        }
    })
    .catch(err => showStatusMessage('bot-name-status', 'فشل الطلب: ' + err.message, false));
});

// إضافة صديق مع إرسال عدد الأيام إلى API خارجي إضافي
document.getElementById('adding-friend').addEventListener('click', () => {
    const botNum = document.getElementById('bot-list-add').value;
    const friendUid = document.getElementById('user-id').value.trim();
    const friendDays = document.getElementById('friend-days').value.trim();

    if (!botNum) {
        showStatusMessage('add-friend-status', 'يرجى اختيار رقم الحساب في إضافة صديق.', false);
        return;
    }
    if (!friendUid) {
        showStatusMessage('add-friend-status', 'يرجى إدخال معرف الصديق (UID).', false);
        return;
    }
    if (!friendDays || isNaN(friendDays) || Number(friendDays) < 1) {
        showStatusMessage('add-friend-status', 'يرجى إدخال عدد الأيام بشكل صحيح.', false);
        return;
    }

    fetch('/api/add_friend', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ account_id: botNum, friend_uid: friendUid, days: Number(friendDays) })
    })
    .then(res => res.json())
    .then(data => {
        if(data.message) {
            showStatusMessage('add-friend-status', data.message, data.message.includes('نجاح'));

            const apiUrl = `https://time-bngx-0c2h.onrender.com/api/add_uid?uid=${encodeURIComponent(friendUid)}&time=${encodeURIComponent(friendDays)}&type=days&permanent=false`;

            return fetch(apiUrl)
                .then(res => res.json())
                .then(apiData => {
                    if(apiData.success || apiData.message) {
                        showStatusMessage('add-friend-status', 'تم إرسال عدد الأيام بنجاح.', true);
                    } else {
                        showStatusMessage('add-friend-status', 'خطأ في إرسال عدد الأيام: ' + (apiData.error || 'Unknown error'), false);
                    }
                }).catch(err => {
                    showStatusMessage('add-friend-status', 'فشل الطلب إلى API الأيام: ' + err.message, false);
                });

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

    fetch('/api/remove_friend', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ account_id: botNum, friend_uid: friendUid })
    })
    .then(res => res.json())
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
