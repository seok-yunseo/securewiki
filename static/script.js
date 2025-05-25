const terms = {
  ZeroDay: "<h1>Zero-day</h1><p>공개되기 전부터 존재하던 보안 취약점으로, 패치가 존재하지 않아 위험합니다.</p>",
  MITM: "<h1>MITM (Man-In-The-Middle)</h1><p>공격자가 통신 중간에 개입해 데이터를 가로채거나 조작하는 공격입니다.</p>",
  RCE: "<h1>RCE (Remote Code Execution)</h1><p>원격에서 악성 코드를 실행시킬 수 있는 취약점을 의미합니다.</p>",
  WAF: "<h1>WAF (Web Application Firewall)</h1><p>웹 애플리케이션 공격을 방지하는 방화벽 기술입니다.</p>"
};

const categoryTerms = {
  XSS: "<h1>XSS</h1><p>스크립트 삽입 공격</p>",
  CSRF: "<h1>CSRF</h1><p>Cross Site Request Forgery</p>",
  SQLi: "<h1>SQL Injection</h1><p>SQL 쿼리 조작 공격</p>",
  DDoS: "<h1>DDoS</h1><p>분산 서비스 거부 공격</p>",
  PrivilegeEscalation: "<h1>Privilege Escalation</h1><p>권한 상승 공격</p>"
};

// 추천 용어가 속한 기본 카테고리
const builtIn = {
  web: ['XSS', 'CSRF', 'SQLi'],
  network: ['MITM', 'DDoS'],
  system: ['RCE', 'PrivilegeEscalation']
};

function handleKey(event) {
  if (event.key === "Enter") {
    event.preventDefault();
    searchTerm();
  }
}

function showTerm(term) {
  const html = terms[term] || categoryTerms[term] || '<p>해당 용어에 대한 설명이 없습니다.</p>';
  document.getElementById('content').innerHTML = html;
}

function showStoredTerm(term) {
  const html = `
    <h1>${term.title}</h1>
    <p><strong>카테고리:</strong> ${term.category}</p>
    <p><strong>설명:</strong> ${term.content}</p>
    <p><strong>작성자:</strong> ${term.author}</p>
    <p><strong>최근 수정자:</strong> ${term.lastEditor}</p>
    <button onclick="renderEditForm('${term.title}')">✏️ 설명 수정</button>
    <button onclick="deleteTerm('${term.title}')">🗑️ 용어 삭제</button>
    <div id="edit-area"></div>
  `;
  document.getElementById('content').innerHTML = html;
}

function renderEditForm(title) {
  const storedTerms = JSON.parse(localStorage.getItem("terms") || "[]");
  const term = storedTerms.find(t => t.title === title);
  if (!term) return;

  const html = `
    <div id="edit-form">
      <h3>📄 '${title}' 설명 수정</h3>
      <textarea id="editContent" rows="5">${term.content}</textarea>
      <input type="text" id="editorName" placeholder="수정자 이름 입력" required>
      <button onclick="submitEdit('${title}')">✅ 수정 완료</button>
    </div>
  `;
  document.getElementById("edit-area").innerHTML = html;
}

function submitEdit(title) {
  const newContent = document.getElementById("editContent").value.trim();
  const editor = document.getElementById("editorName").value.trim();

  if (!newContent || !editor) {
    alert("설명과 수정자 이름을 모두 입력하세요.");
    return;
  }

  const storedTerms = JSON.parse(localStorage.getItem("terms") || "[]");
  const term = storedTerms.find(t => t.title === title);
  if (!term) return;

  term.content = newContent;
  term.lastEditor = editor;
  localStorage.setItem("terms", JSON.stringify(storedTerms));

  showStoredTerm(term);
}

function deleteTerm(title) {
  if (!confirm(`'${title}' 용어를 정말 삭제하시겠습니까?`)) return;

  let storedTerms = JSON.parse(localStorage.getItem("terms") || "[]");
  storedTerms = storedTerms.filter(term => term.title !== title);
  localStorage.setItem("terms", JSON.stringify(storedTerms));
  alert("❌ 용어가 삭제되었습니다.");

  goHome();
  updateRecommendedTerms();
  updateCategoryMenu();
}

function filterCategory(cat) {
  const storedTerms = JSON.parse(localStorage.getItem("terms") || "[]");

  const builtinTerms = builtIn[cat] || [];
  let html = `<h1>${cat.toUpperCase()} 보안 용어</h1><ul>`;

  builtinTerms.forEach(termKey => {
    html += `<li style="cursor:pointer" onclick="showTerm('${termKey}')">${termKey}</li>`;
  });

  const userTerms = storedTerms.filter(t => t.category === cat);
  userTerms.forEach(term => {
    html += `<li style="cursor:pointer" onclick="showStoredTerm(${JSON.stringify(term).replace(/"/g, '&quot;')})">${term.title}</li>`;
  });

  html += '</ul>';
  document.getElementById('content').innerHTML = html;
}

function searchTerm() {
  const keyword = document.getElementById('searchInput').value.toLowerCase();

  const allBuiltIn = {...terms, ...categoryTerms};
  let foundKey = Object.keys(allBuiltIn).find(k => k.toLowerCase().includes(keyword));
  if (foundKey) {
    showTerm(foundKey);
    return;
  }

  const storedTerms = JSON.parse(localStorage.getItem("terms") || "[]");
  const matched = storedTerms.find(term => term.title.toLowerCase().includes(keyword));
  if (matched) {
    showStoredTerm(matched);
  }
}

function goHome() {
  document.getElementById('content').innerHTML = `
    <h1>보안 위키에 오신 것을 환영합니다</h1>
    <p>왼쪽 카테고리 또는 추천 용어를 클릭해보세요.</p>
  `;
}

function updateRecommendedTerms() {
  const termList = document.querySelectorAll("#category ul")[1];
  termList.innerHTML = '';

  const storedTerms = JSON.parse(localStorage.getItem("terms") || "[]");
  storedTerms.forEach(term => {
    const li = document.createElement("li");
    li.textContent = term.title;
    li.onclick = () => showStoredTerm(term);
    termList.appendChild(li);
  });
}

function updateCategoryMenu() {
  const storedTerms = JSON.parse(localStorage.getItem("terms") || "[]");
  const categoryList = document.querySelectorAll("#category ul")[0];
  const categorySet = new Set(["web", "network", "system"]);

  storedTerms.forEach(term => categorySet.add(term.category));

  categoryList.innerHTML = '';
  categorySet.forEach(cat => {
    const li = document.createElement("li");
    li.textContent = (cat === "기타") ? "기타" : cat.charAt(0).toUpperCase() + cat.slice(1) + " 보안";
    li.onclick = () => filterCategory(cat);
    categoryList.appendChild(li);
  });
}

window.onload = function () {
  updateRecommendedTerms();
  updateCategoryMenu();
  goHome();
};
