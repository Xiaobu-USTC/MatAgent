document.addEventListener('DOMContentLoaded', () => {
    const modeSelect = document.getElementById('mode-select');
    const modeConfigDiv = document.getElementById('mode-config');
    const toolsContainer = document.getElementById('tools-container');
    
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const chatMessages = document.getElementById('chat-messages');

    let selectedMode = null; 
    function displayModeConfig(mode) {
        modeConfigDiv.innerHTML = ''; 
        if (mode === 'Ollama') {
            const input = document.createElement('input');
            input.type = 'text';
            input.id = 'mode-config-input';
            input.placeholder = 'Please enter the local model address...';
            modeConfigDiv.appendChild(input);

            const saveBtn = document.createElement('button');
            saveBtn.id = 'save-config-btn';
            saveBtn.textContent = 'Save configuration';
            modeConfigDiv.appendChild(saveBtn);

            saveBtn.addEventListener('click', () => {
                const config = input.value.trim();
                if (!config) {
                    alert('The local model address cannot be empty.');
                    return;
                }
                setMode(mode, config);
            });
        } else if (mode === 'ChatGPT') {
            const input = document.createElement('input');
            input.type = 'password';
            input.id = 'mode-config-input';
            input.placeholder = 'Please enter OpenAI API Key...';
            modeConfigDiv.appendChild(input);

            const saveBtn = document.createElement('button');
            saveBtn.id = 'save-config-btn';
            saveBtn.textContent = 'Save configuration';
            modeConfigDiv.appendChild(saveBtn);

            saveBtn.addEventListener('click', () => {
                const config = input.value.trim();
                if (!config) {
                    alert('OpenAI API Key cannot be empty.');
                    return;
                }
                setMode(mode, config);
            });
        }
    }

    async function setMode(mode, config) {
        try {
            const response = await fetch('/set_mode', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ mode: mode, config: config })
            });
            const data = await response.json();
            console.log('Set mode response:', data);
            if (data.status === 'success') {
                alert(`${mode} has been set.`);
            } else {
                alert(data.error || 'An error occurred while setting the mode.');
            }
        } catch (error) {
            console.error('Error setting mode:', error);
            alert('An error occurred while setting the mode.');
        }
    }

    modeSelect.addEventListener('change', (e) => {
        const selected = e.target.value;
        selectedMode = selected;
        displayModeConfig(selected);
    });

    async function loadAvailableTools() {
        try {
            const response = await fetch('/get_available_tools');
            const data = await response.json();
            console.log('Available tools:', data);
            if (data.tools) {
                renderAvailableTools(data.tools);
            }
        } catch (error) {
            console.error('Error loading available tools:', error);
        }
    }

    function renderAvailableTools(tools) {
        toolsContainer.innerHTML = '';
        tools.forEach(tool => {
            const toolDiv = document.createElement('div');
            toolDiv.classList.add('tool');

            const toolName = document.createElement('div');
            toolName.classList.add('tool-name');
            toolName.textContent = tool.name;

            const toolDesc = document.createElement('div');
            toolDesc.classList.add('tool-description');
            toolDesc.textContent = tool.description;

            toolDiv.appendChild(toolName);
            toolDiv.appendChild(toolDesc);
            toolsContainer.appendChild(toolDiv);
        });
    }

    async function loadMessages() {
        try {
            const response = await fetch('/get_messages');
            const data = await response.json();
            console.log('Loaded messages:', data);
            if (data.messages) {
                renderMessages(data.messages);
            }
        } catch (error) {
            console.error('Error loading messages:', error);
        }
    }

    function renderMessages(messages) {
        chatMessages.innerHTML = '';
        messages.forEach(msg => {
            appendMessage(msg.text, msg.sender, false);
        });
        chatMessages.scrollTop = chatMessages.scrollHeight; 
    }

    function appendMessage(text, sender, shouldScroll = true) {
        const msgDiv = document.createElement('div');
        msgDiv.classList.add('message', sender);
        msgDiv.textContent = text;
        chatMessages.appendChild(msgDiv);
        if (shouldScroll) {
            chatMessages.scrollTop = chatMessages.scrollHeight; 
        }
        console.log(`Appended message from ${sender}:`, text);
    }

    async function sendMessage() {
        const message = userInput.value.trim();
        if (message === '') return;

        appendMessage(message, 'user');
        userInput.value = '';

        appendMessage('正在思考...', 'bot');
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ message: message })
            });
            const data = await response.json();
            console.log('Chat response:', data);

            const botMessages = chatMessages.querySelectorAll('.bot');
            if (botMessages.length > 0) {
                botMessages[botMessages.length - 1].remove();
                console.log('Removed waiting animation.');
            }

            if (data.response) {
                appendMessage(data.response, 'bot');
            } else {
                appendMessage('An error occurred, please try again later.', 'bot');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            const botMessages = chatMessages.querySelectorAll('.bot');
            if (botMessages.length > 0) {
                botMessages[botMessages.length - 1].remove();
            }
            appendMessage('Request failed, please check network connection or backend service status.', 'bot');
        }
    }

    sendBtn.addEventListener('click', sendMessage);

    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    loadAvailableTools();
    loadMessages();
});
