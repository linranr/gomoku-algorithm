// 从 localStorage 读取点击次数，如果不存在则初始化为0
let clickCount = parseInt(localStorage.getItem('clickCount')) || 0;
let forgotPasswordCount = parseInt(localStorage.getItem('forgotPasswordCount')) || 0;
let isBanned = false;
let countdownInterval = null;
let forgotPasswordCountdownInterval = null;

// 调试信息：在控制台显示当前点击次数
console.log('当前登录/注册点击次数:', clickCount);
console.log('当前忘记密码点击次数:', forgotPasswordCount);

function navigateToLogin() {
    const container = document.querySelector('.container');
    if (container) {
        container.style.opacity = '0';
        container.style.transform = 'translateY(-20px)';
        container.style.transition = 'all 0.3s ease';
    }
    
    setTimeout(() => {
        const currentPath = window.location.pathname;
        if (currentPath.includes('/author/')) {
            window.location.href = 'login.html';
        } else {
            window.location.href = 'author/login.html';
        }
    }, 300);
}

function navigateToRegister() {
    const container = document.querySelector('.container');
    if (container) {
        container.style.opacity = '0';
        container.style.transform = 'translateX(-20px)';
        container.style.transition = 'all 0.3s ease';
    }
    
    setTimeout(() => {
        const currentPath = window.location.pathname;
        if (currentPath.includes('/author/')) {
            window.location.href = 'register.html';
        } else {
            window.location.href = 'author/register.html';
        }
    }, 300);
}

function togglePasswordVisibility(inputId, button) {
    const input = document.getElementById(inputId);
    const eyeIcon = button.querySelector('.eye-icon');
    
    if (input.type === 'password') {
        input.type = 'text';
        eyeIcon.textContent = '🙈';
    } else {
        input.type = 'password';
        eyeIcon.textContent = '👁️';
    }
}

function showModal(message, onModalClose) {
    const modal = document.getElementById('modal');
    const modalMessage = document.getElementById('modal-message');
    
    if (!modal || !modalMessage) {
        console.error('弹窗元素未找到！');
        return;
    }
    
    modalMessage.textContent = message;
    modal.classList.add('show');
    
    function closeModal() {
        modal.classList.remove('show');
        modal.removeEventListener('click', closeModal);
        if (onModalClose) {
            onModalClose();
        }
    }
    
    modal.addEventListener('click', closeModal);
}

function validateLoginForm() {
    const username = document.getElementById('username');
    const password = document.getElementById('password');
    
    if (!username || !password) {
        return false;
    }
    
    if (!username.value.trim() || !password.value.trim()) {
        return false;
    }
    return true;
}

function validateRegisterForm() {
    const username = document.getElementById('reg-username');
    const password = document.getElementById('reg-password');
    const verifyCode = document.getElementById('verify-code');
    
    if (!username || !password || !verifyCode) {
        return false;
    }
    
    if (!username.value.trim() || !password.value.trim() || !verifyCode.value.trim()) {
        return false;
    }
    return true;
}

function handleLogin() {
    console.log('handleLogin 被调用，当前点击次数:', clickCount);
    
    if (isBanned) {
        console.log('用户已被禁言，无法点击');
        return;
    }
    
    if (!validateLoginForm()) {
        showModal('(｀・ω・´)\n心急吃不了热豆腐！');
        return;
    }
    
    // 增加点击次数并保存到 localStorage
    clickCount++;
    localStorage.setItem('clickCount', clickCount);
    console.log('点击次数已增加到:', clickCount);
    
    let message = '';
    
    if (clickCount === 1 || clickCount === 2) {
        message = '(´•ω•̥`)\n诶呀！人家忘记了你的密码，抱歉啦！';
    } else if (clickCount === 3) {
        message = '(；′⌒`)\n人家记不住嘛，不要为难人家啦！';
    } else if (clickCount >= 4 && clickCount <= 6) {
        const messages = [
            '(´•ω•̥`)\n诶呀！人家忘记了你的密码，抱歉啦！',
            '(；′⌒`)\n人家记不住嘛，不要为难人家啦！'
        ];
        message = messages[Math.floor(Math.random() * messages.length)];
    } else if (clickCount === 7) {
        message = '(╥﹏╥)\n嘤嘤嘤~就知道欺负人家！不理你啦！';
        showModal(message, function() {
            startBanCountdown();
        });
        return;
    } else {
        // 超过7次后重置计数
        clickCount = 1;
        localStorage.setItem('clickCount', clickCount);
        message = '(´•ω•̥`)\n诶呀！人家忘记了你的密码，抱歉啦！';
    }
    
    showModal(message, function() {
        location.reload();
    });
}

function handleRegister() {
    console.log('handleRegister 被调用，当前点击次数:', clickCount);
    
    if (isBanned) {
        console.log('用户已被禁言，无法点击');
        return;
    }
    
    if (!validateRegisterForm()) {
        showModal('(｀・ω・´)\n心急吃不了热豆腐！');
        return;
    }
    
    // 增加点击次数并保存到 localStorage
    clickCount++;
    localStorage.setItem('clickCount', clickCount);
    console.log('点击次数已增加到:', clickCount);
    
    let message = '';
    
    if (clickCount === 1 || clickCount === 2) {
        message = '(´•ω•̥`)\n诶呀！人家忘记了你的密码，抱歉啦！';
    } else if (clickCount === 3) {
        message = '(；′⌒`)\n人家记不住嘛，不要为难人家啦！';
    } else if (clickCount >= 4 && clickCount <= 6) {
        const messages = [
            '(´•ω•̥`)\n诶呀！人家忘记了你的密码，抱歉啦！',
            '(；′⌒`)\n人家记不住嘛，不要为难人家啦！'
        ];
        message = messages[Math.floor(Math.random() * messages.length)];
    } else if (clickCount === 7) {
        message = '(╥﹏╥)\n嘤嘤嘤~就知道欺负人家！不理你啦！';
        showModal(message, function() {
            startBanCountdown();
        });
        return;
    } else {
        // 超过7次后重置计数
        clickCount = 1;
        localStorage.setItem('clickCount', clickCount);
        message = '(´•ω•̥`)\n诶呀！人家忘记了你的密码，抱歉啦！';
    }
    
    showModal(message, function() {
        location.reload();
    });
}

function handleForgotPassword() {
    console.log('handleForgotPassword 被调用，当前点击次数:', forgotPasswordCount);
    
    const forgotPasswordBtn = document.querySelector('.secondary-btn:last-child');
    
    if (forgotPasswordBtn && forgotPasswordBtn.disabled) {
        console.log('忘记密码按钮已被禁用');
        return;
    }
    
    // 增加点击次数并保存到 localStorage
    forgotPasswordCount++;
    localStorage.setItem('forgotPasswordCount', forgotPasswordCount);
    console.log('忘记密码点击次数已增加到:', forgotPasswordCount);
    
    let message = '';
    
    if (forgotPasswordCount >= 1 && forgotPasswordCount <= 6) {
        const messages = [
            '(・ω・)\n密码就在你心里，再想想？',
            '(￣▽￣)\n既然忘了，那就重新注册吧！'
        ];
        message = messages[Math.floor(Math.random() * messages.length)];
    } else if (forgotPasswordCount === 7) {
        message = '(´;ω;`)\n密码已经离家出走了，找不到啦！';
        showModal(message, function() {
            startForgotPasswordCountdown();
        });
        return;
    } else {
        // 超过7次后重置计数
        forgotPasswordCount = 1;
        localStorage.setItem('forgotPasswordCount', forgotPasswordCount);
        message = '(・ω・)\n密码就在你心里，再想想？';
    }
    
    showModal(message);
}

function startBanCountdown() {
    console.log('开始禁言倒计时');
    isBanned = true;
    const banOverlay = document.getElementById('ban-overlay');
    const countdownElement = document.getElementById('countdown');
    
    if (!banOverlay || !countdownElement) {
        console.error('禁言遮罩层元素未找到');
        return;
    }
    
    let seconds = 30;
    
    banOverlay.classList.add('show');
    countdownElement.textContent = seconds;
    
    disableAllInputs();
    
    countdownInterval = setInterval(() => {
        seconds--;
        countdownElement.textContent = seconds;
        
        if (seconds <= 0) {
            clearInterval(countdownInterval);
            isBanned = false;
            banOverlay.classList.remove('show');
            enableAllInputs();
            // 重置点击次数
            clickCount = 0;
            localStorage.setItem('clickCount', 0);
            console.log('禁言结束，点击次数已重置');
        }
    }, 1000);
}

function startForgotPasswordCountdown() {
    console.log('开始忘记密码按钮禁用倒计时');
    const forgotPasswordBtn = document.querySelector('.secondary-btn:last-child');
    
    if (!forgotPasswordBtn) {
        console.error('忘记密码按钮未找到');
        return;
    }
    
    let seconds = 30;
    
    forgotPasswordBtn.disabled = true;
    const originalText = forgotPasswordBtn.textContent;
    forgotPasswordBtn.textContent = `30秒后可再次点击`;
    
    forgotPasswordCountdownInterval = setInterval(() => {
        seconds--;
        forgotPasswordBtn.textContent = `${seconds}秒后可再次点击`;
        
        if (seconds <= 0) {
            clearInterval(forgotPasswordCountdownInterval);
            forgotPasswordBtn.disabled = false;
            forgotPasswordBtn.textContent = originalText;
            // 重置点击次数
            forgotPasswordCount = 0;
            localStorage.setItem('forgotPasswordCount', 0);
            console.log('忘记密码按钮禁用结束，点击次数已重置');
        }
    }, 1000);
}

function disableAllInputs() {
    const inputs = document.querySelectorAll('input');
    const buttons = document.querySelectorAll('button');
    
    inputs.forEach(input => {
        input.disabled = true;
    });
    
    buttons.forEach(button => {
        button.disabled = true;
    });
    
    console.log('所有输入框和按钮已禁用');
}

function enableAllInputs() {
    const inputs = document.querySelectorAll('input');
    const buttons = document.querySelectorAll('button');
    
    inputs.forEach(input => {
        input.disabled = false;
    });
    
    buttons.forEach(button => {
        button.disabled = false;
    });
    
    console.log('所有输入框和按钮已启用');
}

function checkBanStatus() {
    // 检查是否处于禁言状态
    const banEndTime = localStorage.getItem('banEndTime');
    
    if (banEndTime) {
        const endTime = parseInt(banEndTime);
        const currentTime = Date.now();
        
        if (currentTime < endTime) {
            const remainingSeconds = Math.ceil((endTime - currentTime) / 1000);
            startBanCountdownWithRemaining(remainingSeconds);
        } else {
            localStorage.removeItem('banEndTime');
        }
    }
}

function startBanCountdownWithRemaining(seconds) {
    isBanned = true;
    const banOverlay = document.getElementById('ban-overlay');
    const countdownElement = document.getElementById('countdown');
    
    if (!banOverlay || !countdownElement) {
        return;
    }
    
    banOverlay.classList.add('show');
    countdownElement.textContent = seconds;
    
    disableAllInputs();
    
    countdownInterval = setInterval(() => {
        seconds--;
        countdownElement.textContent = seconds;
        
        if (seconds <= 0) {
            clearInterval(countdownInterval);
            isBanned = false;
            banOverlay.classList.remove('show');
            enableAllInputs();
            clickCount = 0;
            localStorage.setItem('clickCount', 0);
            localStorage.removeItem('banEndTime');
        }
    }, 1000);
}

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    console.log('页面加载完成，初始化...');
    
    checkBanStatus();
    
    // 为输入框添加焦点效果
    const inputs = document.querySelectorAll('.form-input');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            const hint = this.parentElement.querySelector('.input-hint');
            if (hint) {
                hint.style.color = '#667eea';
            }
        });
        
        input.addEventListener('blur', function() {
            const hint = this.parentElement.querySelector('.input-hint');
            if (hint) {
                hint.style.color = '#999';
            }
        });
    });
    
    console.log('初始化完成');
});
