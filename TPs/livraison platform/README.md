Ce projet simule une architecture distribuée de gestion de commandes logistiques inspirée des systèmes modernes de type Kafka.

Il permet de traiter des commandes en temps réel, de générer des événements métier, de les distribuer via un broker partitionné et de les analyser via des consumers et un dashboard.

 Architecture globale
Service (sync)
     ↓
Event Producer
     ↓
Mini Broker (partitionné)
     ↓
Consumers (A & B)
     ↓
Storage + Dashboard + Offsets


 Structure du projet
livraison_platform/
├── contracts/        # Contrats de données (Order, OrderEvent)
├── service/          # API synchrone de création de commandes
├── broker/           # Broker simulé partitionné
├── producers/        # Génération des événements métier
├── consumers/        # Consumers A et B (traitement parallèle)
├── storage/          # Stockage partitionné sur disque
├── dashboard/        # Dashboard temps réel
├── offsets/          # Gestion reprise après crash
├── data/             # Données partitionnées (runtime)
├── main.py           # Simulation globale
└── README.md

 Fonctionnalités principales
 1. Service synchrone
Création de commandes
Validation des données
Retour immédiat avec order_id
 2. Event Producer
Génère le cycle de vie complet d’une commande :
created → confirmed → prepared → dispatched → delivered
 3. Broker partitionné
Simulation d’un système type Kafka
Partitionnement par ville
Stockage en mémoire
 4. Consumers parallèles
Consumer A :
analyse par ville
analyse par statut
Consumer B :
analyse par livreur
taux de succès / échec
 5. Dashboard temps réel
Nombre de commandes
Taux de succès
Activité par ville
Activité par livreur
 6. Stockage partitionné
Format JSONL
Dossiers par ville :
data/city=Fes/events.jsonl
 7. Offsets & reprise
Sauvegarde des offsets dans JSON
Reprise après crash (at-least-once)
 Lancer le projet
1. Installer Python (>=3.10)
2. Lancer la simulation
python main.py

Scénarios de test

Scénario normal
création de commandes valides
cycle complet des événements
dashboard cohérent

 Scénario erreur
ville invalide
montant négatif
champ manquant

 Scénario crash
arrêt des consumers
redémarrage
reprise via offsets

 Concepts utilisés
Architecture event-driven
Partitionnement des données
Multithreading Python
Sérialisation JSON
Gestion d’offsets
Stockage distribué simulé
Observabilité temps réel

 Exemple d’événement
{
  "event_id": "EVT-1001",
  "event_type": "order_created",
  "timestamp": "2026-05-12T10:30:00",
  "partition_key": "Fes",
  "order": {
    "order_id": "ORD-001",
    "customer_id": "CUST-101",
    "city": "Fes",
    "zone": "Saiss",
    "courier_id": "CRR-07",
    "amount": 245.0,
    "items_count": 2,
    "status": "created"
  }
}

Limites du système
broker non distribué réel (simulation Python)
pas de base de données réelle
scalabilité limitée à une machine
pas de garantie exactly-once

 Améliorations possibles
migration vers Apache Kafka
base de données (PostgreSQL / Redis)
API REST (FastAPI)
monitoring (Prometheus / Grafana)
containerisation (Docker)

 Auteur

Projet académique — Simulation d’une architecture distribuée de livraison.

 Conclusion

Ce projet démontre la compréhension des systèmes distribués modernes :

découplage des composants
traitement asynchrone
tolérance aux pannes
observabilité temps réel
partitionnement des données