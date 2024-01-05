document.getElementById('chat-form').addEventListener('submit', function(event) {
    event.preventDefault();
    let question = document.getElementById('question').value;
    let chatContainer = document.getElementById('chat-container');

    chatContainer.insertAdjacentHTML('beforeend', '<div class="message user-message">' + question + '</div>');

    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'question=' + encodeURIComponent(question),
    })
    .then(response => response.json())
    .then(data => {
        chatContainer.insertAdjacentHTML('beforeend', '<div class="message chatbot-message">' + data.response + '</div>');
    });

    document.getElementById('question').value = '';
});