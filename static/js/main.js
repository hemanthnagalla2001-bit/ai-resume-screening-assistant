// Drop-zone drag & drop handling
(function () {
  const dropZone = document.getElementById('drop-zone');
  const fileInput = document.getElementById('resumes');
  const fileList  = document.getElementById('file-list');

  if (!dropZone || !fileInput) return;

  dropZone.addEventListener('dragover', function (e) {
    e.preventDefault();
    dropZone.classList.add('dragover');
  });

  dropZone.addEventListener('dragleave', function () {
    dropZone.classList.remove('dragover');
  });

  dropZone.addEventListener('drop', function (e) {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    fileInput.files = e.dataTransfer.files;
    renderFileList(fileInput.files);
  });

  fileInput.addEventListener('change', function () {
    renderFileList(fileInput.files);
  });

  function renderFileList(files) {
    if (!fileList) return;
    fileList.innerHTML = '';
    const icons = { pdf: '📄', docx: '📝', doc: '📝', txt: '📃' };
    Array.from(files).forEach(function (file) {
      const ext = file.name.split('.').pop().toLowerCase();
      const icon = icons[ext] || '📁';
      const size = file.size > 1048576
        ? (file.size / 1048576).toFixed(1) + ' MB'
        : (file.size / 1024).toFixed(0) + ' KB';
      const item = document.createElement('div');
      item.className = 'file-item';
      item.innerHTML =
        '<span class="file-item-icon">' + icon + '</span>' +
        '<span>' + file.name + '</span>' +
        '<span style="margin-left:auto;color:var(--gray-400);font-size:0.8rem;">' + size + '</span>';
      fileList.appendChild(item);
    });
  }
})();

// Word count for job description textarea
(function () {
  const textarea  = document.getElementById('job_description');
  const wordCount = document.getElementById('jd-word-count');

  if (!textarea || !wordCount) return;

  function update() {
    const words = textarea.value.trim().split(/\s+/).filter(Boolean).length;
    wordCount.textContent = words + ' word' + (words !== 1 ? 's' : '');
  }

  textarea.addEventListener('input', update);
  update();
})();

// Submit button loading state
(function () {
  const form       = document.getElementById('upload-form');
  const submitText = document.getElementById('submit-text');
  const submitLoad = document.getElementById('submit-loading');
  const submitBtn  = document.getElementById('submit-btn');

  if (!form) return;

  form.addEventListener('submit', function () {
    if (submitText) submitText.style.display = 'none';
    if (submitLoad) submitLoad.style.display = 'inline';
    if (submitBtn)  submitBtn.disabled = true;
  });
})();

// Auto-dismiss flash messages after 5 seconds
(function () {
  var flashes = document.querySelectorAll('.flash');
  flashes.forEach(function (el) {
    setTimeout(function () {
      el.style.transition = 'opacity 0.4s';
      el.style.opacity = '0';
      setTimeout(function () { el.remove(); }, 400);
    }, 5000);
  });
})();
