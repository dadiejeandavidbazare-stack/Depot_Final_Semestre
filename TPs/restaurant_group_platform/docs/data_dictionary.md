# Dictionnaire des Données (Data Dictionary)

## Flux : `kitchen.orders.v1` (Commandes)
| Champ | Type | Description | Contrainte / Règle Métier |
| :--- | :--- | :--- | :--- |
| `order_id` | String | Identifiant unique de la commande | Doit respecter le pattern `ORD-YYYY-XXXXX` |
| `restaurant_id` | String | ID unique du restaurant émetteur | Clé de jointure référentiel |
| `order_type` | String | Canal de vente | Valeurs : `salle`, `emporter`, `delivery` |
| `status` | String | État d'avancement de la commande | Valeurs : `recue`, `en_preparation`, `prete`, `payee`, etc. |
| `amount` | Float | Montant total de la commande | Strictement supérieur à 0.00 |
| `items_count` | Integer | Nombre d'articles inclus | Supérieur ou égal à 1 |
| `event_ts` | String | Timestamp de l'événement | Format ISO 8601 UTC obligatoire |

## Flux : `payment.events.v1` (Paiements)
| Champ | Type | Description | Contrainte / Règle Métier |
| :--- | :--- | :--- | :--- |
| `payment_id` | String | Identifiant unique de transaction | Clé primaire financière |
| `order_id` | String | ID de la commande associée | Doit correspondre à un `order_id` existant |
| `payment_method` | String | Moyen de paiement | Valeurs : `especes`, `carte`, `application` |
| `amount` | Float | Montant encaissé | Doit être strictement positif |
| `payment_ts` | String | Horodatage de validation | Format ISO 8601 UTC |