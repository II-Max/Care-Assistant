const fs = require('fs');

const indexHtml = fs.readFileSync('frontend/index.html', 'utf8');

// Extract style
const styleMatch = indexHtml.match(/<style>([\s\S]*?)<\/style>/);
const styles = styleMatch ? styleMatch[1] : '';

// Extract header
const headerMatch = indexHtml.match(/<header class="header"[^>]*>([\s\S]*?)<\/header>/);
const header = headerMatch ? `<header class="header" id="header">\n${headerMatch[1]}\n  </header>` : '';

// Update active class in header
let modifiedHeader = header.replace(/class="active"/g, '');
modifiedHeader = modifiedHeader.replace(/<a href="ai-chat\.html">Chat AI<\/a>/g, '<a href="ai-chat.html" class="active">💬 CHAT AI</a>');

// Extract footer
const footerMatch = indexHtml.match(/<footer class="footer">([\s\S]*?)<\/footer>/);
const footer = footerMatch ? `<footer class="footer">\n${footerMatch[1]}\n    </footer>` : '';

const newAiChat = `<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Trợ lý AI Chăm sóc Khách hàng &mdash; Bệnh viện Tim Hà Nội</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;900&family=Roboto+Condensed:wght@400;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="css/hospital-design.css">
  <style>
${styles}
    /* AI Chat specific styles */
    body { background: var(--site-bg); }
    .hero-section {
      background: #fff;
      padding: 60px 20px;
      margin-bottom: 30px;
      border-bottom: 1px solid var(--site-border);
    }
    .hero-container {
      max-width: 1100px;
      margin: 0 auto;
      display: flex;
      align-items: center;
      gap: 40px;
    }
    .hero-content { flex: 1; }
    .hero-title {
      font-family: 'Roboto Condensed', sans-serif;
      font-size: 2.5rem;
      color: var(--site-blue);
      margin-bottom: 20px;
    }
    .hero-desc {
      font-size: 1.1rem;
      color: var(--site-muted);
      line-height: 1.6;
      margin-bottom: 20px;
    }
    .hero-features {
      list-style: none;
      padding: 0;
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 10px;
    }
    .hero-features li {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 500;
      color: var(--site-text);
    }
    .hero-features li::before {
      content: '✓';
      color: var(--site-cyan);
      font-weight: bold;
    }
    .hero-illustration {
      flex: 1;
      display: flex;
      justify-content: center;
    }
    .hero-illustration svg {
      max-width: 100%;
      height: auto;
      border-radius: 20px;
      box-shadow: var(--site-shadow-lg);
    }
    .ai-chat-wrapper {
      max-width: 1100px;
      margin: 0 auto 60px;
      padding: 0 20px;
    }
    .quick-actions-row {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-bottom: 24px;
    }
    .qa-card {
      background: #fff;
      border: 1px solid var(--site-border);
      border-radius: 12px;
      padding: 12px 18px;
      display: flex;
      align-items: center;
      gap: 10px;
      cursor: pointer;
      font-weight: 600;
      color: var(--site-blue);
      box-shadow: var(--site-shadow);
      transition: all 0.2s;
    }
    .qa-card:hover {
      transform: translateY(-2px);
      box-shadow: var(--site-shadow-lg);
      border-color: var(--site-blue);
    }
    
    .chat-container-card {
      background: #fff;
      border-radius: 20px;
      box-shadow: var(--site-shadow-lg);
      border: 1px solid var(--site-border);
      overflow: hidden;
      display: flex;
      flex-direction: column;
      height: 700px;
      max-height: 80vh;
    }
    
    /* Reuse aichat-page.js classes */
    .aichat-msgs-wrap {
      flex: 1;
      overflow-y: auto;
      padding: 30px;
      scroll-behavior: smooth;
    }
    .aichat-msgs-inner {
      display: flex;
      flex-direction: column;
      gap: 24px;
    }
    
    .chat-welcome {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      text-align: center;
      height: 100%;
      padding: 40px;
    }
    .chat-welcome .w-av {
      width: 90px;
      height: 90px;
      border-radius: 50%;
      background: linear-gradient(135deg, var(--site-blue), var(--site-cyan));
      color: #fff;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 2.5rem;
      margin-bottom: 24px;
      box-shadow: 0 10px 24px rgba(0, 92, 169, 0.2);
    }
    .chat-welcome h2 {
      font-family: 'Roboto Condensed', sans-serif;
      font-size: 1.8rem;
      color: var(--site-blue-dark);
      margin-bottom: 12px;
    }
    .chat-welcome p {
      color: var(--site-muted);
      max-width: 500px;
      margin-bottom: 30px;
      line-height: 1.6;
    }
    .welcome-stats {
      display: flex;
      gap: 15px;
      flex-wrap: wrap;
      justify-content: center;
    }
    .stat-badge {
      background: var(--site-bg);
      padding: 6px 14px;
      border-radius: 20px;
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--site-blue);
      border: 1px solid var(--site-border);
    }
    
    .suggested-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 12px;
      width: 100%;
      max-width: 600px;
      margin-top: 30px;
    }
    .sugg-chip {
      background: #fff;
      border: 1px solid var(--site-border);
      border-radius: 12px;
      padding: 14px;
      display: flex;
      align-items: center;
      gap: 12px;
      cursor: pointer;
      text-align: left;
      transition: all 0.2s;
    }
    .sugg-chip:hover {
      border-color: var(--site-blue);
      box-shadow: var(--site-shadow);
      background: #f8fbfe;
    }
    .sugg-icon {
      font-size: 1.2rem;
    }
    .sugg-text {
      font-weight: 600;
      font-size: 0.9rem;
      color: var(--site-text);
    }
    
    .msg-row {
      display: flex;
      gap: 16px;
      animation: fadeIn 0.3s ease;
    }
    .msg-row.user {
      flex-direction: row-reverse;
    }
    .msg-av {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      box-shadow: 0 4px 10px rgba(0,0,0,0.08);
    }
    .msg-av.bot {
      background: linear-gradient(135deg, var(--site-blue), var(--site-cyan));
      color: #fff;
      font-size: 1.2rem;
    }
    .msg-av.user {
      background: linear-gradient(135deg, #3b4f66, #55687f);
      color: #fff;
      font-size: 1.2rem;
    }
    .msg-content {
      max-width: 75%;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .msg-name {
      font-size: 0.8rem;
      font-weight: 600;
      color: var(--site-muted);
    }
    .msg-row.user .msg-name {
      text-align: right;
    }
    .msg-bubble {
      padding: 16px 20px;
      border-radius: 18px;
      font-size: 1rem;
      line-height: 1.6;
    }
    .msg-row.bot .msg-bubble {
      background: #fff;
      border: 1px solid var(--site-border);
      border-top-left-radius: 4px;
      color: var(--site-text);
      box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .msg-row.user .msg-bubble {
      background: linear-gradient(135deg, var(--site-blue), #0071cc);
      color: #fff;
      border-top-right-radius: 4px;
      box-shadow: 0 4px 15px rgba(0, 92, 169, 0.2);
    }
    .msg-bubble p { margin-bottom: 10px; }
    .msg-bubble p:last-child { margin-bottom: 0; }
    .msg-bubble ul { margin-left: 20px; margin-bottom: 10px; }
    .msg-bubble a { color: var(--site-blue); text-decoration: underline; }
    .msg-row.user .msg-bubble a { color: rgba(255,255,255,.9); }
    .msg-bubble.emergency { background: #fde6e8 !important; border: 1.5px solid #df2027 !important; color: #8b0000 !important; }
    .msg-bubble.warning { background: #fffbe6; border: 1px solid #f0cc50; color: #6b4c00; }
    
    .typing-row { display: flex; gap: 16px; }
    .typing-dots {
      padding: 16px 20px;
      background: #fff;
      border: 1px solid var(--site-border);
      border-radius: 18px;
      border-top-left-radius: 4px;
      display: flex;
      gap: 6px;
      align-items: center;
      height: fit-content;
    }
    .td { width: 8px; height: 8px; border-radius: 50%; background: var(--site-muted); animation: bounce 1.4s infinite ease-in-out both; }
    .td:nth-child(1) { animation-delay: -0.32s; }
    .td:nth-child(2) { animation-delay: -0.16s; }
    @keyframes bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); background: var(--site-blue); } }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    
    .aqr {
      padding: 0 30px 15px;
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }
    .aqr.hidden { display: none !important; }
    .aqr-btn {
      padding: 8px 16px;
      border: 1px solid var(--site-cyan);
      background: #fff;
      color: var(--site-blue);
      border-radius: 20px;
      font-weight: 600;
      font-size: 0.9rem;
      cursor: pointer;
      transition: all 0.2s;
    }
    .aqr-btn:hover {
      background: var(--site-cyan);
      color: #fff;
    }
    
    .chat-input-area {
      padding: 20px 30px;
      background: #fff;
      border-top: 1px solid var(--site-border);
    }
    .ac-input-wrap {
      display: flex;
      align-items: flex-end;
      gap: 12px;
      background: var(--site-bg);
      border: 1px solid var(--site-border);
      border-radius: 24px;
      padding: 10px 12px 10px 24px;
      transition: all 0.2s;
    }
    .ac-input-wrap:focus-within {
      border-color: var(--site-blue);
      background: #fff;
      box-shadow: 0 4px 20px rgba(0, 92, 169, 0.1);
    }
    #aichat-input {
      flex: 1;
      border: none;
      background: transparent;
      outline: none;
      font-size: 1rem;
      font-family: inherit;
      color: var(--site-text);
      resize: none;
      padding: 8px 0;
      max-height: 120px;
    }
    .aichat-send {
      width: 44px;
      height: 44px;
      border-radius: 50%;
      background: var(--site-blue);
      color: #fff;
      border: none;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.2s;
      flex-shrink: 0;
    }
    .aichat-send:hover:not(:disabled) {
      transform: scale(1.05);
      background: var(--site-blue-dark);
    }
    .aichat-send:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
    
    .ac-disc {
      text-align: center;
      font-size: 0.8rem;
      color: var(--site-muted);
      padding: 10px 30px 20px;
      background: #fff;
    }
    .ac-disc a { color: var(--site-blue); font-weight: 600; }

    @media (max-width: 900px) {
      .hero-container { flex-direction: column; text-align: center; }
      .hero-features { justify-content: center; margin: 0 auto; display: inline-grid; text-align: left; }
      .hero-illustration svg { max-width: 250px; }
      .chat-container-card { height: 600px; }
    }
    
    @media (max-width: 600px) {
      .aichat-msgs-wrap, .chat-welcome, .chat-input-area, .aqr { padding-left: 15px; padding-right: 15px; }
      .msg-bubble { padding: 12px 16px; }
      .ac-input-wrap { padding-left: 16px; }
      .hero-title { font-size: 2rem; }
      .qa-card { width: 100%; justify-content: center; }
    }
  </style>
</head>
<body class="homepage-rebuild ai-chat-page chat-full">

${modifiedHeader}

  <main id="main-content">
    <section class="hero-section">
      <div class="hero-container">
        <div class="hero-content">
          <h1 class="hero-title">🤖 Trợ lý AI Chăm sóc Khách hàng</h1>
          <p class="hero-desc">Hệ thống Trợ lý Trí tuệ Nhân tạo của Bệnh viện Tim Hà Nội sẵn sàng hỗ trợ bạn mọi lúc, mọi nơi. Giải đáp nhanh chóng các thắc mắc về quy trình khám chữa bệnh.</p>
          <ul class="hero-features">
            <li>Đặt lịch khám</li>
            <li>Tra cứu bác sĩ</li>
            <li>Giá dịch vụ</li>
            <li>Bảo hiểm y tế (BHYT)</li>
            <li>Hướng dẫn khám</li>
            <li>Thông tin cấp cứu</li>
          </ul>
        </div>
        <div class="hero-illustration">
          <svg width="320" height="240" viewBox="0 0 320 240" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="320" height="240" rx="20" fill="url(#paint0_linear)"/>
            <circle cx="160" cy="100" r="50" fill="white" fill-opacity="0.2"/>
            <circle cx="160" cy="100" r="35" fill="white"/>
            <path d="M150 95H170M150 105H160" stroke="#005CA9" stroke-width="4" stroke-linecap="round"/>
            <rect x="60" y="180" width="200" height="20" rx="10" fill="white" fill-opacity="0.8"/>
            <rect x="80" y="210" width="160" height="20" rx="10" fill="white" fill-opacity="0.5"/>
            <defs>
              <linearGradient id="paint0_linear" x1="0" y1="0" x2="320" y2="240" gradientUnits="userSpaceOnUse">
                <stop stop-color="#2CB7E8"/>
                <stop offset="1" stop-color="#005CA9"/>
              </linearGradient>
            </defs>
          </svg>
        </div>
      </div>
    </section>

    <div class="ai-chat-wrapper">
      <div class="quick-actions-row">
        <button class="qa-card sb-btn" data-quick="Tôi muốn đặt lịch khám bệnh, cần làm gì?">
          <span>📅</span> Đặt lịch khám
        </button>
        <button class="qa-card sb-btn" data-quick="Bệnh viện có những bác sĩ chuyên khoa nào?">
          <span>👨‍⚕️</span> Tra cứu bác sĩ
        </button>
        <button class="qa-card sb-btn" data-quick="Chi phí khám bệnh tại bệnh viện là bao nhiêu?">
          <span>💰</span> Giá dịch vụ
        </button>
        <button class="qa-card sb-btn" data-quick="Bảo hiểm y tế chi trả những dịch vụ nào?">
          <span>🩺</span> BHYT
        </button>
        <button class="qa-card sb-btn" data-quick="Thủ tục cấp cứu và cách tiếp nhận bệnh nhân khẩn cấp?">
          <span>🚑</span> Cấp cứu
        </button>
        <button class="qa-card sb-btn" data-quick="Hotline hỗ trợ khách hàng là số nào?">
          <span>📞</span> Hotline
        </button>
      </div>

      <div class="chat-container-card">
        
        <div class="chat-welcome" id="chat-welcome">
          <div class="w-av">🤖</div>
          <h2>Xin chào! Tôi có thể giúp gì cho bạn?</h2>
          <p>Trợ lý AI Chăm sóc Khách hàng của Bệnh viện Tim Hà Nội.</p>
          <div class="welcome-stats">
            <span class="stat-badge">✓ 24/7 Support</span>
            <span class="stat-badge">✓ AI Powered</span>
            <span class="stat-badge">✓ RAG Knowledge Base</span>
            <span class="stat-badge">✓ Bệnh viện Tim Hà Nội</span>
          </div>
          <div class="suggested-grid" id="suggested-grid"></div>
        </div>

        <div class="aichat-msgs-wrap" id="aichat-msgs-wrap" style="display:none">
          <div class="aichat-msgs-inner" id="aichat-messages"></div>
        </div>

        <div class="aqr hidden" id="aichat-quick-replies"></div>

        <div class="chat-input-area">
          <div class="ac-input-wrap">
            <textarea
              id="aichat-input"
              rows="1"
              placeholder="Nhập câu hỏi của bạn... (Enter để gửi)"
              maxlength="2000"
              autocomplete="off"
            ></textarea>
            <button class="aichat-send" id="aichat-send" aria-label="Gửi tin nhắn">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
              </svg>
            </button>
          </div>
        </div>
        
        <div class="ac-disc">
          ⚕️ Thông tin do AI cung cấp chỉ mang tính tham khảo. Không thay thế tư vấn y tế chuyên môn.
          Khẩn cấp: gọi <strong>115</strong> hoặc hotline <a href="tel:19001082">19001082</a>.
        </div>

      </div>
    </div>
  </main>

${footer}

  <script src="js/app.js"></script>
  <script src="js/aichat-page.js"></script>
</body>
</html>`;

fs.writeFileSync('frontend/ai-chat.html', newAiChat);
console.log('Successfully rewrote ai-chat.html');
