// 코드 블록에 헤더 바(언어 라벨 + 복사 버튼)를 동적으로 추가한다.
// 스타일은 _mono-overrides.scss 의 .code-header / .copy-btn 에서 처리(인라인 스타일 없음).
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("div.highlighter-rouge").forEach((block) => {
    if (block.querySelector(".code-header")) return; // 중복 방지

    // language-xxx 클래스에서 언어 라벨 추출
    let lang = "CODE";
    const m = block.className.match(/language-([\w+#-]+)/);
    if (m) lang = m[1].toUpperCase();

    const header = document.createElement("div");
    header.className = "code-header";

    const label = document.createElement("span");
    label.className = "code-lang";
    label.textContent = lang;

    const button = document.createElement("button");
    button.className = "copy-btn";
    button.type = "button";
    button.textContent = "Copy";
    button.addEventListener("click", () => {
      const codeTd = block.querySelector("td.rouge-code");
      const code = codeTd ? codeTd.innerText : block.innerText;
      navigator.clipboard.writeText(code).then(() => {
        button.textContent = "Copied!";
        setTimeout(() => (button.textContent = "Copy"), 2000);
      });
    });

    header.appendChild(label);
    header.appendChild(button);
    block.insertBefore(header, block.firstChild);
  });
});
