const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const HTML = path.join(__dirname, 'html');
const OUT = path.join(__dirname, '..', 'pdf');

(async () => {
  fs.mkdirSync(OUT, { recursive: true });

  const browser = await puppeteer.launch({
    executablePath: CHROME,
    headless: true,
    args: ['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage'],
  });

  const files = fs.readdirSync(HTML).filter(f => f.endsWith('.html')).sort();
  // sections first, combined report last
  files.sort((a, b) => (a.startsWith('_') ? 1 : 0) - (b.startsWith('_') ? 1 : 0) || a.localeCompare(b));

  const page = await browser.newPage();
  for (const f of files) {
    const src = 'file://' + path.join(HTML, f);
    const dst = path.join(OUT, f.replace(/\.html$/, '.pdf'));
    await page.goto(src, { waitUntil: 'load', timeout: 60000 });
    await page.pdf({
      path: dst,
      format: 'A4',
      printBackground: true,
      preferCSSPageSize: true,
      displayHeaderFooter: true,
      headerTemplate: '<span></span>',
      footerTemplate:
        '<div style="width:100%;font-size:8pt;color:#6b7680;font-family:Helvetica,Arial;' +
        'padding:0 18mm;display:flex;justify-content:space-between;">' +
        '<span>Behavioural Economics Based AI Risk Assessment</span>' +
        '<span class="pageNumber"></span></div>',
      margin: { top: '20mm', bottom: '18mm', left: '18mm', right: '18mm' },
    });
    const kb = (fs.statSync(dst).size / 1024).toFixed(0);
    console.log(`${f.replace(/\.html$/, '.pdf').padEnd(34)} ${kb} KB`);
  }

  await browser.close();
  console.log('\ndone: ' + files.length + ' PDFs');
})().catch(e => { console.error('FAILED:', e.message); process.exit(1); });
