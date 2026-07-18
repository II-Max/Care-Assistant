/**
 * 🏥 Chat Widget — Bệnh viện Tim Hà Nội
 * 
 * Xử lý:
 * - Floating chat widget (open/close)
 * - Gửi/nhận tin nhắn qua AI API
 * - Emergency alert rendering
 * - Quick reply suggestions
 * - Typing indicator
 * - Simple markdown rendering
 * - Session-based conversation history
 */

(function () {
  'use strict';

  // ========================
  // Configuration
  // ========================
  const CONFIG = {
    // Đã trỏ cố định về backend Localhost để khi deploy Firebase vẫn gọi được AI nội bộ
    apiUrl: 'http://localhost:8001',
    chatEndpoint: '/api/ai/chat',
    maxMessageLength: 2000,
    quickReplies: [
      'Đặt lịch khám như thế nào?',
      'Giờ làm việc của bệnh viện?',
      'Bảo hiểm y tế chi trả những gì?',
      'Các dịch vụ khám tim mạch?',
      'Địa chỉ bệnh viện?',
    ],
    welcomeMessage: `Xin chào! 👋 Tôi là Trợ lý AI của **Bệnh viện Tim Hà Nội**.

Tôi có thể giúp bạn với:
• 📅 Hướng dẫn đặt lịch khám
• 🏥 Thông tin dịch vụ & chuyên khoa
• 💳 Bảo hiểm y tế (BHYT)
• 📍 Địa chỉ & liên hệ
• ❓ Các thắc mắc khác

Hãy đặt câu hỏi hoặc chọn một gợi ý bên dưới!

📋 *Lưu ý: Tôi chỉ cung cấp thông tin tham khảo, không thay thế tư vấn y tế chuyên môn.*`
  };

  // ========================
  // State
  // ========================
  let isOpen = false;
  let isLoading = false;
  let conversationId = null;

  // ========================
  // DOM Elements
  // ========================
  let chatTrigger, chatPanel, chatMessages, chatInput, chatSend, quickRepliesContainer;

  // ========================
  // Initialization
  // ========================
  function init() {
    // Nếu đang ở trang ai-chat.html (full page), không tạo widget
    if (document.querySelector('.chat-full')) {
      initFullPageChat();
      return;
    }

    injectChatWidget();
    bindEvents();
  }

  function injectChatWidget() {
    // Chat Trigger Button
    chatTrigger = document.createElement('button');
    chatTrigger.className = 'chat-widget-trigger';
    chatTrigger.id = 'chat-trigger';
    chatTrigger.innerHTML = '💬';
    chatTrigger.setAttribute('aria-label', 'Mở chat AI');

    // Chat Panel
    chatPanel = document.createElement('div');
    chatPanel.className = 'chat-panel';
    chatPanel.id = 'chat-panel';
    chatPanel.innerHTML = `
      <div class="chat-header">
        <div class="chat-header-avatar">🏥</div>
        <div class="chat-header-info">
          <h4>Trợ lý AI</h4>
          <p>Bệnh viện Tim Hà Nội</p>
        </div>
        <button class="chat-close" id="chat-close" aria-label="Đóng chat">✕</button>
      </div>
      <div class="chat-disclaimer">
        ⚕️ Thông tin chỉ mang tính tham khảo. Không thay thế tư vấn y tế.
      </div>
      <div class="chat-messages" id="chat-messages"></div>
      <div class="quick-replies" id="quick-replies"></div>
      <div class="chat-input-area">
        <input type="text" class="chat-input" id="chat-input" 
               placeholder="Nhập câu hỏi của bạn..." 
               maxlength="${CONFIG.maxMessageLength}"
               autocomplete="off">
        <button class="chat-send" id="chat-send" aria-label="Gửi">➤</button>
      </div>
    `;

    document.body.appendChild(chatTrigger);
    document.body.appendChild(chatPanel);

    // Get references
    chatMessages = document.getElementById('chat-messages');
    chatInput = document.getElementById('chat-input');
    chatSend = document.getElementById('chat-send');
    quickRepliesContainer = document.getElementById('quick-replies');
  }

  function initFullPageChat() {
    chatMessages = document.getElementById('chat-messages');
    chatInput = document.getElementById('chat-input');
    chatSend = document.getElementById('chat-send');
    quickRepliesContainer = document.getElementById('quick-replies');

    if (!chatMessages || !chatInput) return;

    bindChatEvents();
    addBotMessage(CONFIG.welcomeMessage);
    renderQuickReplies();
    chatInput.focus();
  }

  // ========================
  // Event Binding
  // ========================
  function bindEvents() {
    // Toggle chat panel
    chatTrigger.addEventListener('click', toggleChat);
    document.getElementById('chat-close').addEventListener('click', toggleChat);

    bindChatEvents();
  }

  function bindChatEvents() {
    // Send message
    if (chatSend) {
      chatSend.addEventListener('click', sendMessage);
    }

    if (chatInput) {
      chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          sendMessage();
        }
      });
    }
  }

  // ========================
  // Toggle Chat
  // ========================
  function toggleChat() {
    isOpen = !isOpen;

    if (chatPanel) chatPanel.classList.toggle('open', isOpen);
    if (chatTrigger) {
      chatTrigger.classList.toggle('active', isOpen);
      chatTrigger.innerHTML = isOpen ? '✕' : '💬';
    }

    if (isOpen && chatMessages && chatMessages.children.length === 0) {
      addBotMessage(CONFIG.welcomeMessage);
      renderQuickReplies();
    }

    if (isOpen && chatInput) {
      setTimeout(() => chatInput.focus(), 300);
    }
  }

  // ========================
  // Send Message
  // ========================
  async function sendMessage() {
    if (isLoading) return;

    const message = chatInput.value.trim();
    if (!message) return;

    // Add user message
    addUserMessage(message);
    chatInput.value = '';
    hideQuickReplies();

    // Show typing indicator
    isLoading = true;
    updateSendButton();
    const typingEl = showTypingIndicator();

    try {
      const response = await fetch(`${CONFIG.apiUrl}${CONFIG.chatEndpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: message,
          conversation_id: conversationId
        })
      });

      removeTypingIndicator(typingEl);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();

      // Render bot response
      addBotMessage(data.reply, data.is_emergency, data.sources, data.handoff_required, data.risk_level);

      // Show quick replies again sau khi trả lời
      setTimeout(() => renderQuickReplies(), 500);

    } catch (error) {
      removeTypingIndicator(typingEl);
      console.error('Chat error:', error);
      addBotMessage(
        'Xin lỗi, hiện tại hệ thống đang gặp sự cố. Vui lòng thử lại sau hoặc gọi **Hotline: 19001082** để được hỗ trợ.',
        false
      );
    } finally {
      isLoading = false;
      updateSendButton();
    }
  }

  // ========================
  // Message Rendering
  // ========================
  function addUserMessage(text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'chat-message user';
    msgDiv.innerHTML = `
      <div class="chat-message-avatar">👤</div>
      <div class="chat-bubble">${escapeHtml(text)}</div>
    `;
    chatMessages.appendChild(msgDiv);
    scrollToBottom();
  }

  function addBotMessage(text, isEmergency = false, sources = [], handoffRequired = false, riskLevel = "LOW") {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'chat-message bot';

    let bubbleClass = 'chat-bubble';
    if (isEmergency || riskLevel === 'HIGH') {
        bubbleClass += ' emergency';
    } else if (handoffRequired) {
        bubbleClass += ' warning';
    }

    const htmlContent = renderMarkdown(text);

    let sourcesHtml = '';
    if (sources && sources.length > 0) {
      sourcesHtml = '<div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #eee; font-size: 11px; color: #888;">';
      sourcesHtml += '📎 Nguồn: ';
      sourcesHtml += sources.map(s => {
        const safeUrl = safeOfficialUrl(s.url);
        return safeUrl
          ? `<a href="${safeUrl}" target="_blank" rel="noopener noreferrer">${escapeHtml(s.title)}</a>`
          : escapeHtml(s.title);
      }).join(', ');
      sourcesHtml += '</div>';
    }

    let handoffHtml = '';
    if (handoffRequired && !isEmergency) {
        handoffHtml = `
            <div style="margin-top: 10px; padding: 8px; background: #fff3cd; color: #856404; border-radius: 4px; font-size: 13px; font-weight: 500;">
                ⚠️ AI khuyên bạn nên gặp trực tiếp bác sĩ hoặc gọi Tổng đài 19001082 để được tư vấn chuyên môn.
            </div>
        `;
    }

    msgDiv.innerHTML = `
      <div class="chat-message-avatar">🏥</div>
      <div class="${bubbleClass}">${htmlContent}${handoffHtml}${sourcesHtml}</div>
    `;
    chatMessages.appendChild(msgDiv);
    scrollToBottom();
  }

  // ========================
  // Quick Replies
  // ========================
  function renderQuickReplies() {
    if (!quickRepliesContainer) return;

    quickRepliesContainer.innerHTML = '';
    CONFIG.quickReplies.forEach(text => {
      const btn = document.createElement('button');
      btn.className = 'quick-reply';
      btn.textContent = text;
      btn.addEventListener('click', () => {
        chatInput.value = text;
        sendMessage();
      });
      quickRepliesContainer.appendChild(btn);
    });
    quickRepliesContainer.classList.remove('hidden');
  }

  function hideQuickReplies() {
    if (quickRepliesContainer) {
      quickRepliesContainer.classList.add('hidden');
    }
  }

  // ========================
  // Typing Indicator
  // ========================
  function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'chat-message bot';
    typingDiv.id = 'typing-indicator';
    typingDiv.innerHTML = `
      <div class="chat-message-avatar">🏥</div>
      <div class="typing-indicator">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      </div>
    `;
    chatMessages.appendChild(typingDiv);
    scrollToBottom();
    return typingDiv;
  }

  function removeTypingIndicator(el) {
    if (el && el.parentNode) {
      el.parentNode.removeChild(el);
    }
  }

  // ========================
  // Utilities
  // ========================
  function scrollToBottom() {
    if (chatMessages) {
      requestAnimationFrame(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
      });
    }
  }

  function updateSendButton() {
    if (chatSend) {
      chatSend.disabled = isLoading;
    }
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function renderMarkdown(text) {
    // Simple markdown → HTML converter
    let html = escapeHtml(text);

    // Bold **text** or __text__
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/__(.+?)__/g, '<strong>$1</strong>');

    // Italic *text* or _text_
    html = html.replace(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g, '<em>$1</em>');

    // Links [text](url)
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (match, label, url) => {
      const safeUrl = safeOfficialUrl(url);
      return safeUrl
        ? `<a href="${safeUrl}" target="_blank" rel="noopener noreferrer">${label}</a>`
        : label;
    });

    // Unordered lists (• or - or * at start of line)
    html = html.replace(/^[\•\-\*]\s+(.+)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>');

    // Line breaks
    html = html.replace(/\n\n/g, '</p><p>');
    html = html.replace(/\n/g, '<br>');
    html = `<p>${html}</p>`;

    // Clean up
    html = html.replace(/<p><\/p>/g, '');
    html = html.replace(/<p>(<ul>)/g, '$1');
    html = html.replace(/(<\/ul>)<\/p>/g, '$1');

    return html;
  }

  function safeOfficialUrl(candidate) {
    if (!candidate) return '';
    try {
      const url = new URL(candidate, window.location.origin);
      const allowedHosts = ['benhvientimhanoi.vn', 'www.benhvientimhanoi.vn'];
      if (url.protocol !== 'https:' || !allowedHosts.includes(url.hostname)) {
        return '';
      }
      return escapeHtml(url.toString());
    } catch {
      return '';
    }
  }

  // ========================
  // Auto-init
  // ========================
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Export cho full page chat
  window.ChatWidget = { init, toggleChat, sendMessage };
})();
