import { getCarouselItems } from './carouselService.js'

const contentKey = 'nuage-sur-les-rails:home'

const defaultDescription =
  'NuageSurLesRails est une plateforme web destinée à explorer et analyser les impacts ' +
  'des conditions météorologiques sur la ponctualité des TER en France. ' +
  'Le site croise les données de régularité du réseau ferroviaire avec les relevés ' +
  'climatiques régionaux pour visualiser l’influence du temps sur le trafic.'

export function getHomeContent() {
  const saved = JSON.parse(localStorage.getItem(contentKey) ?? 'null')

  return {
    description: saved?.description ?? defaultDescription,
    carouselItems: getCarouselItems().map((item, index) => ({
      ...item,
      src: saved?.carouselUrls?.[index] ?? item.src,
    })),
  }
}

export function saveHomeContent(description, carouselUrls) {
  const urls = carouselUrls.map((url) => url.trim())

  if (!description.trim() || urls.some((url) => !url)) {
    throw new Error('Renseigne le texte et les trois URL.')
  }

  for (const value of urls) {
    const url = new URL(value, window.location.origin)

    if (!['http:', 'https:'].includes(url.protocol)) {
      throw new Error('Utilise une URL HTTP(S) ou un chemin vers une image du site.')
    }
  }

  localStorage.setItem(contentKey, JSON.stringify({
    description: description.trim(),
    carouselUrls: urls,
  }))
}