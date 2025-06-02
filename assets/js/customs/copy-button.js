document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("div.highlighter-rouge").forEach((block) => {
    const button = document.createElement("button");
    button.innerText = "Copy";
    button.className = "copy-btn";

    // 스타일 지정 (필요 시 조절)
    Object.assign(button.style, {
      position: "absolute",
      top: "8px",
      right: "8px",
      padding: "5px 10px",
      background: "#4CAF50",
      color: "#fff",
      border: "none",
      borderRadius: "4px",
      cursor: "pointer",
      fontSize: "12px",
      zIndex: "10"
    });

    // 복사 로직
    button.addEventListener("click", () => {
      const codeTd = block.querySelector("td.rouge-code");
      if (!codeTd) return;

      const code = codeTd.innerText;
      navigator.clipboard.writeText(code).then(() => {
        button.innerText = "Copied!";
        setTimeout(() => (button.innerText = "Copy"), 2000);
      });
    });

    // 버튼 삽입
    block.style.position = "relative";
    block.appendChild(button);
  });
});