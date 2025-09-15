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

    // مثال استدعاء API (تبديل حسب وظيفتك)
    /*
    fetch('/api/add-friend', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({bot, userId, days})
    }).then(res => res.json())
      .then(data => alert(`Success: ${data.message}`))
      .catch(err => alert('Error: ' + err.message));
    */
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

    // مثال استدعاء API (تبديل حسب وظيفتك)
    /*
    fetch('/api/remove-friend', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({bot, friendId})
    }).then(res => res.json())
      .then(data => alert(`Success: ${data.message}`))
      .catch(err => alert('Error: '+err.message));
    */
    alert(`Sent request to remove friend with player ID "${friendId}" using bot "${bot}".`);
});

// إغلاق المودال
document.querySelector('.close-modal').addEventListener('click', () => {
    document.getElementById('result-modal').style.display = 'none';
});
