/**
 * script.js — Smart PDF Tools
 * Handles file selection, drag-and-drop, AJAX processing, and dynamic UI updates.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const dropZone = document.getElementById('dropZone');
  const fileInput = document.getElementById('fileInput');
  const browseBtn = document.getElementById('browseBtn');
  const clearBtn = document.getElementById('clearBtn');
  const fileList = document.getElementById('fileList');
  const fileListWrapper = document.getElementById('fileListWrapper');
  const processBtn = document.getElementById('processBtn');
  const resultBox = document.getElementById('resultBox');
  const downloadLinks = document.getElementById('downloadLinks');
  const loaderBox = document.getElementById('loaderBox');
  const splitMode = document.getElementById('splitMode');
  const rangeInputGroup = document.getElementById('rangeInputGroup');
  const secureAction = document.getElementById('secureAction');
  const passwordGroup = document.getElementById('passwordGroup');

  let queuedFiles = [];

  // --- Core Logic ---

  const updateUI = () => {
    if (queuedFiles.length > 0) {
      fileListWrapper.classList.remove('hidden');
      dropZone.classList.add('hidden');
      renderFileList();
    } else {
      fileListWrapper.classList.add('hidden');
      dropZone.classList.remove('hidden');
    }
  };

  const renderFileList = () => {
    fileList.innerHTML = '';
    queuedFiles.forEach((file, index) => {
      const ext = file.name.split('.').pop();
      const item = document.createElement('div');
      item.className = 'file-item';
      item.innerHTML = `
                <div class="file-info">
                    <span class="file-ext">${ext}</span>
                    <span class="file-name">${file.name}</span>
                </div>
                <div class="file-remove" onclick="window.removeFile(${index})">✕</div>
            `;
      fileList.appendChild(item);
    });
  };

  window.removeFile = (index) => {
    queuedFiles.splice(index, 1);
    updateUI();
  };

  const handleFiles = (files) => {
    const arr = Array.from(files);
    if (!TOOL_CONFIG.multiple) {
      queuedFiles = [arr[0]];
    } else {
      queuedFiles = [...queuedFiles, ...arr];
    }
    updateUI();
  };

  // --- Events ---

  if (dropZone) {
    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropZone.classList.add('dragover');
    });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropZone.classList.remove('dragover');
      handleFiles(e.dataTransfer.files);
    });
  }

  if (browseBtn) browseBtn.addEventListener('click', (e) => { e.stopPropagation(); fileInput.click(); });
  if (fileInput) fileInput.addEventListener('change', (e) => handleFiles(e.target.files));
  if (clearBtn) clearBtn.addEventListener('click', () => { queuedFiles = []; updateUI(); });

  // Tool-specific fields
  if (splitMode) {
    splitMode.addEventListener('change', (e) => {
      if (e.target.value === 'all') {
        rangeInputGroup.classList.add('hidden');
      } else {
        rangeInputGroup.classList.remove('hidden');
      }
    });
  }

  if (secureAction) {
    secureAction.addEventListener('change', (e) => {
      // Password group is always visible but labels might change
      // (Keeping it simple for now)
    });
  }

  // --- Processing ---

  if (processBtn) {
    processBtn.addEventListener('click', async () => {
      if (queuedFiles.length === 0) return showToast('Please select at least one file.', 'error');

      const formData = new FormData();
      queuedFiles.forEach(f => formData.append('files', f));

      // Tool-specific params
      if (TOOL_ID === 'split') {
        formData.append('split_mode', document.getElementById('splitMode').value);
        formData.append('page_range', document.getElementById('pageRange').value);
      }
      if (TOOL_ID === 'compress') {
        formData.append('comp_level', document.getElementById('compLevel').value);
      }
      if (TOOL_ID === 'pdf-to-image') {
        formData.append('image_format', document.getElementById('imageFormat').value);
      }
      if (TOOL_ID === 'secure') {
        formData.append('secure_action', document.getElementById('secureAction').value);
        formData.append('password', document.getElementById('pdfPassword').value);
        formData.append('unlock_password', document.getElementById('pdfPassword').value);
      }
      if (TOOL_ID === 'translate') {
        formData.append('target_lang', document.getElementById('targetLang').value);
      }

      const customName = document.getElementById('customFilename').value.trim();
      if (customName) {
        formData.append('custom_name', customName);
      }

      loaderBox.classList.remove('hidden');

      try {
        const response = await fetch(`/process/${TOOL_ID}`, {
          method: 'POST',
          body: formData
        });
        const data = await response.json();

        if (data.success) {
          showResult(data.downloads);
        } else {
          showToast(data.message || 'Processing failed.', 'error');
        }
      } catch (err) {
        showToast('A network error occurred.', 'error');
      } finally {
        loaderBox.classList.add('hidden');
      }
    });
  }

  const showResult = (downloads) => {
    fileListWrapper.classList.add('hidden');
    resultBox.classList.remove('hidden');
    downloadLinks.innerHTML = '';
    downloads.forEach(dl => {
      const btn = document.createElement('a');
      btn.className = 'btn btn-primary btn-lg';
      btn.href = `/download/${dl.name}`;
      btn.innerText = dl.label || 'Download File';
      btn.target = '_blank';
      downloadLinks.appendChild(btn);
    });
    showToast('Processing complete!', 'success');
  };

  // --- Toast Utility ---

  window.showToast = (msg, type = 'info') => {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = (type === 'success' ? '✅' : '❌') + ' ' + msg;
    container.appendChild(toast);
    const duration = (type === 'error' || type === 'info') ? 10000 : 3000;
    setTimeout(() => {
      toast.style.opacity = '0';
      setTimeout(() => toast.remove(), 300);
    }, duration);
  };
});
