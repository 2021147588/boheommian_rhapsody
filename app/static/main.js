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
    console.log('Received data:', data);
    
    // Store results globally
    simulationResults = data.data;
    console.log('Stored simulation results:', simulationResults);
    
    // Update summary
    document.getElementById('result-total').textContent = data.data.summary.total_samples;
    document.getElementById('result-success').textContent = data.data.summary.success_count;
    document.getElementById('result-rate').textContent = `${data.data.summary.success_rate.toFixed(1)}%`;
    
    // Update dashboard metrics
    document.getElementById('total-customers').textContent = data.data.summary.total_samples;
    document.getElementById('success-count').textContent = data.data.summary.success_count;
    document.getElementById('success-rate').textContent = `${data.data.summary.success_rate.toFixed(1)}%`;
    document.getElementById('last-run').textContent = data.data.summary.timestamp;
    
    // Update charts
    updateChartsWithData(data.data);
    
    // Update recent simulations table
    updateSimulationsTable(data.data);
    
    // Update customer dropdown
    updateCustomerDropdown(data.data);
    
    // Prepare detail modal content
    prepareDetailModalContent(data.data);
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
        option.textContent = `${conv.user_info.name || `고객 ${index + 1}`} (${conv.success ? '성공' : '실패'})`;
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
    
    conversation.turns.forEach(turn => {
        // Add agent message
        if (turn.agent_response) {
            const agentMessage = document.createElement('div');
            agentMessage.className = 'message agent';
            
            const sender = document.createElement('div');
            sender.className = 'sender';
            sender.textContent = `${turn.current_agent} 에이전트`;
            
            const content = document.createElement('div');
            content.className = 'content';
            content.textContent = turn.agent_response;
            
            agentMessage.appendChild(sender);
            agentMessage.appendChild(content);
            chatMessages.appendChild(agentMessage);
        }
        
        // Add user message
        if (turn.user_reply) {
            const userMessage = document.createElement('div');
            userMessage.className = 'message user';
            
            const sender = document.createElement('div');
            sender.className = 'sender';
            sender.textContent = '고객';
            
            const content = document.createElement('div');
            content.className = 'content';
            content.textContent = turn.user_reply;
            
            userMessage.appendChild(sender);
            userMessage.appendChild(content);
            chatMessages.appendChild(userMessage);
        }
    });
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
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