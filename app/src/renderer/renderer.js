let inputFile = null;

const $ = (id) => document.getElementById(id);

$('btnPick').addEventListener('click', async () => {
  inputFile = await window.api.selectInputFile();
  $('pickedFile').textContent = inputFile || '';
});

$('btnStart').addEventListener('click', async () => {
  $('status').textContent = 'Running...';
  $('log').textContent = '';

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
  $('log').textContent += text;
  $('log').scrollTop = $('log').scrollHeight;
});

window.api.onBackendExit((code) => {
  $('status').textContent = code === 0 ? 'Done' : `Exited with code ${code}`;
});
