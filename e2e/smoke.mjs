// E2E smoke-тест: открывает все страницы сайта в настоящем браузере (Chromium)
// и падает, если на странице ошибка JavaScript или не появился нужный контент.
// Запуск (бэкенд на :8000 и фронтенд на :5173 уже запущены):
//   npm install --no-save playwright && npx playwright install chromium && node e2e/smoke.mjs
import { chromium } from 'playwright'
import { mkdirSync } from 'node:fs'

const BASE = process.env.BASE_URL || 'http://localhost:5173'
const OUT = 'e2e/screenshots'
mkdirSync(OUT, { recursive: true })

const browser = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] })
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
const errors = []
page.on('pageerror', (e) => errors.push(`pageerror: ${e.message}`))
page.on('console', (m) => { if (m.type() === 'error') errors.push(`console: ${m.text()}`) })

const results = []
async function check(name, path, expectText, extra) {
  const before = errors.length
  try {
    await page.goto(BASE + path, { waitUntil: 'networkidle' })
    await page.getByText(expectText, { exact: false }).first().waitFor({ timeout: 15000 })
    if (extra) await extra()
  } catch (e) {
    errors.push(`${name}: ${e.message.split('\n')[0]}`)
  }
  await page.screenshot({ path: `${OUT}/${name}.png`, fullPage: true })
  const ok = errors.length === before
  results.push({ name, path, ok })
  console.log(`${ok ? '✔' : '✘'} ${name.padEnd(12)} ${path}`)
}

await check('home', '/', 'находит, где теряются деньги', async () => {
  const canvas = page.locator('.model3d canvas')
  await canvas.waitFor({ timeout: 10000 })
  const box = await canvas.boundingBox()
  if (!box || box.width < 200) throw new Error('3D canvas не отрисовался')
  await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2)
  await page.mouse.down(); await page.mouse.move(box.x + box.width / 2 + 120, box.y + box.height / 2); await page.mouse.up()
  console.log(`  3D canvas ${Math.round(box.width)}×${Math.round(box.height)} — вращение мышкой ок`)
})
await check('dashboard', '/dashboard', 'Выручка за 7 дней')
await check('menu', '/menu', 'Бешбармак', async () => {
  await page.getByText('Бешбармак').click()
  await page.getByText('Говядина').first().waitFor()
  console.log('  техкарта открывается по клику')
})
await check('warehouse', '/warehouse', 'Заказ поставщикам')
await check('audit', '/audit', 'перерасход', async () => {
  await page.getByText('Ерлан').first().waitFor()
  console.log('  аудитор нашёл говядину и кассира')
})
await check('insights', '/insights', 'Матрица меню')
await check('assistant', '/assistant', 'AI-ассистент владельца', async () => {
  const answers = page.locator('.msg.model .bubble')
  await page.getByRole('button', { name: 'Где я теряю деньги?' }).click()
  await page.waitForFunction(() => document.querySelectorAll('.msg.model .bubble:not(.typing)').length >= 2, null, { timeout: 30000 })
  const answer = await answers.last().innerText()
  console.log('  ответ агента: ' + answer.replace(/\n/g, ' | ').slice(0, 300))
  if (!answer.includes('Говядина')) throw new Error('в ответе агента нет «Говядина»')
})
await check('pricing', '/pricing', 'Tabys Бизнес', async () => {
  await page.locator('.plan', { hasText: 'Tabys Бизнес' }).getByRole('button').click()
  await page.getByText('Подписка активна').waitFor({ timeout: 15000 })
  console.log('  оплата (демо) → подписка активна')
})
await check('notfound', '/no-such-page', '404')

await browser.close()
if (errors.length) {
  console.error('\nОшибки в браузере:\n' + errors.join('\n'))
  process.exit(1)
}
console.log(`\nВсе ${results.length} страниц открылись без ошибок.`)
