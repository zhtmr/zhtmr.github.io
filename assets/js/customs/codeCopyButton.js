// // codeCopyButton.js
// import ClipboardJS from "clipboard";
//
// let pre = document.querySelectorAll('pre');
//
// pre.forEach((snippet) => {
//   let button = document.createElement('button');
//   button.className = 'copy-btn';
//   // button.innerText = 'Copy'; // Text 버튼을 이미지로 변경
//
//   // (option) 마우스를 Code 블록에 올리면 버튼이 나타나도록 함
//   button.addEventListener('mouseleave', clearTooltip);
//   button.addEventListener('blur', clearTooltip);
//
//   // (option) Text 버튼 -> 이미지 버튼
//   let img = document.createElement('img');
//   img.className = "clippy";
//   img.setAttribute('width', '15');
//   img.setAttribute('src', 'https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FbocTTu%2FbtrrQrXMCOg%2FaMErQkgcDCRJJHHIg4O4Wk%2Fimg.png');
//   img.setAttribute('alt', 'Copy to clipboard');
//   button.appendChild(img);
//
//   snippet.appendChild(button)
// });
//
// let copyCode = new ClipboardJS('.copy-btn', {
//   target: function(trigger) {
//     return trigger.previousElementSibling;
//   }
// });
//
// copyCode.on('success', function(event) {
//   event.clearSelection();
//   showTooltip(event.trigger, '복사완료');
//   // showToast("코드 복사 완료!");
// });
//
// copyCode.on('error', function(event) {
//   showTooltip(event.trigger, fallbackMessage(event.action));
// });
//
//
// function clearTooltip(event) {
//   event.currentTarget.setAttribute('class', 'copy-btn');
//   event.currentTarget.removeAttribute('aria-label');
// }
//
// function showTooltip(elem, msg) {
//   elem.setAttribute('class', 'copy-btn tooltipped tooltipped-s');
//   elem.setAttribute('aria-label', msg);
// }
//
// function fallbackMessage(action) {
//   let actionMsg = '';
//   let actionKey = (action === 'cut' ? 'X' : 'C');
//   if (/iPhone|iPad/i.test(navigator.userAgent)) {
//     actionMsg = 'No support :(';
//   } else if (/Mac/i.test(navigator.userAgent)) {
//     actionMsg = 'Press ⌘-' + actionKey + ' to ' + action;
//   } else {
//     actionMsg = 'Press Ctrl-' + actionKey + ' to ' + action;
//   }
//   return actionMsg;
// }