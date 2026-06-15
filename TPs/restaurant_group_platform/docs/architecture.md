# Dossier d'Architecture Technique — RestaurantGroup SA

## 1. Schéma des Acteurs et Flux
* **Clients (App Mobile)** : Émettent les commandes (Livraison / À emporter).
* **Équipes Resto (POS / KDS)** : Gèrent la préparation et les statuts des commandes.
* **Passerelles de Paiement** : Notifient le système des validations financières via Webhooks.
* **Direction & Ops** : Consomment les rapports consolidés en zone Gold.

## 2. Architecture des Données (Medallion)
* **Bronze** : Stockage immuable des payloads bruts JSON reçus de Kafka, partitionné par date (`year=YYYY/month=MM/day=DD/`).
* **Silver** : Données nettoyées, dédoublonnées et enrichies avec le référentiel des restaurants (ajout de la ville).
* **Gold** : Tables d'agrégation prêtes pour la BI (calcul du Chiffre d'Affaires quotidien par restaurant).

## 3. Règles de Validation (Gestion des Pannes)
* **Contrats stricts** : Tout payload ne respectant pas les schémas ou ayant un montant négatif est immédiatement rejeté.
* **Dead Letter Queue (DLQ)** : Les messages invalides sont routés vers le topic `orders.rejected.dlq` pour analyse DataOps sans bloquer le pipeline.
* **Watermarking** : Un retard maximal de 15 minutes est toléré pour les données tardives en streaming.