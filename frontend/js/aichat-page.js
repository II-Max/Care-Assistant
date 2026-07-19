(function () {
  'use strict';

  var SUGGESTIONS = [
    { icon: "📅", text: "Đặt lịch khám",      query: "Tôi muốn đặt lịch khám bệnh, cần làm gì?" },
    { icon: "👨‍⚕️", text: "Tra cứu bác sĩ", query: "Bệnh viện có những bác sĩ chuyên khoa nào?" },
    { icon: "💰", text: "Giá dịch vụ",         query: "Chi phí khám bệnh tại bệnh viện là bao nhiêu?" },
    { icon: "🪪", text: "Bảo hiểm y tế",       query: "Bảo hiểm y tế chi trả những dịch vụ nào?" },
    { icon: "📋", text: "Quy trình khám",       query: "Quy trình khám bệnh tại Bệnh viện Tim Hà Nội như thế nào?" },
    { icon: "🏨", text: "Hướng dẫn nhập viện", query: "Cần chuẩn bị gì khi nhập viện điều trị?" },
    { icon: "🕐", text: "Giờ làm việc",         query: "Giờ làm việc và lịch khám của bệnh viện?" },
    { icon: "🚑", text: "Cấp cứu",              query: "Thủ tục cấp cứu và cách tiếp nhận bệnh nhân khẩn cấp?" },
  ];

  var QUICK_REPLIES = [
    "Đặt lịch khám","Tra cứu bác sĩ","Giá dịch vụ","Bảo hiểm y tế",
    "Quy trình khám","Hướng dẫn nhập viện","Giờ làm việc","Cấp cứu"
  ];

  var API = "http://localhost:8001/api/ai/chat";
  var loading=false,convId=null,started=false;
  var elW=document.getElementById("chat-welcome");
  var elG=document.getElementById("suggested-grid");
  var elWrap=document.getElementById("aichat-msgs-wrap");
  var elM=document.getElementById("aichat-messages");
  var elQR=document.getElementById("aichat-quick-replies");
  var elI=document.getElementById("aichat-input");
  var elS=document.getElementById("aichat-send");

  function init(){buildGrid();bindAll();}

  function buildGrid(){
    if(!elG)return;
    SUGGESTIONS.forEach(function(s){
      var b=document.createElement("button");
      b.className="sugg-chip";
      b.setAttribute("aria-label",s.text);
      b.innerHTML="<span class=\"sugg-icon\">"+s.icon+"</span><span class=\"sugg-text\">"+esc(s.text)+"</span>";
      b.onclick=function(){go();sendMsg(s.query);};
      elG.appendChild(b);
    });
  }

  function buildQR(){
    if(!elQR)return;
    elQR.innerHTML="";
    QUICK_REPLIES.forEach(function(t){
      var b=document.createElement("button");
      b.className="aqr-btn";
      b.textContent=t;
      b.onclick=function(){hideQR();sendMsg(t);};
      elQR.appendChild(b);
    });
  }

  function bindAll(){
    if(elS)elS.onclick=function(){var m=elI&&elI.value.trim();if(m){go();sendMsg(m);}};
    if(elI){
      elI.onkeydown=function(e){if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();var m=elI.value.trim();if(m){go();sendMsg(m);}}};
      elI.oninput=resize;
    }
    document.querySelectorAll(".sb-btn[data-quick]").forEach(function(b){
      b.onclick=function(){var q=b.getAttribute("data-quick");if(q){go();sendMsg(q);}};
    });
  }

  function resize(){if(!elI)return;elI.style.height="auto";elI.style.height=Math.min(elI.scrollHeight,160)+"px";}

  function go(){
    if(started)return;started=true;
    if(elW)elW.style.display="none";
    if(elWrap)elWrap.style.cssText="display:flex;flex:1;flex-direction:column;overflow-y:auto;padding:20px 0;scroll-behavior:smooth;";
    addBot(wMsg());
  }

  function wMsg(){
    return "Xin chào! 👋 Tôi là **Trợ lý AI** của **Bệnh viện Tim Hà Nội**.\n\nTôi hỗ trợ về:\n• 📅 Đặt lịch khám\n• 👨\u200d⚕\ufe0f Tra cứu bác sĩ\n• 💰 Giá dịch vụ\n• 🪪 Bảo hiểm y tế\n• 📋 Quy trình khám\n• 🏨 Hướng dẫn nhập viện\n• 🕐 Giờ làm việc\n• 🚑 Cấp cứu\n\nHãy đặt câu hỏi!\n\n*Gọi **19001082** để hỗ trợ trực tiếp.*";
  }

  async function sendMsg(text){
    if(loading||!text)return;
    if(elI){elI.value="";resize();}
    hideQR();addUser(text);loading=true;setSend();
    var tp=addTyping();
    try{
      var r=await fetch(API,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:text,conversation_id:convId})});
      rmEl(tp);
      if(!r.ok)throw new Error("HTTP "+r.status);
      var d=await r.json();
      if(d.conversation_id)convId=d.conversation_id;
      addBot(d.reply,d.is_emergency,d.sources,d.handoff_required,d.risk_level);
    }catch(e){
      rmEl(tp);addBot(fallback(text));
    }finally{
      loading=false;setSend();setTimeout(showQR,700);if(elI)elI.focus();
    }
  }

  function fallback(q){
    q=q.toLowerCase();
    if(q.includes("đặt lịch")||q.includes("hẹn khám"))return "**Hướng dẫn đặt lịch khám** \n\n• **Hotline:** 19001082\n• **Trực tuyến:** [Dat lich](booking.html)\n• **Tại quầy:** 92 Trần Hưng Đạo";
    if(q.includes("bác sĩ")||q.includes("tra cứu"))return "**Tra cứu bác sĩ** \n\n• PGS.TS.BS **Nguyễn Sinh Hiền** \n• TS.BS **Vũ Quỳnh Nga** \n• TS.BS **Phạm Như Hùng**\n\nGọi **19001082**";
    if(q.includes("giá")||q.includes("chi phí"))return "**Giá dịch vụ** \n\n• Khám thông thường: 100.000–300.000 đ\n• Siêu âm tim: 150.000–400.000 đ\n\nGọi **19001082**";
    if(q.includes("bảo hiểm")||q.includes("bhyt"))return "**Bảo hiểm y tế** \n\nChi trả cho khám, điều trị, thuốc trong danh mục. Mức hưởng 70–100%.";
    if(q.includes("quy trình"))return "**Quy trình khám** \n\n1️⃣ Đăng ký  2️⃣ Khám sàng lọc  3️⃣ Chuyên khoa  4️⃣ Xét nghiệm  5️⃣ Kết quả  6️⃣ Thanh toán";
    if(q.includes("nhập viện"))return "**Hướng dẫn nhập viện** \n\nChẩn bị: CMND, thẻ BHYT, giấy chuyển viện, hồ sơ cũ, quần áo cá nhân.";
    if(q.includes("giờ")||q.includes("lịch làm"))return "**Giờ làm việc** \n\nThứ 2-6: 7h-17h | Thứ 7: 7h-12h\nCấp cứu 24/7 | Hotline 19001082";
    if(q.includes("cấp cứu"))return "🚨 **Cấp cứu** \n\nGọi **115** (24/7) hoặc **19001082**\nĐến Phòng Cấp cứu – 92 Trần Hưng Đạo";
    return "Cảm ơn! 📞 Gọi **19001082** (7h-17h) hoặc đặt lịch tại [booking.html](booking.html).";
  }

  function addUser(t){var r=mk("div","msg-row user");r.innerHTML="<div class=\"msg-content\"><div class=\"msg-name\">Bạn</div><div class=\"msg-bubble\">"+esc(t)+"</div></div><div class=\"msg-av user\" aria-hidden=\"true\">👤</div>";elM.appendChild(r);sb();}
  function addBot(text,isEm,sources,handoff,risk){
    isEm=isEm||false;sources=sources||[];handoff=handoff||false;risk=risk||"LOW";
    var r=mk("div","msg-row bot");
    var c="msg-bubble"; if(isEm||risk==="HIGH")c+=" emergency"; else if(handoff)c+=" warning";
    var sH="";if(sources.length>0)sH="<div class=\"msg-sources\">Ngu\u1ed3n: "+sources.map(function(s){return esc(s.title);}).join(", ")+"</div>";
    var hH=handoff&&!isEm?"<div class=\"msg-handoff\">\u26a0 AI khuy\u00ean g\u1eb7p b\u00e1c s\u0129 ho\u1eb7c g\u1ecdi 19001082.</div>":"";
    r.innerHTML="<div class=\"msg-av bot\" aria-hidden=\"true\">🫀</div><div class=\"msg-content\"><div class=\"msg-name\">Tr\u1ee3 l\u00fd AI \u2013 BV Tim H\u00e0 N\u1ed9i</div><div class=\""+c+"\">"+md(text)+hH+sH+"</div></div>";
    elM.appendChild(r);sb();
  }
  function addTyping(){var r=mk("div","typing-row");r.id="typing-row";r.innerHTML="<div class=\"msg-av bot\" aria-hidden=\"true\">🫀</div><div class=\"typing-dots\"><div class=\"td\"></div><div class=\"td\"></div><div class=\"td\"></div></div>";elM.appendChild(r);sb();return r;}
  function showQR(){buildQR();if(elQR)elQR.classList.remove("hidden");}
  function hideQR(){if(elQR)elQR.classList.add("hidden");}
  function rmEl(el){if(el&&el.parentNode)el.parentNode.removeChild(el);}
  function sb(){requestAnimationFrame(function(){if(elWrap)elWrap.scrollTop=elWrap.scrollHeight;});}
  function setSend(){if(elS)elS.disabled=loading;}
  function mk(tag,cls){var el=document.createElement(tag);el.className=cls;return el;}
  function esc(t){var d=document.createElement("div");d.textContent=t;return d.innerHTML;}
  function su(c){if(!c)return"";try{var u=new URL(c,location.origin);if(u.protocol!=="https:"||!["benhvientimhanoi.vn","www.benhvientimhanoi.vn"].includes(u.hostname))return"";return esc(u.toString());}catch(e){return"";}}
  function md(text){var h=esc(text);h=h.replace(/\*\*(.+?)\*\*/g,"<strong>$1</strong>");h=h.replace(/__(.+?)__/g,"<strong>$1</strong>");h=h.replace(/\[([^\]]+)\]\(([^)]+)\)/g,function(m,l,u){return "<a href=\""+esc(u)+"\">" +l+"</a>";});h=h.replace(/^[\u2022\-\*]\s+(.+)$/gm,"<li>$1</li>");h=h.replace(/(<li>.*<\/li>\n?)+/g,"<ul>$&</ul>");h=h.replace(/\n\n/g,"</p><p>");h=h.replace(/\n/g,"<br>");h="<p>"+h+"</p>";h=h.replace(/<p><\/p>/g,"");h=h.replace(/<p>(<ul>)/g,"$1");h=h.replace(/(<\/ul>)<\/p>/g,"$1");return h;}

  if(document.readyState==="loading"){document.addEventListener("DOMContentLoaded",init);}else{init();}
})();