const fs = require('fs');
const files = ['index.html', 'about.html', 'booking.html', 'contact.html', 'departments.html', 'knowledge.html', 'news.html', 'ai-chat.html'];

for (const file of files) {
  let content = fs.readFileSync('frontend/' + file, 'utf8');

  // We want to ensure we have:
  // <script src="js/app.js"></script>
  // <script src="js/chat.js"></script>
  // right before </body>

  let hasApp = content.includes('<script src="js/app.js"></script>');
  let hasChat = content.includes('<script src="js/chat.js"></script>');
  
  if (!hasApp || !hasChat) {
    content = content.replace(/<\/body>/i, (match) => {
      let scripts = '';
      if (!hasApp) scripts += '<script src="js/app.js"></script>\n  ';
      if (!hasChat) scripts += '<script src="js/chat.js"></script>\n  ';
      return scripts + match;
    });
    fs.writeFileSync('frontend/' + file, content);
    console.log(`Added missing scripts to ${file}`);
  }
}
