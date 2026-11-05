import os
import matplotlib.pyplot as plt

# Dossiers de sortie
FRONT_DIR = os.path.join(os.path.dirname(__file__), '../front/public/carousel')
API_DIR = os.path.join(os.path.dirname(__file__), '../api/public/carousel')

os.makedirs(FRONT_DIR, exist_ok=True)
os.makedirs(API_DIR, exist_ok=True)

def save_graph(fig, filename):
    fig.savefig(os.path.join(FRONT_DIR, filename), dpi=300, bbox_inches='tight')
    fig.savefig(os.path.join(API_DIR, filename), dpi=300, bbox_inches='tight')
    plt.close(fig)

# 1. Bar Chart : Régularité par région
# Style du graphique 1
fig1, ax1 = plt.subplots(figsize=(7, 3.5))

# Fond transparent ou accordé
fig1.patch.set_facecolor('none')
ax1.set_facecolor('none')

# Barres avec une couleur bleue plus douce
ax1.bar(['Bretagne', 'PACA', 'Occitanie', 'Grand Est'], [94, 85, 88, 91], color='#0284c7', width=0.5)

# Nettoyage des bordures du graphique (enlever le cadre noir)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.spines['left'].set_color('#64748b')
ax1.spines['bottom'].set_color('#64748b')

ax1.tick_params(colors='#1e293b')
ax1.set_title('Régularité moyenne par région (%)', fontsize=12, color='#1e293b', fontweight='bold', pad=15)

plt.tight_layout()
save_graph(fig1, 'graph1_bar.png')

# 2. Courbe : Ponctualité vs Précipitations
fig2, ax2 = plt.subplots(figsize=(8, 4))
ax2.plot(['Jan', 'Fév', 'Mar', 'Avr', 'Mai'], [85, 87, 92, 94, 91], color='#0284c7', marker='o')
ax2.set_title('Évolution de la ponctualité')
save_graph(fig2, 'graph2_line.png')

# 3. Scatter Plot : Météo vs Retards
fig3, ax3 = plt.subplots(figsize=(8, 4))
ax3.scatter([2, 5, 8, 12, 15], [100, 250, 400, 600, 850], color='#818cf8')
ax3.set_title('Jours d\'intempéries vs Cumul des retards (min)')
save_graph(fig3, 'graph3_scatter.png')

print("Graphiques du carrousel générés avec succès !")