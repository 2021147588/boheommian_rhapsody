// Global variables
let simulationResults = null;
let activeSection = 'dashboard-section';
const charts = {};

// DOM Elements
document.addEventListener('DOMContentLoaded', () => {
    // Initialize UI
    initUI();
    
    // Event listeners
    setupEventListeners();
});

// Initialize UI components
function initUI() {
    // Set up empty charts
    initCharts();
    
    // Check for dark mode preference
    if (localStorage.getItem('darkMode') === 'true') {
        document.body.classList.add('dark-theme');
        document.querySelector('.theme-toggle i').classList.remove('fa-moon');
        document.querySelector('.theme-toggle i').classList.add('fa-sun');
    }
}

// Initialize charts with empty data
function initCharts() {
    // Agent activity chart
    const agentActivityCtx = document.getElementById('agent-activity-chart').getContext('2d');
    charts.agentActivity = new Chart(agentActivityCtx, {
        type: 'doughnut',
        data: {
            labels: ['Router', 'Recommendation', 'Sales', 'RAG'],
            datasets: [{
                data: [0, 0, 0, 0],
                backgroundColor: ['#4a6bff', '#28a745', '#ffc107', '#17a2b8'],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right'
                }
            }
        }
    });
    
    // Success by turn chart
    const successByTurnCtx = document.getElementById('success-by-turn-chart').getContext('2d');
    charts.successByTurn = new Chart(successByTurnCtx, {
        type: 'bar',
        data: {
            labels: ['Turn 1', 'Turn 2', 'Turn 3', 'Turn 4', 'Turn 5'],
            datasets: [{
                label: '성공률',
                data: [0, 0, 0, 0, 0],
                backgroundColor: '#4a6bff',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });
    
    // Plan distribution chart
    const planDistributionCtx = document.getElementById('plan-distribution-chart').getContext('2d');
    charts.planDistribution = new Chart(planDistributionCtx, {
        type: 'pie',
        data: {
            labels: ['고급형', '표준형', '3400형'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: ['#28a745', '#4a6bff', '#ffc107'],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right'
                }
            }
        }
    });
    
    // Agent transitions chart
    const agentTransitionsCtx = document.getElementById('agent-transitions-chart').getContext('2d');
    charts.agentTransitions = new Chart(agentTransitionsCtx, {
        type: 'bar',
        data: {
            labels: ['Router → Rec', 'Rec → Sales', 'Rec → RAG', 'RAG → Sales', 'Sales → RAG'],
            datasets: [{
                label: '전환 횟수',
                data: [0, 0, 0, 0, 0],
                backgroundColor: '#4a6bff',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
    
    // Success by characteristics chart
    const successByCharacteristicsCtx = document.getElementById('success-by-characteristics-chart').getContext('2d');
    charts.successByCharacteristics = new Chart(successByCharacteristicsCtx, {
        type: 'radar',
        data: {
            labels: ['사고이력', '운전경력 많음', '고가 차량', '여성', '젊은층'],
            datasets: [{
                label: '성공',
                data: [0, 0, 0, 0, 0],
                backgroundColor: 'rgba(40, 167, 69, 0.2)',
                borderColor: '#28a745',
                borderWidth: 2,
                pointBackgroundColor: '#28a745'
            }, {
                label: '실패',
                data: [0, 0, 0, 0, 0],
                backgroundColor: 'rgba(220, 53, 69, 0.2)',
                borderColor: '#dc3545',
                borderWidth: 2,
                pointBackgroundColor: '#dc3545'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    min: 0,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });
}

// Set up event listeners
function setupEventListeners() {
    // Menu item click
    document.querySelectorAll('.menu-item').forEach(item => {
        item.addEventListener('click', () => {
            const targetSection = item.getAttribute('data-target');
            switchSection(targetSection);
        });
    });
    
    // Theme toggle
    document.querySelector('.theme-toggle').addEventListener('click', toggleTheme);
    
    // File input change
    const fileInput = document.getElementById('file-input');
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drop area for file
    const dropArea = document.getElementById('drop-area');
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    dropArea.addEventListener('dragenter', () => dropArea.classList.add('highlight'), false);
    dropArea.addEventListener('dragover', () => dropArea.classList.add('highlight'), false);
    dropArea.addEventListener('dragleave', () => dropArea.classList.remove('highlight'), false);
    dropArea.addEventListener('drop', () => dropArea.classList.remove('highlight'), false);
    
    dropArea.addEventListener('drop', handleDrop, false);
    
    // Simulate button click
    document.getElementById('run-simulation-btn').addEventListener('click', runSimulation);
    
    // View details button
    document.getElementById('view-details-btn').addEventListener('click', () => {
        openModal('detail-modal');
    });
    
    // Customer select change
    document.getElementById('customer-select').addEventListener('change', handleCustomerSelect);
    
    // Close modal buttons
    document.querySelectorAll('.close-modal').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.modal').forEach(modal => {
                modal.classList.remove('active');
            });
        });
    });
}

// Switch between sections
function switchSection(targetSection) {
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    
    document.querySelectorAll('.menu-item').forEach(item => {
        item.classList.remove('active');
    });
    
    document.getElementById(targetSection).classList.add('active');
    document.querySelector(`[data-target="${targetSection}"]`).classList.add('active');
    
    activeSection = targetSection;
}

// Toggle between light and dark theme
function toggleTheme() {
    const isDark = document.body.classList.toggle('dark-theme');
    const icon = document.querySelector('.theme-toggle i');
    
    if (isDark) {
        icon.classList.remove('fa-moon');
        icon.classList.add('fa-sun');
    } else {
        icon.classList.remove('fa-sun');
        icon.classList.add('fa-moon');
    }
    
    localStorage.setItem('darkMode', isDark);
    
    // Update chart colors if needed
    if (simulationResults) {
        updateChartsWithData(simulationResults);
    }
}

// Handle file selection
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        if (file.name.endsWith('.json')) {
            document.getElementById('file-name').textContent = file.name;
            document.getElementById('run-simulation-btn').disabled = false;
        } else {
            alert('Please upload a .json file');
            document.getElementById('file-input').value = '';
            document.getElementById('file-name').textContent = '';
            document.getElementById('run-simulation-btn').disabled = true;
        }
    }
}

// Handle file drop
function handleDrop(e) {
    const dt = e.dataTransfer;
    const file = dt.files[0];
    
    if (file && file.name.endsWith('.json')) {
        document.getElementById('file-input').files = dt.files;
        document.getElementById('file-name').textContent = file.name;
        document.getElementById('run-simulation-btn').disabled = false;
    } else {
        alert('Please upload a .json file');
    }
}

// Run simulation with selected file
async function runSimulation() {
    const fileInput = document.getElementById('file-input');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Please select a file first');
        return;
    }
    
    try {
        // Show progress bar
        document.querySelector('.simulation-progress').style.display = 'block';
        document.querySelector('.simulation-results').style.display = 'none';
        
        // Get max turns and sample count
        const maxTurns = parseInt(document.getElementById('max-turns').value);
        const maxSamples = parseInt(document.getElementById('sample-count').value) || 10; // 값이 0이면 기본값 10 사용
        
        // Create FormData object
        const formData = new FormData();
        formData.append('file', file);
        formData.append('max_turns', maxTurns);
        formData.append('max_samples', maxSamples);
        
        // Update progress
        updateProgressBar(10, '파일 분석 완료, 서버로 전송 중...');
        
        // Send to server using the /submit API
        const response = await fetch('/submit', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        updateProgressBar(50, '시뮬레이션 실행 중...');
        
        // Get response data
        const result = await response.json();
        
        // Update progress
        updateProgressBar(90, '데이터 처리 중...');
        
        // Process and display results
        processResults(result);
        
        // Complete progress
        updateProgressBar(100, '완료!');
        setTimeout(() => {
            document.querySelector('.simulation-progress').style.display = 'none';
            document.querySelector('.simulation-results').style.display = 'block';
        }, 500);
        
    } catch (error) {
        console.error('Simulation error:', error);
        alert(`시뮬레이션 실행 중 오류가 발생했습니다: ${error.message}`);
        document.querySelector('.simulation-progress').style.display = 'none';
    }
}

// Read file as text
function readFile(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = event => resolve(event.target.result);
        reader.onerror = error => reject(error);
        reader.readAsText(file);
    });
}

// Update progress bar
function updateProgressBar(percent, message) {
    document.getElementById('simulation-progress-bar').style.width = `${percent}%`;
    document.getElementById('progress-status').textContent = `${percent}% ${message}`;
}

// Process simulation results
function processResults(data) {
    // Store results globally
    simulationResults = data.data;
    
    // Hide progress, show results
    document.querySelector('.simulation-progress').style.display = 'none';
    document.querySelector('.simulation-results').style.display = 'block';
    
    // Update summary
    document.getElementById('result-total').textContent = data.data.summary.total_samples;
    document.getElementById('result-success').textContent = Array.from(data.data.summary.success_count)[0];
    document.getElementById('result-rate').textContent = `${data.data.summary.success_rate.toFixed(1)}%`;
    
    // Update dashboard metrics
    document.getElementById('total-customers').textContent = data.data.summary.total_samples;
    document.getElementById('success-count').textContent = Array.from(data.data.summary.success_count)[0];
    document.getElementById('success-rate').textContent = `${data.data.summary.success_rate.toFixed(1)}%`;
    document.getElementById('last-run').textContent = formatTimestamp(data.data.summary.timestamp);
    
    // Update charts
    updateChartsWithData(data.data);
    
    // Update simulations table
    updateSimulationsTable(data.data);
    
    // Update customer dropdown for conversation viewer
    updateCustomerDropdown(data.data);
    
    // Update customer dropdown for final report visualization
    updateReportCustomerDropdown(data.data);
}

// Update charts with actual data
function updateChartsWithData(data) {
    // Calculate agent activity data
    const agentCounts = { Router: 0, Recommendation: 0, Sales: 0, RAG: 0 };
    
    // Calculate plan distribution
    const planCounts = { '고급형': 0, '표준형': 0, '3400형': 0 };
    
    // Calculate agent transitions
    const transitions = {
        'Router → Rec': 0,
        'Rec → Sales': 0,
        'Rec → RAG': 0,
        'RAG → Sales': 0,
        'Sales → RAG': 0
    };
    
    // Success by turn
    const successByTurn = [0, 0, 0, 0, 0];
    const totalByTurn = [0, 0, 0, 0, 0];
    
    // Success by characteristics
    const characteristicsSuccess = {
        'accident': { success: 0, total: 0 },
        'experienced': { success: 0, total: 0 },
        'luxury': { success: 0, total: 0 },
        'female': { success: 0, total: 0 },
        'young': { success: 0, total: 0 }
    };
    
    // Process each conversation
    data.conversations.forEach(conv => {
        // Process turns for agent activity
        let prevAgent = null;
        
        if (conv.turns) {
            conv.turns.forEach(turn => {
                // Agent activity
                const agent = turn.current_agent;
                if (agent && agentCounts[agent] !== undefined) {
                    agentCounts[agent]++;
                }
                
                // Agent transitions
                if (prevAgent && agent) {
                    const transitionKey = `${prevAgent} → ${agent}`;
                    if (transitions[transitionKey] !== undefined) {
                        transitions[transitionKey]++;
                    }
                }
                prevAgent = agent;
                
                // Success by turn
                if (turn.turn <= 5) {
                    totalByTurn[turn.turn - 1]++;
                    if (conv.success) {
                        successByTurn[turn.turn - 1]++;
                    }
                }
            });
        }
        
        // Extract recommended plan type from conversation
        if (conv.turns) {
            for (const turn of conv.turns) {
                const response = turn.agent_response || '';
                
                if (response.includes('고급형')) {
                    planCounts['고급형']++;
                    break;
                } else if (response.includes('표준형')) {
                    planCounts['표준형']++;
                    break;
                } else if (response.includes('3400형')) {
                    planCounts['3400형']++;
                    break;
                }
            }
        }
        
        // Process user characteristics
        if (conv.user_info) {
            // Accident history
            if (conv.user_info.user?.accident_history) {
                characteristicsSuccess.accident.total++;
                if (conv.success) characteristicsSuccess.accident.success++;
            }
            
            // Driving experience (>15 years is "experienced")
            if (conv.user_info.driving_experience > 15) {
                characteristicsSuccess.experienced.total++;
                if (conv.success) characteristicsSuccess.experienced.success++;
            }
            
            // Luxury car (>30M won)
            if (conv.user_info.vehicle?.market_value > 30000000) {
                characteristicsSuccess.luxury.total++;
                if (conv.success) characteristicsSuccess.luxury.success++;
            }
            
            // Gender
            if (conv.user_info.gender === '여성') {
                characteristicsSuccess.female.total++;
                if (conv.success) characteristicsSuccess.female.success++;
            }
            
            // Age (below 30 is "young")
            const birthYear = parseInt(conv.user_info.birth_date?.substring(0, 4));
            if (birthYear && birthYear > 1990) {
                characteristicsSuccess.young.total++;
                if (conv.success) characteristicsSuccess.young.success++;
            }
        }
    });
    
    // Update agent activity chart
    charts.agentActivity.data.datasets[0].data = [
        agentCounts.Router,
        agentCounts.Recommendation,
        agentCounts.Sales,
        agentCounts.RAG
    ];
    charts.agentActivity.update();
    
    // Update plan distribution chart
    charts.planDistribution.data.datasets[0].data = [
        planCounts['고급형'],
        planCounts['표준형'],
        planCounts['3400형']
    ];
    charts.planDistribution.update();
    
    // Update agent transitions chart
    charts.agentTransitions.data.datasets[0].data = [
        transitions['Router → Rec'],
        transitions['Rec → Sales'],
        transitions['Rec → RAG'],
        transitions['RAG → Sales'],
        transitions['Sales → RAG']
    ];
    charts.agentTransitions.update();
    
    // Update success by turn chart
    const successRateByTurn = totalByTurn.map((total, i) => {
        return total > 0 ? (successByTurn[i] / total * 100) : 0;
    });
    
    charts.successByTurn.data.datasets[0].data = successRateByTurn;
    charts.successByTurn.update();
    
    // Update characteristics chart
    const characteristicsData = {
        success: [
            calculatePercentage(characteristicsSuccess.accident.success, characteristicsSuccess.accident.total),
            calculatePercentage(characteristicsSuccess.experienced.success, characteristicsSuccess.experienced.total),
            calculatePercentage(characteristicsSuccess.luxury.success, characteristicsSuccess.luxury.total),
            calculatePercentage(characteristicsSuccess.female.success, characteristicsSuccess.female.total),
            calculatePercentage(characteristicsSuccess.young.success, characteristicsSuccess.young.total)
        ],
        failed: [
            calculatePercentage(characteristicsSuccess.accident.total - characteristicsSuccess.accident.success, characteristicsSuccess.accident.total),
            calculatePercentage(characteristicsSuccess.experienced.total - characteristicsSuccess.experienced.success, characteristicsSuccess.experienced.total),
            calculatePercentage(characteristicsSuccess.luxury.total - characteristicsSuccess.luxury.success, characteristicsSuccess.luxury.total),
            calculatePercentage(characteristicsSuccess.female.total - characteristicsSuccess.female.success, characteristicsSuccess.female.total),
            calculatePercentage(characteristicsSuccess.young.total - characteristicsSuccess.young.success, characteristicsSuccess.young.total)
        ]
    };
    
    charts.successByCharacteristics.data.datasets[0].data = characteristicsData.success;
    charts.successByCharacteristics.data.datasets[1].data = characteristicsData.failed;
    charts.successByCharacteristics.update();
}

// Calculate percentage safely
function calculatePercentage(part, total) {
    return total > 0 ? (part / total * 100) : 0;
}

// Update simulations table
function updateSimulationsTable(data) {
    const tableBody = document.querySelector('#recent-simulations-table tbody');
    tableBody.innerHTML = '';
    
    data.conversations.forEach((conv, index) => {
        if (!conv.user_info || conv.error) return;
        
        const row = document.createElement('tr');
        
        // Get recommended plan
        let recommendedPlan = '미정';
        if (conv.turns) {
            for (const turn of conv.turns) {
                const response = turn.agent_response || '';
                if (response.includes('고급형')) {
                    recommendedPlan = '고급형';
                    break;
                } else if (response.includes('표준형')) {
                    recommendedPlan = '표준형';
                    break;
                } else if (response.includes('3400형')) {
                    recommendedPlan = '3400형';
                    break;
                }
            }
        }
        
        // Create cells
        const cells = [
            conv.user_info.name || `고객 ${index + 1}`,
            calculateAge(conv.user_info.birth_date) || '-',
            conv.user_info.vehicle_model || '-',
            recommendedPlan,
            conv.success ? '성공' : '실패',
            conv.turns ? conv.turns.length : '-'
        ];
        
        cells.forEach(cellText => {
            const td = document.createElement('td');
            td.textContent = cellText;
            
            // Add success/failure class
            if (cellText === '성공') {
                td.style.color = 'var(--success-color)';
                td.style.fontWeight = 'bold';
            } else if (cellText === '실패') {
                td.style.color = 'var(--danger-color)';
                td.style.fontWeight = 'bold';
            }
            
            row.appendChild(td);
        });
        
        tableBody.appendChild(row);
    });
}

// Calculate age from birth date
function calculateAge(birthDate) {
    if (!birthDate) return null;
    
    const year = parseInt(birthDate.substring(0, 4));
    const currentYear = new Date().getFullYear();
    
    return currentYear - year;
}

// Update customer dropdown
function updateCustomerDropdown(data) {
    const select = document.getElementById('customer-select');
    select.innerHTML = '<option value="">고객을 선택하세요</option>';
    
    data.conversations.forEach((conv, index) => {
        if (!conv.user_info || conv.error) return;
        
        const option = document.createElement('option');
        option.value = index;
        option.textContent = `${conv.user_info.name || `고객 ${index + 1}`} (${conv.success === true ? '성공' : '실패'})`;
        select.appendChild(option);
    });
}

// Handle customer selection
function handleCustomerSelect(e) {
    const selectedIndex = e.target.value;
    
    if (!selectedIndex || !simulationResults) {
        // Clear conversation and info panels
        document.getElementById('customer-info').innerHTML = '<p>고객을 선택하면 정보가 표시됩니다.</p>';
        document.getElementById('chat-messages').innerHTML = '<p class="empty-message">고객을 선택하면 대화 내역이 표시됩니다.</p>';
        document.getElementById('agent-activity').innerHTML = '<p>고객을 선택하면 에이전트 활동이 표시됩니다.</p>';
        document.getElementById('agent-switches').textContent = '0';
        document.getElementById('rag-count').textContent = '0';
        document.getElementById('conversation-status').textContent = '대기 중';
        document.getElementById('conversation-status').className = 'status-badge';
        return;
    }
    
    console.log('Selected index:', selectedIndex);
    console.log('Simulation results:', simulationResults);
    
    const conversation = simulationResults.conversations[selectedIndex];
    console.log('Selected conversation:', conversation);
    
    // Update customer info panel
    updateCustomerInfoPanel(conversation);
    
    // Update chat messages
    updateChatMessages(conversation);
    
    // Update agent activity
    updateAgentActivity(conversation);
    
    // Update conversation status
    document.getElementById('conversation-status').textContent = conversation.success ? '성공' : '실패';
    document.getElementById('conversation-status').className = conversation.success ? 'status-badge success' : 'status-badge failed';
}

// Update customer info panel
function updateCustomerInfoPanel(conversation) {
    if (!conversation || !conversation.user_info) {
        console.log('No conversation or user_info found:', conversation);
        return;
    }
    
    const info = conversation.user_info.user;
    const vehicle = conversation.user_info.vehicle;
    const customerInfo = document.getElementById('customer-info');
    console.log(conversation.user_info)
    let html = `
        <div class="info-item">
            <strong>이름:</strong> ${info.name || '-'}
        </div>
        <div class="info-item">
            <strong>생년월일:</strong> ${info.birth_date || '-'}
        </div>
        <div class="info-item">
            <strong>성별:</strong> ${info.gender || '-'}
        </div>
        <div class="info-item">
            <strong>운전 경력:</strong> ${info.driving_experience_years || '-'}년
        </div>
        <div class="info-item">
            <strong>차량:</strong> ${vehicle?.model || '-'}
        </div>
        <div class="info-item">
            <strong>사용 목적:</strong> ${vehicle?.usage || '-'}
        </div>
    `;
    
    customerInfo.innerHTML = html;
}

// Update chat messages
function updateChatMessages(conversation) {
    if (!conversation || !conversation.turns) {
        return;
    }
    
    const chatMessages = document.getElementById('chat-messages');
    chatMessages.innerHTML = '';
    
    // 첫 번째 턴 처리 - 사용자 메시지가 먼저 와야 함
    if (conversation.turns.length > 0) {
        const firstTurn = conversation.turns[0];
        
        // 첫 번째 턴의 사용자 메시지 표시
        // if (firstTurn.user_reply) {
        //     addUserMessage(chatMessages, firstTurn.user_reply);
        // }
        
        // // 첫 번째 턴의 에이전트 응답 표시
        // if (firstTurn.agent_response) {
        //     addAgentMessage(chatMessages, firstTurn.agent_response, firstTurn.current_agent);
        // }
        
        // 두 번째 턴부터 처리 - 에이전트 응답 후 사용자 응답 순서
        for (let i = 0; i < conversation.turns.length; i++) {
            const turn = conversation.turns[i];
            
            // 사용자 응답 표시
            addUserMessage(chatMessages, turn.user_reply);
            
            addAgentMessage(chatMessages, turn.agent_response, turn.current_agent);
            
        }
    }
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 사용자 메시지 추가 헬퍼 함수
function addUserMessage(container, message) {
    const userMessage = document.createElement('div');
    userMessage.className = 'message user';
    
    const sender = document.createElement('div');
    sender.className = 'sender';
    sender.textContent = '고객';
    
    const content = document.createElement('div');
    content.className = 'content';
    content.textContent = message;
    
    userMessage.appendChild(sender);
    userMessage.appendChild(content);
    container.appendChild(userMessage);
}

// 에이전트 메시지 추가 헬퍼 함수
function addAgentMessage(container, message, agentType) {
    const agentMessage = document.createElement('div');
    agentMessage.className = 'message agent';
    
    const sender = document.createElement('div');
    sender.className = 'sender';
    sender.textContent = `${agentType} 에이전트`;
    
    const content = document.createElement('div');
    content.className = 'content';
    content.textContent = message;
    
    agentMessage.appendChild(sender);
    agentMessage.appendChild(content);
    container.appendChild(agentMessage);
}

// Update agent activity
function updateAgentActivity(conversation) {
    if (!conversation || !conversation.turns) {
        return;
    }
    
    const agentActivity = document.getElementById('agent-activity');
    agentActivity.innerHTML = '';
    
    // Count agent types and transitions
    const agentCounts = { Router: 0, Recommendation: 0, Sales: 0, RAG: 0 };
    let prevAgent = null;
    let agentSwitches = 0;
    let ragCount = 0;
    
    conversation.turns.forEach(turn => {
        const agent = turn.current_agent;
        
        if (agent && agentCounts[agent] !== undefined) {
            agentCounts[agent]++;
            
            if (prevAgent && prevAgent !== agent) {
                agentSwitches++;
            }
            
            prevAgent = agent;
        }
        
        if (turn.rag_performed) {
            ragCount++;
        }
    });
    
    // Create pie chart for agent activity
    const canvas = document.createElement('canvas');
    canvas.id = 'individual-agent-chart';
    agentActivity.appendChild(canvas);
    
    const ctx = canvas.getContext('2d');
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: Object.keys(agentCounts),
            datasets: [{
                data: Object.values(agentCounts),
                backgroundColor: ['#4a6bff', '#28a745', '#ffc107', '#17a2b8'],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
    
    // Update agent stats
    document.getElementById('agent-switches').textContent = agentSwitches;
    document.getElementById('rag-count').textContent = ragCount;
}

// Prepare detail modal content
function prepareDetailModalContent(data) {
    const detailContent = document.getElementById('detail-content');
    
    let html = `
        <div class="detail-summary">
            <h3>시뮬레이션 요약</h3>
            <div class="summary-stats">
                <div class="stat-box">
                    <span class="label">총 고객</span>
                    <span class="value">${data.summary.total_samples}</span>
                </div>
                <div class="stat-box">
                    <span class="label">성공</span>
                    <span class="value">${data.summary.success_count}</span>
                </div>
                <div class="stat-box">
                    <span class="label">성공률</span>
                    <span class="value">${data.summary.success_rate.toFixed(1)}%</span>
                </div>
                <div class="stat-box">
                    <span class="label">실행 시간</span>
                    <span class="value">${data.summary.timestamp}</span>
                </div>
            </div>
        </div>
    `;
    
    detailContent.innerHTML = html;
}

// Open a modal by ID
function openModal(modalId) {
    document.getElementById(modalId).classList.add('active');
}

// After the handleCustomerSelect function, add the functions for final report visualization
function updateReportCustomerDropdown(data) {
    const reportCustomerSelect = document.getElementById('report-customer-select');
    reportCustomerSelect.innerHTML = '<option value="">고객을 선택하세요</option>';
    
    if (!data || !data.conversations || data.conversations.length === 0) {
        return;
    }
    
    data.conversations.forEach((conversation, index) => {
        const userInfo = conversation.user_info.user;
        const option = document.createElement('option');
        option.value = index;
        option.textContent = `${userInfo.name} (${userInfo.gender}, ${calculateAge(userInfo.birth_date)}세)`;
        reportCustomerSelect.appendChild(option);
    });
    
    reportCustomerSelect.addEventListener('change', handleReportCustomerSelect);
}

function handleReportCustomerSelect(e) {
    const selectedIndex = e.target.value;
    
    if (!selectedIndex || !simulationResults || !simulationResults.conversations) {
        const reportContent = document.getElementById('report-content');
        reportContent.innerHTML = '<p class="empty-message">고객을 선택하면 최종 보고서가 표시됩니다.</p>';
        return;
    }
    
    const conversation = simulationResults.conversations[selectedIndex];
    renderFinalReport(conversation);
}

function renderFinalReport(conversation) {
    const reportContent = document.getElementById('report-content');
    
    // Check if final_report exists
    if (!conversation.final_report) {
        // Try to load from a result file if not in memory
        console.log("No final_report found in conversation data, attempting to load from file...");
        loadFinalReportFromFile(conversation, reportContent);
        return;
    }
    
    displayFinalReport(conversation, conversation.final_report, reportContent);
}

// 새 함수: 파일에서 final_report 데이터 로드
function loadFinalReportFromFile(conversation, reportContent) {
    const userInfo = conversation.user_info && conversation.user_info.user ? conversation.user_info.user : { name: "Unknown" };
    const userName = userInfo.name || "Unknown";
    
    // 임시로 로딩 메시지 표시
    reportContent.innerHTML = '<p class="loading-message">최종 보고서 데이터를 불러오는 중입니다...</p>';
    
    // 파일 경로 생성 (주의: 실제 경로는 서버 설정에 따라 달라질 수 있음)
    // 현재 JSON 파일은 database/result/ 디렉토리에 있을 것으로 가정
    fetch(`/load-report?name=${encodeURIComponent(userName)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('최종 보고서 데이터를 불러오는데 실패했습니다.');
            }
            return response.json();
        })
        .then(data => {
            if (data && data.final_report) {
                // 성공적으로 불러온 경우 데이터를 메모리에 저장하고 표시
                conversation.final_report = data.final_report;
                displayFinalReport(conversation, data.final_report, reportContent);
            } else {
                // 데이터를 찾을 수 없는 경우
                reportContent.innerHTML = '<p class="no-report-data">이 대화에 대한 최종 보고서 데이터를 찾을 수 없습니다.</p>';
            }
        })
        .catch(error => {
            console.error('Error loading final report:', error);
            reportContent.innerHTML = `<p class="error-message">최종 보고서 데이터를 불러오는 중 오류가 발생했습니다: ${error.message}</p>`;
        });
}

// 새 함수: 최종 보고서 표시 로직을 분리
function displayFinalReport(conversation, finalReport, reportContent) {
    const userInfo = conversation.user_info.user;
    
    // Create HTML for the report
    let html = `
        <div class="report-header">
            <h4>${userInfo.name}님의 최종 보고서</h4>
            <div class="report-actions">
                <button class="report-button" onclick="generateReportHTML(${JSON.stringify(conversation.id || '').replace(/"/g, '&quot;')})">
                    <i class="fas fa-file-export"></i> HTML 보고서 생성
                </button>
                <button class="report-button" onclick="downloadReportPDF(${JSON.stringify(conversation.id || '').replace(/"/g, '&quot;')})">
                    <i class="fas fa-file-pdf"></i> PDF 다운로드
                </button>
            </div>
        </div>
        <div class="report-visualization">
            <div class="report-summary-cards">
                <div class="report-card">
                    <div class="card-icon"><i class="fas fa-check-circle"></i></div>
                    <div class="card-content">
                        <h5>최종 결과</h5>
                        <div class="status-badge ${conversation.success ? 'success' : 'failed'}">${conversation.success ? '성공' : '실패'}</div>
                    </div>
                </div>
                <div class="report-card">
                    <div class="card-icon"><i class="fas fa-comment-dots"></i></div>
                    <div class="card-content">
                        <h5>대화 턴 수</h5>
                        <div class="card-value">${conversation.turns ? conversation.turns.length : 0}</div>
                    </div>
                </div>
                <div class="report-card">
                    <div class="card-icon"><i class="fas fa-smile"></i></div>
                    <div class="card-content">
                        <h5>만족도</h5>
                        <div class="satisfaction-display">
                            ${getSatisfactionDisplay(finalReport['사용자 만족도 추정'] || '알 수 없음')}
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="report-sections">
`;

    // Organize report items into sections
    const sections = organizeReportSections(finalReport);

    // Add each section to HTML
    Object.entries(sections).forEach(([sectionName, items]) => {
        html += `
                <div class="report-section">
                    <div class="section-header">
                        <h5>${sectionName}</h5>
                    </div>
                    <div class="section-content">
        `;

        // Add items for this section
        items.forEach(item => {
            let valueClass = '';
            
            // Apply special formatting for certain keys
            if (item.key === '사용자 만족도 추정') {
                valueClass = getSatisfactionClass(item.value);
            } else if (item.key === '주요 논점' || item.key === '핵심 고객 요구사항') {
                valueClass = 'highlight-item';
            } else if (item.key.includes('추천') || item.key.includes('제안')) {
                valueClass = 'recommendation-item';
            }
            
            html += `
                        <div class="report-item">
                            <div class="report-label">${item.key}</div>
                            <div class="report-value ${valueClass}">${formatReportValue(item.value)}</div>
                        </div>
            `;
        });

        html += `
                    </div>
                </div>
        `;
    });

    // Close the report sections div
    html += `
            </div>
        </div>
    `;
    
    reportContent.innerHTML = html;
    
    // Add visualization charts if applicable
    if (finalReport['상품 적합도 점수'] || finalReport['상담 성과 지표']) {
        renderReportCharts(finalReport, conversation);
    }
}

// Format report values for better display
function formatReportValue(value) {
    if (!value) return '정보 없음';
    
    // If value contains list items with - or * bullets, format as a list
    if (value.includes('- ') || value.includes('* ')) {
        const items = value.split(/\n/);
        let formattedValue = '<ul>';
        
        items.forEach(item => {
            const trimmedItem = item.trim();
            if (trimmedItem.startsWith('- ') || trimmedItem.startsWith('* ')) {
                formattedValue += `<li>${trimmedItem.substring(2)}</li>`;
            } else if (trimmedItem) {
                formattedValue += `<li>${trimmedItem}</li>`;
            }
        });
        
        formattedValue += '</ul>';
        return formattedValue;
    }
    
    // Format percentage values
    if (/\d+%/.test(value)) {
        return value.replace(/(\d+)%/g, '<span class="percentage">$1%</span>');
    }
    
    return value;
}

// Organize report items into logical sections
function organizeReportSections(finalReport) {
    const sections = {
        '고객 정보 요약': [],
        '상담 결과': [],
        '추천 상품 정보': [],
        '상담 분석': []
    };
    
    // Skip the conversation log
    Object.entries(finalReport).forEach(([key, value]) => {
        if (key === 'conversation_log') return;
        
        if (key.includes('고객') || key.includes('사용자') || key.includes('요구')) {
            sections['고객 정보 요약'].push({ key, value });
        } else if (key.includes('추천') || key.includes('상품') || key.includes('플랜')) {
            sections['추천 상품 정보'].push({ key, value });
        } else if (key.includes('문제점') || key.includes('개선') || key.includes('분석') || key.includes('제안')) {
            sections['상담 분석'].push({ key, value });
        } else {
            sections['상담 결과'].push({ key, value });
        }
    });
    
    // Remove empty sections
    Object.keys(sections).forEach(key => {
        if (sections[key].length === 0) {
            delete sections[key];
        }
    });
    
    return sections;
}

// Get satisfaction display based on text
function getSatisfactionDisplay(satisfactionText) {
    let level = 0;
    
    if (satisfactionText.includes('높') || satisfactionText.includes('만족')) {
        level = 3;
    } else if (satisfactionText.includes('중간') || satisfactionText.includes('보통')) {
        level = 2;
    } else if (satisfactionText.includes('낮') || satisfactionText.includes('불만족')) {
        level = 1;
    }
    
    let display = '';
    for (let i = 0; i < 3; i++) {
        if (i < level) {
            display += '<i class="fas fa-smile satisfaction-high"></i>';
        } else {
            display += '<i class="far fa-smile satisfaction-low"></i>';
        }
    }
    
    return display;
}

// Get CSS class for satisfaction level
function getSatisfactionClass(satisfactionText) {
    if (satisfactionText.includes('높') || satisfactionText.includes('만족')) {
        return 'satisfaction-badge satisfaction-high';
    } else if (satisfactionText.includes('중간') || satisfactionText.includes('보통')) {
        return 'satisfaction-badge satisfaction-medium';
    } else if (satisfactionText.includes('낮') || satisfactionText.includes('불만족')) {
        return 'satisfaction-badge satisfaction-low';
    }
    return '';
}

// Render charts for the report data
function renderReportCharts(finalReport, conversation) {
    // Add canvas elements for charts
    const reportContent = document.getElementById('report-content');
    const chartsContainer = document.createElement('div');
    chartsContainer.className = 'report-charts';
    chartsContainer.innerHTML = `
        <div class="report-chart-row">
            <div class="report-chart-container">
                <canvas id="product-fit-chart"></canvas>
            </div>
            <div class="report-chart-container">
                <canvas id="consultation-metrics-chart"></canvas>
            </div>
        </div>
    `;
    reportContent.appendChild(chartsContainer);
    
    // Extract product fit data if available
    if (finalReport['상품 적합도 점수'] || finalReport['상품 적합성']) {
        let productFitData = extractProductFitData(finalReport);
        renderProductFitChart(productFitData);
    }
    
    // Extract consultation metrics if available
    if (finalReport['상담 성과 지표'] || finalReport['대화 효율성']) {
        let metricsData = extractConsultationMetrics(finalReport, conversation);
        renderConsultationMetricsChart(metricsData);
    }
}

// Extract product fit data from the report
function extractProductFitData(finalReport) {
    // Try to find product fit data in various possible keys
    let fitDataText = finalReport['상품 적합도 점수'] || 
                      finalReport['상품 적합성'] || 
                      finalReport['추천 상품 적합도'];
    
    if (!fitDataText) return null;
    
    // Default data if we can't parse from text
    const defaultData = [
        { name: '고급형', score: 70 },
        { name: '표준형', score: 50 },
        { name: '3400형', score: 30 }
    ];
    
    // Try to extract percentages or scores from text
    const percentageMatches = fitDataText.match(/(\d+)%/g);
    const scoreMatches = fitDataText.match(/(\d+)[^%]/g);
    
    if (percentageMatches && percentageMatches.length > 0) {
        // Extract plan names too if possible
        const planMatches = fitDataText.match(/(고급형|표준형|3400형|기본형)/g);
        
        return percentageMatches.map((percent, index) => {
            return {
                name: planMatches && planMatches[index] ? planMatches[index] : `상품 ${index + 1}`,
                score: parseInt(percent)
            };
        });
    } else if (scoreMatches && scoreMatches.length > 0) {
        // Try score format
        const planMatches = fitDataText.match(/(고급형|표준형|3400형|기본형)/g);
        
        return scoreMatches.map((score, index) => {
            return {
                name: planMatches && planMatches[index] ? planMatches[index] : `상품 ${index + 1}`,
                score: parseInt(score)
            };
        });
    }
    
    return defaultData;
}

// Extract consultation metrics from the report
function extractConsultationMetrics(finalReport, conversation) {
    // Try to find metrics in various possible keys
    let metricsText = finalReport['상담 성과 지표'] || 
                      finalReport['대화 효율성'] || 
                      finalReport['상담 분석'];
    
    // Default metrics based on conversation data
    const metrics = [
        { name: '응답 시간', score: 75 },
        { name: '정보 제공', score: 80 },
        { name: '고객 만족도', score: 65 },
        { name: '문제 해결', score: 70 }
    ];
    
    // If we have conversation turns, calculate some metrics
    if (conversation.turns) {
        // Calculate satisfaction based on the final satisfaction estimate
        if (finalReport['사용자 만족도 추정']) {
            let satisfactionText = finalReport['사용자 만족도 추정'];
            let satisfactionScore = 50; // default
            
            if (satisfactionText.includes('높') || satisfactionText.includes('만족')) {
                satisfactionScore = 85;
            } else if (satisfactionText.includes('중간') || satisfactionText.includes('보통')) {
                satisfactionScore = 65;
            } else if (satisfactionText.includes('낮') || satisfactionText.includes('불만족')) {
                satisfactionScore = 35;
            }
            
            // Update customer satisfaction score
            metrics.find(m => m.name === '고객 만족도').score = satisfactionScore;
        }
        
        // Update problem solving score based on success
        metrics.find(m => m.name === '문제 해결').score = conversation.success ? 90 : 40;
    }
    
    return metrics;
}

// Render product fit chart
function renderProductFitChart(productFitData) {
    if (!productFitData) return;
    
    const ctx = document.getElementById('product-fit-chart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: productFitData.map(item => item.name),
            datasets: [{
                label: '상품 적합도 점수',
                data: productFitData.map(item => item.score),
                backgroundColor: ['#28a745', '#4a6bff', '#ffc107'],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                title: {
                    display: true,
                    text: '상품 적합도 분석'
                },
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });
}

// Render consultation metrics chart
function renderConsultationMetricsChart(metricsData) {
    if (!metricsData) return;
    
    const ctx = document.getElementById('consultation-metrics-chart').getContext('2d');
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: metricsData.map(item => item.name),
            datasets: [{
                label: '상담 효율성 지표',
                data: metricsData.map(item => item.score),
                backgroundColor: 'rgba(74, 107, 255, 0.2)',
                borderColor: '#4a6bff',
                borderWidth: 2,
                pointBackgroundColor: '#4a6bff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    min: 0,
                    max: 100,
                    ticks: {
                        display: false
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: '상담 성과 분석'
                }
            }
        }
    });
}

// Function to download report as PDF (stub for now)
function downloadReportPDF(conversationId) {
    alert('PDF 다운로드 기능은 개발 중입니다.');
}

// Generate HTML report
function generateReportHTML(conversationId) {
    if (!simulationResults || !simulationResults.conversations) {
        alert('시뮬레이션 결과가 없습니다.');
        return;
    }
    
    const conversation = simulationResults.conversations.find(conv => conv.id === conversationId) || 
                         simulationResults.conversations[conversationId];
    
    if (!conversation) {
        alert('선택된 대화를 찾을 수 없습니다.');
        return;
    }
                         
    // Call the backend to generate HTML report
    fetch('/generate-report', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(conversation)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.blob();
    })
    .then(blob => {
        // Create a download link for the HTML file
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `insurance_report_${conversation.user_info.user.name}.html`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
    })
    .catch(error => {
        console.error('Error generating HTML report:', error);
        alert('HTML 보고서 생성에 실패했습니다.');
    });
}

// Helper function to format timestamp
function formatTimestamp(timestamp) {
    // Format: "YYYYMMdd_HHmmss" to "YYYY-MM-DD HH:mm"
    const year = timestamp.substring(0, 4);
    const month = timestamp.substring(4, 6);
    const day = timestamp.substring(6, 8);
    const hour = timestamp.substring(9, 11);
    const minute = timestamp.substring(11, 13);
    
    return `${year}-${month}-${day} ${hour}:${minute}`;
} 