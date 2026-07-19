const fs = require('fs');

try {
  const index = fs.readFileSync('frontend/index.html', 'utf8');

  // extract styles, header, footer
  const styleMatch = index.match(/<style>([\s\S]*?)<\/style>/);
  if (!styleMatch) {
      console.log('No style block found in index.html, maybe already removed?');
  } else {
      const globalStyles = styleMatch[1];
      let css = fs.readFileSync('frontend/css/hospital-design.css', 'utf8');
      if (!css.includes('.top-utility')) {
        css += '\n\n/* GLOBAL LAYOUT STYLES FROM INDEX.HTML */\n' + globalStyles;
        fs.writeFileSync('frontend/css/hospital-design.css', css);
      }

      // Remove inline <style> from index.html
      let indexContent = index.replace(/<style>[\s\S]*?<\/style>/, '');
      fs.writeFileSync('frontend/index.html', indexContent);
      console.log('Processed index.html');
  }

  // Update ai-chat.html
  let aiChat = fs.readFileSync('frontend/ai-chat.html', 'utf8');
  aiChat = aiChat.replace(/<style>([\s\S]*?)<\/style>/, (match, p1) => {
    const aiChatSpecificIdx = match.indexOf('/* AI Chat specific styles */');
    if (aiChatSpecificIdx !== -1) {
      return '<style>\n    ' + match.substring(aiChatSpecificIdx);
    }
    return match;
  });
  fs.writeFileSync('frontend/ai-chat.html', aiChat);
  console.log('Processed ai-chat.html');

  // Re-read index to get header and footer (in case we run this multiple times)
  const index2 = fs.readFileSync('frontend/index.html', 'utf8');
  const headerMatch = index2.match(/<header class="header"[^>]*>([\s\S]*?)<\/header>/);
  const globalHeader = `<header class="header" id="header">${headerMatch[1]}</header>`;
  const footerMatch = index2.match(/<footer class="footer">([\s\S]*?)<\/footer>/);
  const globalFooter = `<footer class="footer">${footerMatch[1]}</footer>`;

  // Process the other files
  const files = ['about.html', 'booking.html', 'contact.html', 'departments.html'];

  for (const file of files) {
    let content = fs.readFileSync('frontend/' + file, 'utf8');

    // Replace header
    let newHeader = globalHeader.replace(/class="active"/g, '');
    
    // Add active class back to the right link
    const hrefRegex = new RegExp(`(<a href="${file}")(>)`, 'g');
    newHeader = newHeader.replace(hrefRegex, '$1 class="active"$2');

    content = content.replace(/<header[\s\S]*?<\/header>/, newHeader);
    content = content.replace(/<footer[\s\S]*?<\/footer>/, globalFooter);

    // Add homepage-rebuild class to body
    content = content.replace(/<body([^>]*)>/, (match, p1) => {
      if (p1.includes('class="')) {
        if (!p1.includes('homepage-rebuild')) {
           return match.replace(/class="/, 'class="homepage-rebuild ');
        }
      } else {
        return `<body${p1} class="homepage-rebuild">`;
      }
      return match;
    });

    fs.writeFileSync('frontend/' + file, content);
    console.log(`Processed ${file}`);
  }

  console.log('Synchronization complete!');

} catch (err) {
  console.error('Error during synchronization:', err);
}
