const express = require('express');
const app = express();
let fired = false;

// ---------------- HTTP API ----------------
app.get('/fire',  (_,res)=>{ fired = true;  console.log('[FIRE]');  res.send('ok'); });
app.get('/reset', (_,res)=>{ fired = false; console.log('[RESET]'); res.send('reset');});
app.get('/status',(_,res)=>{ res.send(fired ? 'FIRE' : 'WAIT'); });

app.listen(56830, ()=>console.log('Listening on http://localhost:56830'));

// -------------- Console trigger -----------
const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin, output: process.stdout });

console.log('Press ENTER to fire, type r + ENTER to reset, q + ENTER to quit.');
rl.setPrompt('> ');
rl.prompt();

rl.on('line', line => {
  const cmd = line.trim().toLowerCase();
  if (cmd === '') {                 // just ENTER → fire
    fired = true;
    console.log('[FIRE]');
  } else if (cmd === 'r' || cmd === 'reset') {
    fired = false;
    console.log('[RESET]');
  } else if (cmd === 'q' || cmd === 'quit') {
    console.log('bye!');
    process.exit(0);
  } else {
    console.log('ENTER = fire, r = reset, q = quit');
  }
  rl.prompt();
});
