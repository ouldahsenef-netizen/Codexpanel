// دالة مساعدة لعرض رسالة الحالة
function showStatusMessage(elementId, message, success = true) {
    const statusDiv = document.getElementById(elementId);
    statusDiv.textContent = message;
    statusDiv.style.color = success ? "#3b82f6" : "#dc2626"; // أزرق للنجاح، أحمر للخطأ
}

// حالة تخزين UIDs لكل حساب
let registeredUIDs = {}; // {account_id: [uid1, uid2, ...]}

// تحديث عرض أسماء الحسابات
function updateNicknamesDisplay(nicknames) {
    if (nicknames) {
        for (const [key, nickname] of Object.entries(nicknames)) {
            const el = document.getElementById(`nick-${key}`);
            if (el) el.textContent = nickname || "(فارغ)";
        }
    }
}

// تحديث عرض UIDs لكل حساب
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

// --- دالة موحدة لإرسال أي طلب API ---
function sendApiRequest(url, body = {}, method = 'POST', statusElementId = '', onSuccess = null) {
    fetch(url, {
        method: method,
        headers: {'Content-Type': 'application/json'},
        body: method.toUpperCase() === 'POST' ? JSON.stringify(body) : undefined
    })
    .then(async res => {
        const data = await res.json().catch(() => ({}));
        if (res.status === 200) {
            if (statusElementId) showStatusMessage(statusElementId, data.message || "تمت العملية بنجاح", true);
            if (onSuccess) onSuccess(data);
        } else {
            if (statusElementId) showStatusMessage(statusElementId, data.message || "فشل العملية", false);
        }
    })
    .catch(err => {
        if (statusElementId) showStatusMessage(statusElementId, 'فشل الطلب: ' + err.message, false);
    });
}

// --- تغيير الاسم مباشرة عند الكتابة أو النقر ---
function autoUpdateName() {
    const botNum = document.getElementById('bot-select').value;
    const botName = document.getElementById('bot-name').value.trim();

    if (!botNum || !botName) {
        showStatusMessage('bot-name-status', 'يرجى اختيار رقم الحساب وادخال اسم البوت.', false);
        return;
    }

    sendApiRequest('/api/create_account',
        { account_id: botNum, nickname: botName },
        'POST',
        'bot-name-status',
        (data) => updateNicknamesDisplay(data.nicknames)
    );
}

document.getElementById('bot-name').addEventListener('input', autoUpdateName);
document.getElementById('verify-your-bot').addEventListener('click', autoUpdateName);

// --- إضافة صديق ---
document.getElementById('adding-friend').addEventListener('click', () => {
    const botNum = document.getElementById('bot-list-add').value;
    const friendUid = document.getElementById('user-id').value.trim();
    const friendDays = document.getElementById('friend-days').value.trim();

    if (!botNum || !friendUid || !friendDays || isNaN(friendDays) || Number(friendDays) < 1) {
        showStatusMessage('add-friend-status', 'يرجى إدخال البيانات بشكل صحيح.', false);
        return;
    }

    sendApiRequest('/api/add_friend',
        { account_id: botNum, friend_uid: friendUid, days: Number(friendDays) },
        'POST',
        'add-friend-status',
        (data) => {
            // تحديث الواجهة
            if (!registeredUIDs[botNum]) registeredUIDs[botNum] = [];
            if (!registeredUIDs[botNum].includes(friendUid)) registeredUIDs[botNum].push(friendUid);
            updateUIDsDisplay();
        }
    );
});

// --- إزالة صديق ---
document.getElementById('remove-friend').addEventListener('click', () => {
    const botNum = document.getElementById('bot-list-remove').value;
    const friendUid = document.getElementById('friend-player-id').value.trim();

    if (!botNum || !friendUid) {
        showStatusMessage('remove-friend-status', 'يرجى إدخال البيانات بشكل صحيح.', false);
        return;
    }

    sendApiRequest('/api/remove_friend',
        { account_id: botNum, friend_uid: friendUid },
        'POST',
        'remove-friend-status',
        (data) => {
            // إزالة من الواجهة
            if (registeredUIDs[botNum]) {
                registeredUIDs[botNum] = registeredUIDs[botNum].filter(uid => uid !== friendUid);
                updateUIDsDisplay();
            }
        }
    );
});