/**
 * Client-side JavaScript for Amazon Product Analysis
 * Integrates with the backend API and Redis pub/sub via WebSockets
 */

// Backend API URL
const BACKEND_API_URL = 'http://localhost:8000';

document.addEventListener('DOMContentLoaded', function() {
    // Elements - Subscribe form
    const subscribeForm = document.getElementById('subscribeForm');
    const taskIdInput = document.getElementById('taskId');
    const unsubscribeBtn = document.getElementById('unsubscribeBtn');
    const messagesContainer = document.getElementById('messagesContainer');
    const statusIndicator = document.getElementById('statusIndicator');
    const connectionStatus = document.getElementById('connectionStatus');
    const channelHeader = document.getElementById('channelHeader');
    const currentTaskId = document.getElementById('currentTaskId');
    
    // Elements - Analysis form
    const analysisForm = document.getElementById('analysisForm');
    const amazonUrlInput = document.getElementById('amazonUrl');
    const maxProductsInput = document.getElementById('maxProducts');
    const maxCompetitiveInput = document.getElementById('maxCompetitive');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const taskAlert = document.getElementById('taskAlert');
    const createdTaskId = document.getElementById('createdTaskId');
    const taskStatus = document.getElementById('taskStatus');
    
    // Connect to Socket.IO server
    const socket = io();
    let currentSubscription = null;
    
    // Socket connection status handling
    socket.on('connect', () => {
        updateConnectionStatus(true);
    });
    
    socket.on('disconnect', () => {
        updateConnectionStatus(false);
    });
    
    // Handle subscription events
    socket.on('subscribed', (channel) => {
        console.log(`Successfully subscribed to ${channel}`);
        currentSubscription = channel.replace('product_analysis_', '');
        updateSubscriptionUI(true);
        
        // Clear previous messages
        clearMessages();
        
        // Show welcome message
        addSystemMessage(`Subscribed to messages for task: ${currentSubscription}`);
    });
    
    socket.on('unsubscribed', () => {
        currentSubscription = null;
        updateSubscriptionUI(false);
        clearMessages();
        addSystemMessage('Unsubscribed from task messages');
    });
    
    // Handle incoming messages
    socket.on('message', (data) => {
        addMessage(data);
    });
    
    // Backend API functions
    async function submitProductAnalysis(url, maxProducts = 5, maxCompetitive = 3) {
        try {
            const response = await fetch(`${BACKEND_API_URL}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    url: url,
                    max_products: parseInt(maxProducts),
                    max_competitive: parseInt(maxCompetitive)
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error submitting product analysis:', error);
            throw error;
        }
    }
    
    async function checkTaskStatus(taskId) {
        try {
            const response = await fetch(`${BACKEND_API_URL}/task/${taskId}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error checking task status:', error);
            throw error;
        }
    }
    
    // Analysis form submission
    analysisForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const amazonUrl = amazonUrlInput.value.trim();
        const maxProducts = maxProductsInput.value;
        const maxCompetitive = maxCompetitiveInput.value;
        
        if (!amazonUrl) return;
        
        // Show loading state
        analyzeBtn.disabled = true;
        loadingSpinner.classList.remove('d-none');
        taskAlert.classList.add('d-none');
        
        try {
            // Submit analysis request to backend
            const response = await submitProductAnalysis(amazonUrl, maxProducts, maxCompetitive);
            
            // Display task ID
            createdTaskId.textContent = response.task_id;
            taskStatus.textContent = response.status;
            taskAlert.classList.remove('d-none');
            
            // Auto-subscribe to task messages
            if (currentSubscription && currentSubscription !== response.task_id) {
                socket.emit('unsubscribe', currentSubscription);
            }
            socket.emit('subscribe', response.task_id);
            
            // Start polling task status
            pollTaskStatus(response.task_id);
            
        } catch (error) {
            alert(`Error: ${error.message || 'Failed to submit analysis request'}`);
        } finally {
            // Reset form state
            analyzeBtn.disabled = false;
            loadingSpinner.classList.add('d-none');
        }
    });
    
    // Manual subscription form
    subscribeForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const taskId = taskIdInput.value.trim();
        
        if (taskId) {
            // If already subscribed to something else, unsubscribe first
            if (currentSubscription && currentSubscription !== taskId) {
                socket.emit('unsubscribe', currentSubscription);
            }
            
            // Subscribe to the new task ID
            socket.emit('subscribe', taskId);
        }
    });
    
    // Unsubscribe button
    unsubscribeBtn.addEventListener('click', function() {
        if (currentSubscription) {
            socket.emit('unsubscribe', currentSubscription);
        }
    });
    
    // Helper functions
    function updateConnectionStatus(isConnected) {
        statusIndicator.className = `status-indicator ${isConnected ? 'connected' : 'disconnected'}`;
        connectionStatus.textContent = isConnected ? 'Connected to server' : 'Disconnected';
    }
    
    function updateSubscriptionUI(isSubscribed) {
        unsubscribeBtn.disabled = !isSubscribed;
        channelHeader.style.display = isSubscribed ? 'block' : 'none';
        
        if (isSubscribed) {
            currentTaskId.textContent = currentSubscription;
        }
    }
    
    function addMessage(data) {
        // Check if the welcome message is still there
        if (messagesContainer.querySelector('.text-center')) {
            clearMessages();
        }
        
        const messageItem = document.createElement('div');
        messageItem.className = 'message-item';
        
        const timestamp = new Date(data.timestamp);
        const formattedTime = timestamp.toLocaleTimeString();
        
        messageItem.innerHTML = `
            <div>
                <span class="agent-name">${data.agent}:</span> ${data.message}
            </div>
            <div class="timestamp">${formattedTime}</div>
        `;
        
        // Add to container and scroll to bottom
        messagesContainer.appendChild(messageItem);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    // Poll task status every 5 seconds
    async function pollTaskStatus(taskId) {
        let intervalId = setInterval(async () => {
            try {
                const statusResponse = await checkTaskStatus(taskId);
                taskStatus.textContent = statusResponse.status;
                
                // Stop polling if task completed or failed
                if (['success', 'error'].includes(statusResponse.status)) {
                    clearInterval(intervalId);
                    
                    // Display completion message
                    if (statusResponse.status === 'success') {
                        addSystemMessage('Analysis completed successfully!');
                    } else {
                        addSystemMessage(`Analysis failed: ${statusResponse.result?.error || 'Unknown error'}`);
                    }
                }
            } catch (error) {
                console.error('Error polling task status:', error);
            }
        }, 5000);
    }
    
    function addSystemMessage(text) {
        const messageItem = document.createElement('div');
        messageItem.className = 'message-item';
        
        messageItem.innerHTML = `
            <div>
                <span class="agent-name">System:</span> ${text}
            </div>
            <div class="timestamp">${new Date().toLocaleTimeString()}</div>
        `;
        
        messagesContainer.appendChild(messageItem);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    function clearMessages() {
        messagesContainer.innerHTML = '';
    }
});
