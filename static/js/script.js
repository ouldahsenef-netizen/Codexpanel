// دالة مساعدة لعرض رسالة الحالة
function showStatusMessage(elementId, message, success = true) {
    const statusDiv = document.getElementById(elementId);
    statusDiv.textContent = message;
    statusDiv.style.color = success ? "#3b82f6" : "#dc2626"; // أزرق للنجاح، أحمر للخطأ
}

// حالة تخزين UIDs لكل حساب
let registeredUIDs = {}; // {account_id: [uid1, uid2, ...]}

// دالة لتحديث عرض حالة الحسابات بأسمائها الجديدة
function updateNicknamesDisplay(nicknames) {
    if(nicknames){
        for (const [key, nickname] of Object.entries(nicknames)) {
            const el = document.getElementById(`nick-${key}`);
            if(el) el.textContent = nickname || "(فارغ)";
        }
    }
}

// دالة لتحديث عرض UIDs لكل حساب
function updateUIDsDisplay() {
    const uidsListDiv = document.getElementById('uids-list');
    uidsListDiv.innerHTML = '';

    for (const [accountId, uids] of Object.entries(registeredUIDs)) {
        let accountDiv = document.createElement('div');
        accountDiv.innerHTML = `<h3>الحساب ${accountId}:</h3>`;
        let ul = document.createElement('ul');

        uids.forEach(uid => {
            let li = document.createElement('li');
            li.textContent = uid;
            ul.appendChild(li);
        });

        accountDiv.appendChild(ul);
        uidsListDiv.appendChild(accountDiv);
    }
}

// دالة لتحديث الاسم مباشرة عند الكتابة أو النقر
function autoUpdateName() {
    const botNum = document.getElementById('bot-select').value;
    const botName = document.getElementById('bot-name').value.trim();

    if (!botNum || !botName) {
        showStatusMessage('bot-name-status', 'يرجى اختيار رقم الحساب وادخال اسم البوت.', false);
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
            updateNicknamesDisplay(data.nicknames);
        } else {
            showStatusMessage('bot-name-status', 'رد غير متوقع', false);
        }
    })
    .catch(err => showStatusMessage('bot-name-status', 'فشل الطلب: ' + err.message, false));
}

// حدث عند تغيير النص في حقل الاسم مباشرة
document.getElementById('bot-name').addEventListener('input', () => {
    autoUpdateName();
});

// حدث زر إنشاء الحساب (مازال موجود لدعم الاستخدام اليدوي)
document.getElementById('verify-your-bot').addEventListener('click', () => {
    autoUpdateName();
});

// إضافة صديق
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
        if(data.success) {
            showStatusMessage('add-friend-status', data.message, true);

            if (!registeredUIDs[botNum]) {
                registeredUIDs[botNum] = [];
            }
            if (!registeredUIDs[botNum].includes(friendUid)) {
                registeredUIDs[botNum].push(friendUid);
            }
            updateUIDsDisplay();

            const apiUrl = `https://time-bngx-0c2h.onrender.com/api/add_uid?uid=${encodeURIComponent(friendUid)}&time=${encodeURIComponent(friendDays)}&type=days&permanent=false`;
            fetch(apiUrl).then(res => res.json())
                .then(apiData => {
                    if(apiData.success || apiData.message) {
                        showStatusMessage('add-friend-status', 'تم إرسال عدد الأيام بنجاح.', true);
                    } else {
                        showStatusMessage('add-friend-status', 'خطأ في إرسال عدد الأيام: ' + (apiData.error || 'Unknown error'), false);
                    }
                }).catch(err => {
                    showStatusMessage('add-friend-status', 'فشل الطلب إلى API الأيام: ' + err.message, false);
                });

        } else {
            showStatusMessage('add-friend-status', 'خطأ: ' + (data.message || data.error), false);
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
        if(data.success) {
            showStatusMessage('remove-friend-status', data.message, true);
            if (registeredUIDs[botNum]) {
                registeredUIDs[botNum] = registeredUIDs[botNum].filter(uid => uid !== friendUid);
                updateUIDsDisplay();
            }
        } else {
            showStatusMessage('remove-friend-status', 'خطأ: ' + (data.message || data.error), false);
        }
    }).catch(err => showStatusMessage('remove-friend-status', 'فشل الطلب: ' + err.message, false));
});
