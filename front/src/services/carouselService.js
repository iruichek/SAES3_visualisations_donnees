// Service local pour le S3 (sans appel API réseau)
export const getCarouselItems = () => {
  return [
    {
      id: 1,
      src: '/carousel/graph1_bar.png',
      alt: 'Régularité des TER par région',
      title: 'Régularité par Région'
    },
    {
      id: 2,
      src: '/carousel/graph2_line.png',
      alt: 'Évolution ponctualité et précipitations',
      title: 'Ponctualité vs Météo'
    },
    {
      id: 3,
      src: '/carousel/graph3_scatter.png',
      alt: 'Impact des intempéries sur les retards',
      title: 'Impact des intempéries'
    }
  ]
}