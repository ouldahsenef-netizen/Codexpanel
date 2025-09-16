// إضافة حدث لزر إنشاء الحساب
document.getElementById('verify-your-bot').addEventListener('click', () => {
    const botSelect = document.getElementById('bot-select').value;
    const botName = document.getElementById('bot-name').value.trim();

    if (!botSelect) {
        alert('Please select a bot number.');
        return;
    }
    if (!botName) {
        alert('Please enter a bot name.');
        return;
    }

    fetch('/create-acc', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            bot: botSelect,
            name: botName
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert(data.message);
        } else if (data.error) {
            alert('Error: ' + data.error);
        } else {
            alert('Unexpected response');
        }
    })
    .catch(error => {
        alert('Request failed: ' + error.message);
    });
});

// إضافة وظائف أزرار إضافة وإزالة الأصدقاء كما في الكود السابق

document.getElementById('adding-friend').addEventListener('click', () => {
    const bot = document.getElementById('bot-list-add').value;
    const userId = document.getElementById('user-id').value.trim();
    const days = document.getElementById('days').value.trim();

    if (!bot) {
        alert('Please select a bot from YOUR BOT LIST.');
        return;
    }
    if (!userId) {
        alert('Please enter a User ID.');
        return;
    }
    if (!days) {
        alert('Please enter number of days.');
        return;
    }

    console.log(`Adding friend: User ID=${userId}, Days=${days}, using Bot=${bot}`);

    alert(`Sent request to add friend with User ID "${userId}" for ${days} days using bot "${bot}".`);
});

document.getElementById('remove-friend').addEventListener('click', () => {
    const bot = document.getElementById('bot-list-remove').value;
    const friendId = document.getElementById('friend-player-id').value.trim();

    if (!bot) {
        alert('Please select a bot from YOUR BOT LIST.');
        return;
    }
    if (!friendId) {
        alert('Please enter a Player ID.');
        return;
    }

    console.log(`Removing friend: Player ID=${friendId} using Bot=${bot}`);

    alert(`Sent request to remove friend with player ID "${friendId}" using bot "${bot}".`);
});

// إغلاق المودال
document.querySelector('.close-modal').addEventListener('click', () => {
    document.getElementById('result-modal').style.display = 'none';
});
