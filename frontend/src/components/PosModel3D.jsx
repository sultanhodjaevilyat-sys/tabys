import { useEffect, useRef } from 'react'
import * as THREE from 'three'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js'

/*
 * 3D-модель рабочего места кассира Tabys (three.js):
 *  моноблок с экраном Tabys, принтер чеков, платёжный терминал и денежный ящик.
 *  Модель сама медленно вращается; мышкой/пальцем можно крутить и приближать.
 */

const GREEN = '#1E6B52'
const GOLD = '#E0A526'

// Рисуем «интерфейс Tabys» на canvas и используем как текстуру экрана
function makeScreenTexture() {
  const c = document.createElement('canvas')
  c.width = 1024
  c.height = 640
  const g = c.getContext('2d')
  g.fillStyle = '#0f2e25'
  g.fillRect(0, 0, 1024, 640)
  g.fillStyle = GREEN
  g.fillRect(0, 0, 1024, 80)
  g.fillStyle = GOLD
  g.font = 'bold 44px Arial'
  g.fillText('Tabys', 32, 56)
  g.fillStyle = '#fff'
  g.font = '26px Arial'
  g.fillText('Панель владельца', 200, 52)
  const cards = [['Выручка', '4 240 800 ₸'], ['Средний чек', '4 249 ₸'], ['Food cost', '25,1 %']]
  cards.forEach(([t, v], i) => {
    const x = 32 + i * 330
    g.fillStyle = '#17463a'
    g.fillRect(x, 110, 300, 130)
    g.fillStyle = '#9fc9b9'
    g.font = '24px Arial'
    g.fillText(t, x + 20, 150)
    g.fillStyle = '#fff'
    g.font = 'bold 40px Arial'
    g.fillText(v, x + 20, 210)
  })
  // график выручки по дням
  const bars = [54, 69, 82, 69, 47, 49, 54]
  bars.forEach((h, i) => {
    g.fillStyle = i === 2 ? GOLD : '#3fa07f'
    g.fillRect(48 + i * 70, 590 - h * 3.6, 46, h * 3.6)
  })
  // карточка аудитора потерь
  g.fillStyle = '#4a1f1f'
  g.fillRect(560, 280, 430, 310)
  g.fillStyle = '#ffb4a8'
  g.font = 'bold 30px Arial'
  g.fillText('⚠ Аудитор потерь', 585, 330)
  g.fillStyle = '#fff'
  g.font = '26px Arial'
  ;['Говядина: +26,5 кг', '≈ 106 200 ₸ за 4 недели', 'Вт и Чт, вечер', '', 'Удаления после пречека:', 'в 4 раза чаще нормы'].forEach((l, i) =>
    g.fillText(l, 585, 380 + i * 36),
  )
  const tex = new THREE.CanvasTexture(c)
  tex.colorSpace = THREE.SRGBColorSpace
  tex.anisotropy = 8
  return tex
}

function makeTerminalTexture() {
  const c = document.createElement('canvas')
  c.width = 256
  c.height = 320
  const g = c.getContext('2d')
  g.fillStyle = '#e9f7f1'
  g.fillRect(0, 0, 256, 320)
  g.fillStyle = GREEN
  g.beginPath()
  g.arc(128, 120, 60, 0, Math.PI * 2)
  g.fill()
  g.strokeStyle = '#fff'
  g.lineWidth = 14
  g.beginPath()
  g.moveTo(98, 122)
  g.lineTo(120, 146)
  g.lineTo(162, 98)
  g.stroke()
  g.fillStyle = '#0f2e25'
  g.font = 'bold 30px Arial'
  g.textAlign = 'center'
  g.fillText('Оплачено', 128, 230)
  g.font = '24px Arial'
  g.fillText('+ чаевые 10 %', 128, 270)
  const tex = new THREE.CanvasTexture(c)
  tex.colorSpace = THREE.SRGBColorSpace
  return tex
}

function buildModel() {
  const root = new THREE.Group()
  const dark = new THREE.MeshStandardMaterial({ color: '#22262b', roughness: 0.45, metalness: 0.3 })
  const body = new THREE.MeshStandardMaterial({ color: '#2d3238', roughness: 0.35, metalness: 0.4 })
  const white = new THREE.MeshStandardMaterial({ color: '#f1f2ef', roughness: 0.6 })
  const green = new THREE.MeshStandardMaterial({ color: GREEN, roughness: 0.5 })
  const gold = new THREE.MeshStandardMaterial({ color: GOLD, roughness: 0.3, metalness: 0.6 })

  // стойка (столешница)
  const counter = new THREE.Mesh(new THREE.CylinderGeometry(3.2, 3.2, 0.18, 64), new THREE.MeshStandardMaterial({ color: '#c9b79c', roughness: 0.8 }))
  counter.position.y = -0.09
  counter.receiveShadow = true
  root.add(counter)
  const rim = new THREE.Mesh(new THREE.TorusGeometry(3.2, 0.04, 12, 96), gold)
  rim.rotation.x = Math.PI / 2
  root.add(rim)

  // денежный ящик
  const drawer = new THREE.Mesh(new RoundedBoxGeometry(2.4, 0.45, 1.7, 4, 0.06), dark)
  drawer.position.set(0, 0.225, 0.1)
  drawer.castShadow = true
  root.add(drawer)
  const handle = new THREE.Mesh(new RoundedBoxGeometry(0.8, 0.06, 0.06, 2, 0.02), gold)
  handle.position.set(0, 0.25, 0.97)
  root.add(handle)

  // моноблок: подставка, ножка, корпус, экран
  const base = new THREE.Mesh(new THREE.CylinderGeometry(0.45, 0.55, 0.08, 40), body)
  base.position.set(0, 0.49, -0.1)
  root.add(base)
  const neck = new THREE.Mesh(new RoundedBoxGeometry(0.22, 0.9, 0.14, 3, 0.05), body)
  neck.position.set(0, 0.95, -0.2)
  neck.rotation.x = -0.18
  root.add(neck)
  const monitor = new THREE.Group()
  monitor.position.set(0, 1.55, -0.12)
  monitor.rotation.x = -0.22
  const shell = new THREE.Mesh(new RoundedBoxGeometry(2.0, 1.3, 0.12, 4, 0.05), body)
  shell.castShadow = true
  monitor.add(shell)
  const screen = new THREE.Mesh(new THREE.PlaneGeometry(1.86, 1.16), new THREE.MeshBasicMaterial({ map: makeScreenTexture() }))
  screen.position.z = 0.061
  monitor.add(screen)
  const logo = new THREE.Mesh(new THREE.CircleGeometry(0.18, 32), green)
  logo.position.z = -0.061
  logo.rotation.y = Math.PI
  monitor.add(logo)
  root.add(monitor)

  // принтер чеков с бумажной лентой
  const printer = new THREE.Group()
  printer.position.set(1.65, 0, 0.35)
  printer.rotation.y = -0.5
  const pBody = new THREE.Mesh(new RoundedBoxGeometry(0.75, 0.55, 0.9, 4, 0.08), white)
  pBody.position.y = 0.275
  pBody.castShadow = true
  printer.add(pBody)
  const pLid = new THREE.Mesh(new RoundedBoxGeometry(0.72, 0.06, 0.5, 2, 0.03), dark)
  pLid.position.set(0, 0.56, -0.15)
  printer.add(pLid)
  const paper = new THREE.Mesh(new THREE.PlaneGeometry(0.5, 0.6), new THREE.MeshStandardMaterial({ color: '#ffffff', side: THREE.DoubleSide, roughness: 0.9 }))
  paper.geometry.translate(0, 0.3, 0)
  paper.position.set(0, 0.58, 0.12)
  paper.rotation.x = -0.35
  printer.add(paper)
  const led = new THREE.Mesh(new THREE.SphereGeometry(0.03, 16, 16), new THREE.MeshBasicMaterial({ color: '#39e07a' }))
  led.position.set(0.25, 0.4, 0.452)
  printer.add(led)
  root.add(printer)

  // платёжный терминал (QR / карта)
  const term = new THREE.Group()
  term.position.set(-1.65, 0, 0.45)
  term.rotation.y = 0.55
  const tBase = new THREE.Mesh(new THREE.CylinderGeometry(0.32, 0.38, 0.1, 32), dark)
  tBase.position.y = 0.05
  term.add(tBase)
  const tBody = new THREE.Mesh(new RoundedBoxGeometry(0.5, 0.85, 0.12, 4, 0.05), dark)
  tBody.position.set(0, 0.55, 0)
  tBody.rotation.x = -0.35
  tBody.castShadow = true
  const tScreen = new THREE.Mesh(new THREE.PlaneGeometry(0.42, 0.52), new THREE.MeshBasicMaterial({ map: makeTerminalTexture() }))
  tScreen.position.set(0, 0.1, 0.061)
  tBody.add(tScreen)
  const keys = new THREE.Mesh(new THREE.PlaneGeometry(0.4, 0.16), green)
  keys.position.set(0, -0.28, 0.061)
  tBody.add(keys)
  term.add(tBody)
  root.add(term)

  // монеты «табыс» — прибыль, которую сохраняет система
  const coins = []
  for (let i = 0; i < 5; i++) {
    const coin = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.16, 0.04, 32), gold)
    coin.position.set(0.9 + (i % 2) * 0.05, 0.47 + i * 0.045, 0.55)
    root.add(coin)
    coins.push(coin)
  }

  return { root, paper, led, coins }
}

export default function PosModel3D({ height = 420 }) {
  const mountRef = useRef(null)

  useEffect(() => {
    const mount = mountRef.current
    const scene = new THREE.Scene()
    const camera = new THREE.PerspectiveCamera(40, mount.clientWidth / height, 0.1, 100)
    camera.position.set(4.2, 3.2, 5.4)

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    renderer.setSize(mount.clientWidth, height)
    renderer.shadowMap.enabled = true
    renderer.outputColorSpace = THREE.SRGBColorSpace
    mount.appendChild(renderer.domElement)

    scene.add(new THREE.HemisphereLight('#ffffff', '#3b4a44', 1.3))
    const sun = new THREE.DirectionalLight('#ffffff', 2.2)
    sun.position.set(4, 7, 5)
    sun.castShadow = true
    sun.shadow.mapSize.set(1024, 1024)
    scene.add(sun)
    const rimLight = new THREE.PointLight(GOLD, 8, 12)
    rimLight.position.set(-4, 3, -3)
    scene.add(rimLight)

    const { root, paper, led, coins } = buildModel()
    root.position.y = -0.6
    scene.add(root)

    const controls = new OrbitControls(camera, renderer.domElement)
    controls.enableDamping = true
    controls.autoRotate = true
    controls.autoRotateSpeed = 1.4
    controls.minDistance = 3.5
    controls.maxDistance = 11
    controls.maxPolarAngle = Math.PI / 2.05
    controls.target.set(0, 0.5, 0)
    controls.enablePan = false

    const clock = new THREE.Clock()
    let frame
    const animate = () => {
      const t = clock.getElapsedTime()
      paper.scale.y = 0.55 + 0.45 * ((t * 0.35) % 1) // чек «печатается»
      led.material.color.set(Math.sin(t * 4) > 0 ? '#39e07a' : '#145c33')
      coins.forEach((c, i) => (c.position.y = 0.47 + i * 0.045 + Math.sin(t * 2 + i) * 0.01))
      controls.update()
      renderer.render(scene, camera)
      frame = requestAnimationFrame(animate)
    }
    animate()

    const onResize = () => {
      camera.aspect = mount.clientWidth / height
      camera.updateProjectionMatrix()
      renderer.setSize(mount.clientWidth, height)
    }
    const ro = new ResizeObserver(onResize)
    ro.observe(mount)

    return () => {
      cancelAnimationFrame(frame)
      ro.disconnect()
      controls.dispose()
      scene.traverse((o) => {
        if (o.geometry) o.geometry.dispose()
        if (o.material) {
          if (o.material.map) o.material.map.dispose()
          o.material.dispose()
        }
      })
      renderer.dispose()
      mount.removeChild(renderer.domElement)
    }
  }, [height])

  return <div ref={mountRef} className="model3d" style={{ height }} aria-label="3D-модель кассы Tabys" />
}
