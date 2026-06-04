let inputFile = null;
const progressRe = /PROGRESS\s+(\d+)\/(\d+)/;

const $ = (id) => document.getElementById(id);

$('btnPick').addEventListener('click', async () => {
  inputFile = await window.api.selectInputFile();
  $('pickedFile').textContent = inputFile || '';
});

$('btnStart').addEventListener('click', async () => {
  $('status').textContent = 'Running...';
  $('log').textContent = '';
  $('progressBar').value = 0;
  $('progressBar').max = 1;
  $('progressText').textContent = '';

  const job = {
    inputFile,
    pastedText: $('pasted').value?.trim() || null,
    outputRoot: $('outputRoot').value?.trim() || 'D:\\Papers',
    proxy: $('proxy').value?.trim() || null,
    resume: $('resume').checked,
  };

  await window.api.startBackendJob(job);
});

window.api.onBackendLog((text) => {
  const match = text.match(progressRe);
  if (match) {
    const current = Number(match[1]);
    const total = Number(match[2]);
    if (Number.isFinite(current) && Number.isFinite(total) && total > 0) {
      $('progressBar').max = total;
      $('progressBar').value = current;
      $('progressText').textContent = `${current}/${total}`;
    }
    return;
  }
  $('log').textContent += text;
  $('log').scrollTop = $('log').scrollHeight;
});

window.api.onBackendExit((code) => {
  $('status').textContent = code === 0 ? 'Done' : `Exited with code ${code}`;
});
